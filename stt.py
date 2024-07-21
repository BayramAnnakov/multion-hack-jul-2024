import speech_recognition as sr

def transcribe_audio(audio_file_path: str) -> str:
    """Transcribe audio file to text using SpeechRecognition library."""
    # Initialize the recognizer
    recognizer = sr.Recognizer()
    
    # Load the audio file
    with sr.AudioFile(audio_file_path) as source:
        audio_data = recognizer.record(source)
    
    # Recognize the speech using Google Web Speech API
    try:
        text = recognizer.recognize_google(audio_data)
        print(f"Transcription: {text}")
        return text
    except sr.UnknownValueError:
        print("Google Web Speech API could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Web Speech API; {e}")
    
    return ""