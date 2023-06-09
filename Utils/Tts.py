import pyttsx3

tts = pyttsx3.init()
tts.setProperty('rate', 100)
tts.setProperty('volume', 1)

voices = tts.getProperty('voices')
for voice in voices:
    tts.setProperty('voice', voice.id)


