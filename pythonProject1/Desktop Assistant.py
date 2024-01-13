
import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import pywhatkit
import webbrowser

engine=pyttsx3.init()
voices=engine.getProperty('voices')
engine.setProperty('voice',voices[1].id)
def take_command():
    recod=sr.Recognizer()
    with sr.Microphone() as source:
        print("listening...")
        audio=recod.listen(source)
        try:
            text=recod.recognize_google(audio,language='en-in')
            text=text.lower()
            if 'garv' in text:
                text=text.replace('garv','')
                print(text)
                return text
        except sr.UnknownValueError:
            print("Sorry could not recognize your voice")
        except sr.RequestError as e:
            print("Could not request results from google speech recognition service; {0}".format(e))
def talk(text):
    engine.say(text)
    engine.runAndWait()
def date():
    now=datetime.datetime.now().strftime("%I:%M:%S")
    talk(now)
def wiki(query):
    talk("Searching...")
    query=query.replace("wikipedia","")
    result=wikipedia.summary(query,sentences=2)
    talk(result)
def greetings():
    a=phase()
    talk("Hello sir,",a," I am your personal assistant garv. How may I help you?")
def phase():
    now=datetime.datetime.now()
    if now.hour<12:
        return "Good Morning"
    elif 12<=now.hour<18:
        return "Good Evening"
    else:
        return "Good night"
def song(query):
    query = query.replace("play song", "")
    print("Playing"+query)
    talk("Playing"+query)
    pywhatkit.playonyt(query)

#the main function
if __name__ == '__main__':
    greetings()
    while True:
        query = take_command().lower()
        if 'stop' in query:
            talk("Bye sir, have a nice day")
            break

        elif 'open youtube' in query:
            webbrowser.open("youtube.com")
            talk("Opening youtube")

        elif 'open google' in query:
            webbrowser.open("google.com")
            talk("Opening google")

        elif 'open github' in query:
            webbrowser.open("github.com")
            talk("Opening github")

        elif 'date' in query:
            date()

        elif 'wikipedia' in query:
            wiki(query)

        elif 'play song' in query:
            talk("Playing your favourite song")
            song(query)

        elif 'open yahoo' in query:
            webbrowser.open("https://www.yahoo.com")
            talk("opening yahoo")

        elif 'open gmail' in query:
            webbrowser.open("https://mail.google.com")
            talk("opening google mail")

        elif 'open snapdeal' in query:
            webbrowser.open("https://www.snapdeal.com")
            talk("opening snapdeal")

        elif 'open amazon' in query or 'shop online' in query:
            webbrowser.open("https://www.amazon.com")
            talk("opening amazon")

        elif 'open flipkart' in query:
            webbrowser.open("https://www.flipkart.com")
            talk("opening flipkart")

        elif 'open facebook' in query:
            webbrowser.open("https://www.facebook.com")
            talk("opening facebook")

        elif 'open instagram' in query:
            webbrowser.open("https://www.instagram.com")
            talk("opening instagram")

        elif 'open linkedin' in query:
            webbrowser.open("https://www.linkedin.com")
            talk("opening linkedin")

        elif 'weather' in query:
            webbrowser.open("https://www.accuweather.com")
            talk("opening weather report")

        else:
            talk("Sorry I could not understand your query. Please try again")



