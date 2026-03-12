# 💡 Lumi: The Emotion-Responsive Smart Lamp

Lumi is an interactive robotic lamp that uses computer vision to detect human emotions and responds with synchronized light (NeoPixels) and audio (MP3 via ESP32). It features a wake-word system, voice command recognition, and a state-based interaction loop.

## 📂 Project Structure

Based on your workspace, the project is organized as follows:

* **`lumi_lamp.py`**: The main Python application handling OpenCV vision, speech recognition, and Serial communication.
* **`src/`**: Contains the ESP32 firmware (C++/Arduino) for hardware control.
* **`platformio.ini`**: Configuration for deploying code to the ESP32 using PlatformIO.
* **`haarcascade_frontalface_default.xml`**: Pre-trained model for facial detection.
* **`README.md`**: Project documentation and setup guide.

---

## 🛠️ Hardware Setup

### Components
* **ESP32** (NodeMCU or similar)
* **I2S DAC/Amplifier** (e.g., MAX98357A)
* **Micro SD Card Module** + Formatted SD Card
* **WS2812B NeoPixel Strip** (90 LEDs)
* **PC with Webcam**

### Wiring Reference



| Component | ESP32 Pin |
| :--- | :--- |
| **SD CS** | GPIO 5 |
| **SD MOSI** | GPIO 23 |
| **SD MISO** | GPIO 19 |
| **SD SCK** | GPIO 18 |
| **I2S BCLK** | GPIO 26 |
| **I2S LRC** | GPIO 25 |
| **I2S DOUT** | GPIO 22 |
| **NeoPixel DIN**| GPIO 13 |

---

## 💾 SD Card Files
Format your SD card to **FAT32**. Ensure the following MP3 files are in the root directory:
* `intro.mp3` — Greeting on wake-up.
* `happyq.mp3` / `happy.mp3` — Response for Happy state.
* `sadq.mp3` / `sad.mp3` — Response for Sad state.
* `angryq.mp3` / `angry.mp3` — Response for Angry state.
* `surprisedq.mp3` / `surprised.mp3` — Response for Surprised state.
* `response.mp3` — Audio for "Stay Quiet" or "Don't play" commands.

---

## 🚀 Installation & Running

### 1. ESP32 Firmware
1. Open this folder in **VS Code** with the **PlatformIO** extension.
2. Ensure the ESP32 code is in `src/main.cpp`.
3. Connect your ESP32 and click the **Upload** icon.

### 2. Python Environment
1. Install required libraries:
   ```bash
   pip install opencv-python pyserial SpeechRecognition PyAudio

## How It Works
1. System listens for the wake word "Hey Lumi".
2. Webcam detects the user's face and identifies the emotion.
3. Python sends the emotion command to the ESP32.
4. ESP32 changes LED colors and plays matching music.

