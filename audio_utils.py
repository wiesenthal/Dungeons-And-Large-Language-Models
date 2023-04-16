from io import BytesIO
from gtts import gTTS

import requests

voices = {
    "antoni": "ErXwobaYiN019PkySvjV"
}

# check if key file exists
try:
    with open("eleven_labs_key.txt", "r") as f:
        eleven_labs_key = f.read()
        if eleven_labs_key == "":
            eleven_labs_key = None
except FileNotFoundError:
    eleven_labs_key = None

def generate_audio_gtts(text):
    tts = gTTS(text, lang='en')
    audio_buffer = BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer

def generate_audio(text):
    if (eleven_labs_key is None):
        return generate_audio_gtts(text)
    
    voice_id = voices["antoni"]
    path = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Content-Type": "application/json",
        "xi-api-key": eleven_labs_key
    }
    data = {
        "text": text,
        "voice_settings": {
            "stability": 0,
            "similarity_boost": 0
        }
    }
    response = requests.post(path, headers=headers, json=data)
    if response.status_code == 200:
        return response.content
    else:
        print(response.text)
        return None

def get_audio(audio_bytes):
    if audio_bytes is not None:
        audio_buffer = BytesIO(audio_bytes)
        return audio_buffer, 'audio/mpeg'
    else:
        return "No audio available", 404