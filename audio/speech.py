import pyttsx3
import speech_recognition


def record_audio(recorder):
    try:
        with speech_recognition.Microphone() as mic:
            recorder.adjust_for_ambient_noise(mic, duration=0.2)
            audio = recorder.listen(mic)
            text = recorder.recognize_google(audio, language='it')
            text = text.lower()
            return text

    except:
        return ''


def text_to_speech(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.say(text)
    engine.runAndWait()
