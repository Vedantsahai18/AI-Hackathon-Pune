#Python 2.x program to transcribe an Audio file 
import speech_recognition as sr 
  
AUDIO_FILE = ("./data/4.wav") 
  
# use the audio file as the audio source 
  
r = sr.Recognizer()
r.pause_threshold = 10
  
with sr.AudioFile(AUDIO_FILE) as source: 
    #reads the audio file. Here we use record instead of 
    #listen 
    r.adjust_for_ambient_noise(source)
    audio = r.record(source)   
  
try: 
    print(r.recognize_google(audio)) 
  
except sr.UnknownValueError: 
    print("Google Speech Recognition could not understand audio") 
  
except sr.RequestError as e: 
    print("Could not request results from Google Speech Recognition service; {0}".format(e))