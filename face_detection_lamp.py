import cv2
import time
import serial
import speech_recognition as sr

# --- CONFIGURATION ---
ESP_PORT = 'COM8'  # Check Device Manager to confirm
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
# If it still doesn't hear you, try sr.Microphone(device_index=1)
# You can list devices using: print(sr.Microphone.list_microphone_names())
microphone = sr.Microphone()

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_smile.xml")

def send_to_esp(command):
    if esp32:
        esp32.write((command + '\n').encode())
        print(f"📡 Sent: {command}")

def wait_for_audio_finish():
    print("⏳ Waiting for ESP32 to finish audio...")
    while True:
        if esp32 and esp32.in_waiting > 0:
            line = esp32.readline().decode('utf-8', errors='ignore').strip()
            if "Song Finished" in line:
                print("✅ ESP32 Audio Done.")
                break
        time.sleep(0.1)

def listen_for_speech(timeout=None, phrase_limit=4):
    with microphone as source:
        # Lower threshold = more sensitive. 300 is a good starting point.
        recognizer.energy_threshold = 300 
        recognizer.dynamic_energy_threshold = True
        print("🎤 Listening...")
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
            text = recognizer.recognize_google(audio).lower()
            print(f"🗣️ Heard: {text}")
            return text
        except Exception:
            return ""

def wait_for_wake_word():
    print(f"\n💤 SYSTEM ASLEEP. Say one of: {WAKE_WORDS}")
    while True:
        text = listen_for_speech(timeout=None, phrase_limit=3)
        if any(trigger in text for trigger in WAKE_WORDS):
            print(f"✨ WAKE WORD DETECTED ✨")
            return
        elif text:
            print(f"   (Heard '{text}', but not a wake word)")

# --- EXECUTION ---
wait_for_wake_word()

print("--- SYSTEM WAKING UP ---")
send_to_esp("INTRO")
wait_for_audio_finish()

cap = cv2.VideoCapture(0)
last_check_time = time.time()
CHECK_INTERVAL = 10 

print("👁️ Vision System Active")

while True:
    ret, frame = cap.read()
    if not ret: break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    current_emotion = "NEUTRAL"

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        roi_gray = gray[y+int(h/2):y+h, x:x+w]
        smiles = smile_cascade.detectMultiScale(roi_gray, 1.7, 22)

        if len(smiles) > 0: current_emotion = "HAPPY"
        elif w > 250: current_emotion = "SURPRISED"
        else: current_emotion = "NEUTRAL"
        
        cv2.putText(frame, current_emotion, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    now = time.time()
    if (now - last_check_time > CHECK_INTERVAL) and (current_emotion != "NEUTRAL"):
        print(f"⏸️ Interaction: User is {current_emotion}")
        
        # Ask question based on emotion
        send_to_esp(f"ASK_{current_emotion}")
        wait_for_audio_finish()

        # Listen for response
        response = listen_for_speech(timeout=5)
        if any(w in response for w in ['yes', 'yeah', 'play', 'sure']):
            send_to_esp(f"PLAY_{current_emotion}")
            wait_for_audio_finish()
        else:
            send_to_esp("SAY_QUIET")
            wait_for_audio_finish()

        last_check_time = time.time()

    cv2.imshow("Lumi Vision", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()