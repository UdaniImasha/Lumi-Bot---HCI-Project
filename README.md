# Lumi Bot – Emotion Aware Smart Lamp

Lumi Bot is an interactive smart lamp that detects a user's emotions via facial recognition and voice interaction, then responds with dynamic lighting and music to enhance the environment.

## Features
- Real-time face and emotion detection
- Wake-word activation ("Hey Lumi")
- Mood-based LED lighting
- Music playback based on detected emotion
- Serial communication between Python and ESP32

## Technologies
- Python, OpenCV, SpeechRecognition
- ESP32 (Arduino)
- WS2812B LED Strip
- MAX98357A I2S Audio Amplifier
- Micro SD Card Module

## Hardware Components
- ESP32 Development Board
- WS2812B Addressable LED Strip
- MAX98357A I2S Amplifier + Speaker
- Micro SD Card Module
- Webcam & Microphone

## How It Works
1. System listens for the wake word "Hey Lumi".
2. Webcam detects the user's face and identifies the emotion.
3. Python sends the emotion command to the ESP32.
4. ESP32 changes LED colors and plays matching music.

The webcam detects the user's face and identifies the emotion.

Python sends the emotion command to the ESP32.

ESP32 changes LED colors and plays matching music.
