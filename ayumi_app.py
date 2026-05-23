import tkinter as tk
from tkinter import scrolledtext
import threading
import speech_recognition as sr
import pyttsx3
import wikipedia
import webbrowser
import datetime
import os
import winsound
import pyautogui
import urllib.request
import re

# Setup Wikipedia language
wikipedia.set_lang("id")

class AyumiAssistant(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("AYUMI - AI Voice Assistant")
        self.geometry("800x600")
        self.configure(bg="#0a0e27")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # UI Setup
        self.chat_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, bg="#1a1f3a", fg="#00d9ff", font=("Inter", 12))
        self.chat_area.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        self.chat_area.insert(tk.END, "Sistem: Memulai AYUMI... Siap mendengarkan di latar belakang.\n")
        self.chat_area.configure(state='disabled')

        # Speech Engine Setup
        self.engine = pyttsx3.init()
        # Mencoba mengatur suara ke bahasa Indonesia jika tersedia
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if "indonesia" in voice.name.lower() or "id" in voice.languages:
                self.engine.setProperty('voice', voice.id)
                break
        
        self.recognizer = sr.Recognizer()
        
        # State
        self.running = True

        # Start daemon thread for listening
        self.listen_thread = threading.Thread(target=self.wake_word_listener, daemon=True)
        self.listen_thread.start()

    def log_message(self, sender, message):
        now = datetime.datetime.now().strftime("[%H:%M:%S]")
        log_text = f"{now} {sender}: {message}\n"
        
        self.chat_area.configure(state='normal')
        self.chat_area.insert(tk.END, log_text)
        self.chat_area.see(tk.END)
        self.chat_area.configure(state='disabled')

    def speak(self, text):
        self.log_message("AYUMI", text)
        self.engine.say(text)
        self.engine.runAndWait()

    def wake_word_listener(self):
        with sr.Microphone() as source:
            # Adjust ambient noise calibration initially
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            while self.running:
                try:
                    self.log_message("Sistem", "Mendengarkan... (Awali perintah dengan 'Ayumi')")
                    audio = self.recognizer.listen(source, timeout=8, phrase_time_limit=10)
                    text = self.recognizer.recognize_google(audio, language='id-ID').lower()
                    
                    # Tambahan Log untuk melihat apa yang ditangkap oleh mikrofon:
                    self.log_message("Debug", f"Terdengar: '{text}'")
                    
                    wake_words = ["halo ayumi", "hai ayumi", "ai yumi", "hayumi", "ayumi", "yumi"]
                    is_wake_word_spoken = False
                    
                    for wake_word in wake_words:
                        if wake_word in text:
                            is_wake_word_spoken = True
                            # Ekstrak perintah setelah wake word
                            command = text.split(wake_word, 1)[1].strip()
                            
                            if command:
                                # Jika ada perintah langsung (misal: "Ayumi buka youtube")
                                winsound.Beep(1000, 200)
                                self.log_message("Anda", command)
                                
                                if "stop" == command or "berhenti" in command or "tidur" in command:
                                    self.speak("Baik, saya kembali siaga.")
                                else:
                                    self.process_command(command)
                            else:
                                # Jika hanya memanggil "Ayumi"
                                winsound.Beep(1000, 200)
                                self.speak("Ya, ada yang bisa saya bantu? Awali perintah Anda dengan nama saya.")
                            
                            break # Hentikan pengecekan wake word jika sudah ketemu
                            
                except sr.WaitTimeoutError:
                    pass
                except sr.UnknownValueError:
                    pass
                except sr.RequestError:
                    self.log_message("Sistem", "Gangguan koneksi internet.")
                except Exception as e:
                    pass

    def process_command(self, command):
        if command.startswith("wikipedia"):
            topic = command.replace("wikipedia", "").strip()
            if topic:
                try:
                    result = wikipedia.summary(topic, sentences=2)
                    self.speak(f"Menurut Wikipedia: {result}")
                except wikipedia.exceptions.DisambiguationError as e:
                    self.speak("Topik terlalu umum. Silakan lebih spesifik.")
                except wikipedia.exceptions.PageError:
                    self.speak("Topik tidak ditemukan di Wikipedia.")
                except Exception as e:
                    self.speak("Gagal mengambil data dari Wikipedia.")
            else:
                self.speak("Silakan sebutkan topik yang ingin dicari di Wikipedia.")
        
        elif command.startswith("cari di youtube"):
            search_query = command.replace("cari di youtube", "").strip()
            if search_query:
                self.speak(f"Mencari {search_query} di YouTube")
                # Format URL pencarian YouTube
                webbrowser.open(f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}")
            else:
                self.speak("Video apa yang ingin dicari di YouTube?")
                
        elif command.startswith("putar video"):
            search_query = command.replace("putar video", "").strip()
            if search_query:
                self.speak(f"Memutar {search_query} di YouTube")
                try:
                    html = urllib.request.urlopen(f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}")
                    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
                    if video_ids:
                        # Langsung memutar video pertama yang ditemukan
                        webbrowser.open(f"https://www.youtube.com/watch?v={video_ids[0]}")
                    else:
                        self.speak("Maaf, video tidak ditemukan.")
                except Exception as e:
                    self.speak("Gagal memutar video. Periksa koneksi internet Anda.")
            else:
                self.speak("Video apa yang ingin diputar?")
                
        elif "jeda video" in command or "lanjutkan video" in command:
            self.speak("Oke")
            # Menekan tombol spasi untuk pause/play (karena YouTube menggunakan spasi/k)
            pyautogui.press("space")

        elif "layar penuh" in command or "keluar layar penuh" in command:
            self.speak("Siap")
            # Menekan tombol f untuk fullscreen di YouTube
            pyautogui.press("f")
            
        elif "buka youtube" in command:
            self.speak("Membuka YouTube")
            webbrowser.open("https://www.youtube.com")
            
        elif "buka google" in command:
            self.speak("Membuka Google")
            webbrowser.open("https://www.google.com")
            
        elif "buka chatgpt" in command:
            self.speak("Membuka ChatGPT")
            webbrowser.open("https://chat.openai.com")
            
        elif "jam berapa" in command or "waktu" in command:
            now = datetime.datetime.now().strftime("%H:%M")
            self.speak(f"Sekarang jam {now}")
            
        elif "tanggal berapa" in command:
            today = datetime.datetime.now().strftime("%d %B %Y")
            self.speak(f"Hari ini tanggal {today}")
            
        elif "keluar" in command or "tutup program" in command:
            self.speak("Selamat tinggal!")
            self.running = False
            self.after(2000, self.destroy)
        else:
            self.speak("Maaf, saya belum mengerti perintah tersebut.")

    def on_close(self):
        self.running = False
        self.destroy()

if __name__ == "__main__":
    app = AyumiAssistant()
    # Minimize the app to start quietly in the background
    app.iconify() 
    app.mainloop()
