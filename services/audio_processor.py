import speech_recognition as sr
import os
import logging
from pydub import AudioSegment
import tempfile

logger = logging.getLogger(__name__)

class AudioProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
    
    def transcribe_audio(self, audio_file_path):
        """
        Transcribe audio file to text using Google Speech Recognition
        """
        wav_path = None
        try:
            # Convert audio to WAV format if needed
            wav_path = self._convert_to_wav(audio_file_path)
            
            # Use speech recognition
            with sr.AudioFile(wav_path) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.record(source)
            
            # Recognize speech using Google Web Speech API
            try:
                transcript = self.recognizer.recognize_google(audio)
                logger.info(f"Transcription successful: {len(transcript)} characters")
                return transcript
            except sr.UnknownValueError:
                logger.error("Google Speech Recognition could not understand audio")
                return None
            except sr.RequestError as e:
                logger.error(f"Could not request results from Google Speech Recognition service; {e}")
                return None
                
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return None
        finally:
            # Clean up temporary WAV file if created
            if wav_path and wav_path != audio_file_path and os.path.exists(wav_path):
                os.remove(wav_path)
    
    def _convert_to_wav(self, audio_file_path):
        """
        Convert audio file to WAV format if needed
        """
        try:
            file_extension = os.path.splitext(audio_file_path)[1].lower()
            
            # If already WAV, return as is
            if file_extension == '.wav':
                return audio_file_path
            
            # Convert to WAV
            audio = AudioSegment.from_file(audio_file_path)
            
            # Create temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                wav_path = temp_file.name
            
            audio.export(wav_path, format='wav')
            logger.info(f"Converted {file_extension} to WAV format")
            return wav_path
            
        except Exception as e:
            logger.error(f"Error converting audio to WAV: {str(e)}")
            return audio_file_path  # Return original if conversion fails
