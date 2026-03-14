import cv2
import time
import serial
import speech_recognition as sr

# --- CONFIGURATION ---
ESP_PORT = 'COM8' 
BAUD_RATE = 115200
WAKE_WORDS = ["hey lumi", "hello lumi", "lumi", "hello", "hi"]

# --- CONNECT TO ESP32 ---
try:
    esp32 = serial.Serial(ESP_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print(f"✅ Connected to Lamp on {ESP_PORT}")
except Exception as e:
    print(f"❌ Connection Failed: {e}")
    esp32 = None

recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Load Cascades
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_smile.xml")

def send_to_esp(command):
    if esp32:
        esp32.write((command + '\n').encode())
        print(f"📡 Sent: {command}")

def wait_for_audio_finish():
    print("⏳ Waiting for audio...")
    while True:
        if esp32 and esp32.in_waiting > 0:
            line = esp32.readline().decode('utf-8', errors='ignore').strip()
            if "Song Finished" in line:
                break
        time.sleep(0.1)

def listen_for_speech(timeout=None, phrase_limit=4):
    with microphone as source:
        recognizer.energy_threshold = 300 
        recognizer.dynamic_energy_threshold = True
        print("🎤 Listening...")
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
            return recognizer.recognize_google(audio).lower()
        except:
            return ""

def wait_for_wake_word():
    print(f"\n💤 SYSTEM ASLEEP. Waiting for wake word...")
    while True:
        text = listen_for_speech(timeout=None, phrase_limit=3)
        if any(trigger in text for trigger in WAKE_WORDS):
            print(f"✨ WAKE WORD DETECTED ✨")
            return

# --- STARTUP ---
wait_for_wake_word()
send_to_esp("INTRO")
wait_for_audio_finish()

cap = cv2.VideoCapture(0)
last_check_time = time.time()
CHECK_INTERVAL = 8 # Reduced for faster response

print("👁️ Vision System Active")

while True:
    ret, frame = cap.read()
    if not ret: break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 6) # Adjusted sensitivity
    current_emotion = "NEUTRAL"

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        # Region of Interest for the mouth (bottom half of face)
        roi_gray_mouth = gray[y + int(h * 0.5):y + h, x:x + w]
        smiles = smile_cascade.detectMultiScale(roi_gray_mouth, 1.7, 20)

        # REFINED EMOTION LOGIC
        if len(smiles) > 0:
            current_emotion = "HAPPY"
        elif w > 280: # If face is very close/wide
            current_emotion = "SURPRISED"
        elif h > 280: # If face is elongated
            current_emotion = "ANGRY"
        elif h < 200 and w < 200: # If face looks small/withdrawn
            current_emotion = "SAD"
        else:
            current_emotion = "NEUTRAL"
        
        cv2.putText(frame, f"EMOTION: {current_emotion}", (x, y-10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # INTERACTION TRIGGER
    now = time.time()
    if (now - last_check_time > CHECK_INTERVAL) and (current_emotion != "NEUTRAL"):
        print(f"⏸️ Processing {current_emotion}...")
        
        send_to_esp(f"ASK_{current_emotion}")
        wait_for_audio_finish()

        response = listen_for_speech(timeout=5)
        print(f"🗣️ User said: {response}")

        # ADDED "DON'T PLAY" and "STAY QUIET" LOGIC
        if any(w in response for w in ['yes', 'yeah', 'play', 'sure', 'ok']):
            send_to_esp(f"PLAY_{current_emotion}")
            wait_for_audio_finish()
        elif any(w in response for w in ['no', 'stop', "don't", "don't play", 'quiet', 'shut up']):
            print("🔇 User requested silence.")
            send_to_esp("SAY_QUIET")
            wait_for_audio_finish()

        last_check_time = time.time()

    cv2.imshow("Lumi Emotion Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()