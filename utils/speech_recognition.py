# utils/speech_recognition.py
import base64
import speech_recognition as sr
import io
from pydub import AudioSegment
import tempfile
import os

def transcribe_audio(audio_data):
    """Transcribe audio data to text with enhanced error handling"""
    try:
        # Check if audio data is provided
        if not audio_data:
            return "No audio data received"
        
        # Handle different audio data formats
        if audio_data.startswith('data:audio'):
            # Remove data URL prefix
            audio_data = audio_data.split(',')[1]
        
        # Decode base64 audio data
        audio_bytes = base64.b64decode(audio_data)
        
        # Create temporary file for audio processing
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_audio:
            temp_audio.write(audio_bytes)
            temp_audio_path = temp_audio.name
        
        try:
            # Convert to WAV format using pydub
            audio = AudioSegment.from_file(temp_audio_path)
            wav_io = io.BytesIO()
            audio.export(wav_io, format='wav')
            wav_io.seek(0)
            
            # Initialize recognizer
            recognizer = sr.Recognizer()
            
            # Adjust for ambient noise and set timeout
            with sr.AudioFile(wav_io) as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = recognizer.record(source)
            
            # Use Google Speech Recognition with Indian English preference
            text = recognizer.recognize_google(audio_data, language='en-IN')
            return text
            
        except sr.UnknownValueError:
            return "Could not understand audio. Please speak clearly."
        except sr.RequestError as e:
            return f"Speech recognition service error: {e}"
        except Exception as e:
            return f"Audio processing error: {e}"
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_audio_path):
                os.unlink(temp_audio_path)
                
    except Exception as e:
        print(f"Speech recognition overall error: {e}")
        return "Error processing audio. Please try again."

def is_speech_recognition_available():
    """Check if speech recognition is available"""
    try:
        recognizer = sr.Recognizer()
        return True
    except:
        return False

def get_supported_languages():
    """Get list of supported languages for speech recognition"""
    return ['en-IN', 'en-US', 'en-GB', 'hi-IN', 'ta-IN', 'te-IN', 'bn-IN']

def transcribe_audio_file(file_path):
    """Transcribe audio from file path"""
    try:
        recognizer = sr.Recognizer()
        
        with sr.AudioFile(file_path) as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.record(source)
            
        text = recognizer.recognize_google(audio, language='en-IN')
        return text
    except Exception as e:
        print(f"File transcription error: {e}")
        return None