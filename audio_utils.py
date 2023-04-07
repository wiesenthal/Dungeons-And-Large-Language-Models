from io import BytesIO
from gtts import gTTS

def generate_audio(text):
    tts = gTTS(text, lang='en')
    audio_buffer = BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer.getvalue()

def get_audio(audio_bytes):
    if audio_bytes is not None:
        audio_buffer = BytesIO(audio_bytes)
        return audio_buffer, 'audio/mp3'
    else:
        return "No audio available", 404