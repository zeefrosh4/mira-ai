from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
import webbrowser
import speech_recognition as sr

# Android imports
try:
    from jnius import autoclass
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Intent = autoclass('android.content.Intent')
    Uri = autoclass('android.net.Uri')
    TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
    Locale = autoclass('java.util.Locale')
    tts = None
    ANDROID = True
except:
    ANDROID = False

Window.clearcolor = (0.05, 0.05, 0.08, 1)

def speak(text):
    if ANDROID:
        try:
            global tts
            if tts:
                tts.setLanguage(Locale("en", "NG"))
                tts.setSpeechRate(0.9)
                tts.speak(text, TextToSpeech.QUEUE_FLUSH, None)
        except:
            pass
    print(f"MIRA: {text}")

def open_whatsapp_business(message="Hello boss"):
    if ANDROID:
        try:
            activity = PythonActivity.mActivity
            intent = Intent()
            intent.setAction(Intent.ACTION_VIEW)
            encoded = Uri.encode(message)
            intent.setData(Uri.parse(f"https://wa.me/?text={encoded}"))
            intent.setPackage("com.whatsapp.w4b")
            activity.startActivity(intent)
            return True
        except Exception as e:
            # Fallback to normal whatsapp
            try:
                intent.setPackage("com.whatsapp")
                activity.startActivity(intent)
                return True
            except:
                webbrowser.open(f"https://wa.me/?text={message}")
                return False
    else:
        webbrowser.open(f"https://wa.me/?text={message}")

def open_any_app(package_name):
    if ANDROID:
        try:
            activity = PythonActivity.mActivity
            pm = activity.getPackageManager()
            intent = pm.getLaunchIntentForPackage(package_name)
            activity.startActivity(intent)
            return True
        except:
            return False
    return False

class MiraScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15

        self.title = Label(
            text="[b][color=ff3366]MIRA AI[/color][/b]\nYour Naija Assistant",
            markup=True,
            font_size='24sp',
            size_hint=(1, 0.3)
        )
        self.add_widget(self.title)

        self.status = Label(
            text="Say:\n'Mira open WhatsApp Business'\n'Mira tell Mummy say I dey come'\n'Mira search jollof rice'",
            font_size='16sp',
            size_hint=(1, 0.5)
        )
        self.add_widget(self.status)

        self.mic_btn = Button(
            text="🎤 TAP TO TALK TO MIRA",
            font_size='20sp',
            size_hint=(1, 0.3),
            background_color=(1, 0.2, 0.5, 1),
            background_normal=''
        )
        self.mic_btn.bind(on_press=self.start_listening)
        self.add_widget(self.mic_btn)

    def start_listening(self, instance):
        self.status.text = "MIRA dey listen... talk now!"
        self.mic_btn.text = "Listening..."
        Clock.schedule_once(lambda dt: self.listen_and_do(), 0.5)

    def listen_and_do(self):
        r = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=1)
                audio = r.listen(source, timeout=5, phrase_time_limit=7)
                command = r.recognize_google(audio, language="en-NG").lower()
                self.status.text = f"You say: {command}"
                self.do_command(command)
        except Exception as e:
            self.status.text = "I no hear you well, tap again"
            speak("I no hear you, talk again")
            self.mic_btn.text = "🎤 TAP TO TALK TO MIRA"

    def do_command(self, command):
        if "mira" not in command:
            speak("Call my name first, say Mira")
            self.status.text = "You forget to call MIRA"
            self.mic_btn.text = "🎤 TAP TO TALK TO MIRA"
            return

        cmd = command.replace("mira", "").strip()

        # 1. Open WhatsApp Business
        if "whatsapp" in cmd and "open" in cmd:
            open_any_app("com.whatsapp.w4b")
            speak("WhatsApp Business don open boss")
            self.status.text = "Opening WhatsApp Business..."
        
        # 2. Tell person say message
        elif "tell" in cmd and "say" in cmd:
            try:
                # e.g "tell mummy say i dey come" -> message = "i dey come"
                if "say" in cmd:
                    message = cmd.split("say")[-1].strip()
                    speak(f"Okay, I dey tell am say {message}")
                    self.status.text = f"Sending: {message}"
                    open_whatsapp_business(message)
                else:
                    message = cmd.replace("tell", "").strip()
                    open_whatsapp_business(message)
            except:
                open_whatsapp_business(cmd)

        # 3. Search Google
        elif "search" in cmd:
            query = cmd.replace("search", "").strip()
            speak(f"I dey search {query} for you")
            self.status.text = f"Searching: {query}"
            webbrowser.open(f"https://www.google.com/search?q={query}")

        # 4. Open other apps
        elif "open" in cmd:
            if "youtube" in cmd:
                open_any_app("com.google.android.youtube")
            elif "facebook" in cmd:
                open_any_app("com.facebook.katana")
            else:
                speak("I don open am")
        
        else:
            speak("I hear you but I no understand, try again")
            self.status.text = f"I hear: {cmd} but I no understand"

        self.mic_btn.text = "🎤 TAP TO TALK TO MIRA"

class MiraApp(App):
    def build(self):
        global tts
        if ANDROID:
            try:
                tts = TextToSpeech(PythonActivity.mActivity, None)
            except:
                pass
        return MiraScreen()

    def on_start(self):
        speak("Hello boss, na Mira be this, I dey ready")

MiraApp().run()
