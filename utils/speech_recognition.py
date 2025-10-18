# utils/speech_recognition.py
import base64
import speech_recognition as sr
import io
from pydub import AudioSegment

def transcribe_audio(audio_data):
    """Transcribe audio data to text"""
    try:
        # Decode base64 audio data
        audio_bytes = base64.b64decode(audio_data.split(',')[1])
        
        # Convert to WAV format
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
        wav_io = io.BytesIO()
        audio.export(wav_io, format='wav')
        wav_io.seek(0)
        
        # Initialize recognizer
        recognizer = sr.Recognizer()
        
        with sr.AudioFile(wav_io) as source:
            audio = recognizer.record(source)
            
        # Use Google Speech Recognition
        text = recognizer.recognize_google(audio)
        return text
    
    except Exception as e:
        print(f"Speech recognition error: {e}")
        return "Could not transcribe audio. Please try again."