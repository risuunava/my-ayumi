import tkinter as tk
from tkinter import scrolledtext
import threading
import speech_recognition as sr
from gtts import gTTS
import pygame
import wikipedia
import webbrowser
import datetime
import os
import tempfile
import winsound
import pyautogui
import urllib.request
import re

# Setup Wikipedia language
wikipedia.set_lang("id")

class AyumiAssistant(tk.Tk):
    def __init__(self):
        super().__init__()

        # Tema warna — lembut, bersih, modern
        self.BG       = "#1e1e2e"   # Latar utama (gelap lembut)
        self.BG_CHAT  = "#252536"   # Area chat
        self.HEADER   = "#2a2a3d"   # Header
        self.ACCENT   = "#a78bfa"   # Ungu muda (karakter Ayumi)
        self.TEXT      = "#e2e2f0"  # Teks utama
        self.TEXT_DIM  = "#8888a0"  # Teks redup
        self.BORDER    = "#35354a"  # Garis pembatas

        self.title("Ayumi")
        self.geometry("780x540")
        self.minsize(600, 420)
        self.configure(bg=self.BG)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # State
        self.running = True

        # ── Header ──
        header = tk.Frame(self, bg=self.HEADER, pady=14)
        header.pack(fill=tk.X)

        # Lingkaran kecil indikator status
        self.status_dot = tk.Canvas(header, width=12, height=12, bg=self.HEADER, highlightthickness=0)
        self.status_dot.pack(side=tk.LEFT, padx=(20, 8))
        self._dot = self.status_dot.create_oval(2, 2, 10, 10, fill="#66bb6a", outline="")

        title_frame = tk.Frame(header, bg=self.HEADER)
        title_frame.pack(side=tk.LEFT)

        tk.Label(
            title_frame, text="Ayumi", bg=self.HEADER, fg=self.TEXT,
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w")

        self.subtitle_label = tk.Label(
            title_frame, text="Siap mendengarkan",
            bg=self.HEADER, fg=self.TEXT_DIM, font=("Segoe UI", 9)
        )
        self.subtitle_label.pack(anchor="w")

        # Jam di sisi kanan header
        self.clock_label = tk.Label(
            header, text="", bg=self.HEADER, fg=self.TEXT_DIM,
            font=("Segoe UI", 9)
        )
        self.clock_label.pack(side=tk.RIGHT, padx=20)

        # Garis pembatas
        tk.Frame(self, bg=self.BORDER, height=1).pack(fill=tk.X)

        # ── Area Chat ──
        chat_frame = tk.Frame(self, bg=self.BG)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        self.chat_area = tk.Text(
            chat_frame, wrap=tk.WORD, bg=self.BG_CHAT, fg=self.TEXT,
            font=("Consolas", 10), relief=tk.FLAT,
            padx=16, pady=12, spacing1=1, spacing3=3,
            insertbackground=self.ACCENT, borderwidth=0,
            highlightthickness=0,
        )
        scrollbar = tk.Scrollbar(chat_frame, command=self.chat_area.yview, width=6)
        self.chat_area.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Tag warna per pengirim
        self.chat_area.tag_configure("ts",     foreground=self.TEXT_DIM, font=("Consolas", 9))
        self.chat_area.tag_configure("ayumi",  foreground=self.ACCENT, font=("Consolas", 10, "bold"))
        self.chat_area.tag_configure("user",   foreground="#7dd3fc", font=("Consolas", 10, "bold"))
        self.chat_area.tag_configure("sys",    foreground="#fbbf24", font=("Consolas", 10))
        self.chat_area.tag_configure("debug",  foreground="#6b7280", font=("Consolas", 9))
        self.chat_area.tag_configure("msg",    foreground=self.TEXT, font=("Consolas", 10))
        self.chat_area.tag_configure("msg_d",  foreground="#6b7280", font=("Consolas", 9))
        self.chat_area.configure(state='disabled')

        # Garis pembatas
        tk.Frame(self, bg=self.BORDER, height=1).pack(fill=tk.X)

        # ── Status Bar ──
        status_bar = tk.Frame(self, bg=self.HEADER, height=28)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        status_bar.pack_propagate(False)

        self.status_label = tk.Label(
            status_bar, text='Ucapkan "Ayumi" diikuti perintah Anda',
            bg=self.HEADER, fg=self.TEXT_DIM, font=("Segoe UI", 8),
            anchor="w", padx=16
        )
        self.status_label.pack(fill=tk.X)

        # ── Engine Setup ──
        pygame.mixer.init()
        self.speak_lock = threading.Lock()
        self.recognizer = sr.Recognizer()

        # ── Mulai ──
        self._update_clock()
        self.listen_thread = threading.Thread(target=self.wake_word_listener, daemon=True)
        self.listen_thread.start()
        self.log_message("Sistem", "Ayumi siap. Mendengarkan di latar belakang.")

    # ── Utilitas UI ──────────────────────────────────────────

    def _update_clock(self):
        if not self.running:
            return
        self.clock_label.configure(text=datetime.datetime.now().strftime("%H:%M"))
        self.after(30000, self._update_clock)

    def _set_status(self, text, dot_color="#66bb6a"):
        try:
            self.subtitle_label.configure(text=text)
            self.status_dot.itemconfigure(self._dot, fill=dot_color)
        except tk.TclError:
            pass

    def log_message(self, sender, message):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        s = sender.lower()

        tag_name = "sys"
        msg_tag = "msg"
        if s == "ayumi":
            tag_name = "ayumi"
        elif s == "anda":
            tag_name = "user"
        elif s == "debug":
            tag_name = "debug"
            msg_tag = "msg_d"

        try:
            self.chat_area.configure(state='normal')
            self.chat_area.insert(tk.END, f" {now}  ", "ts")
            self.chat_area.insert(tk.END, f"{sender}", tag_name)
            self.chat_area.insert(tk.END, f"  {message}\n", msg_tag)
            self.chat_area.see(tk.END)
            self.chat_area.configure(state='disabled')
        except tk.TclError:
            pass

    # ── TTS ──────────────────────────────────────────────────

    def speak(self, text):
        self.log_message("AYUMI", text)
        self._set_status("Berbicara...", dot_color="#fbbf24")
        try:
            with self.speak_lock:
                tts = gTTS(text=text, lang='id', slow=False)
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
                    tmp_path = f.name
                    tts.save(tmp_path)

                pygame.mixer.music.load(tmp_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)

                pygame.mixer.music.unload()
                os.remove(tmp_path)
        except Exception as e:
            self.log_message("Sistem", f"Gagal memutar suara: {e}")
        finally:
            self._set_status("Siap mendengarkan", dot_color="#66bb6a")

    # ── Wake Word Listener ───────────────────────────────────

    def wake_word_listener(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self._set_status("Mendengarkan...", dot_color="#66bb6a")
            while self.running:
                try:
                    audio = self.recognizer.listen(source, timeout=8, phrase_time_limit=10)
                    text = self.recognizer.recognize_google(audio, language='id-ID').lower()

                    self.log_message("Debug", f"Terdengar: '{text}'")

                    wake_words = ["halo ayumi", "hai ayumi", "ai yumi", "hayumi", "ayumi", "yumi"]

                    for wake_word in wake_words:
                        if wake_word in text:
                            command = text.split(wake_word, 1)[1].strip()

                            if command:
                                winsound.Beep(1000, 200)
                                self.log_message("Anda", command)

                                if "stop" == command or "berhenti" in command or "tidur" in command:
                                    self.speak("Baik, saya kembali siaga.")
                                else:
                                    self.process_command(command)
                            else:
                                winsound.Beep(1000, 200)
                                self.speak("Ya, ada yang bisa saya bantu? Awali perintah Anda dengan nama saya.")

                            break

                except sr.WaitTimeoutError:
                    pass
                except sr.UnknownValueError:
                    pass
                except sr.RequestError:
                    self.log_message("Sistem", "Gangguan koneksi internet.")
                    self._set_status("Tidak ada koneksi", dot_color="#ef4444")
                except Exception:
                    pass

    # ── Command Processor ────────────────────────────────────

    def process_command(self, command):
        if command.startswith("wikipedia"):
            topic = command.replace("wikipedia", "").strip()
            if topic:
                try:
                    result = wikipedia.summary(topic, sentences=2)
                    self.speak(f"Menurut Wikipedia: {result}")
                except wikipedia.exceptions.DisambiguationError:
                    self.speak("Topik terlalu umum. Silakan lebih spesifik.")
                except wikipedia.exceptions.PageError:
                    self.speak("Topik tidak ditemukan di Wikipedia.")
                except Exception:
                    self.speak("Gagal mengambil data dari Wikipedia.")
            else:
                self.speak("Silakan sebutkan topik yang ingin dicari di Wikipedia.")

        elif command.startswith("cari di youtube"):
            search_query = command.replace("cari di youtube", "").strip()
            if search_query:
                self.speak(f"Mencari {search_query} di YouTube")
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
                        webbrowser.open(f"https://www.youtube.com/watch?v={video_ids[0]}")
                    else:
                        self.speak("Maaf, video tidak ditemukan.")
                except Exception:
                    self.speak("Gagal memutar video. Periksa koneksi internet Anda.")
            else:
                self.speak("Video apa yang ingin diputar?")

        elif "jeda video" in command or "lanjutkan video" in command:
            self.speak("Oke")
            pyautogui.press("space")

        elif "layar penuh" in command or "keluar layar penuh" in command:
            self.speak("Siap")
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

    # ── Cleanup ──────────────────────────────────────────────

    def on_close(self):
        self.running = False
        try:
            pygame.mixer.quit()
        except Exception:
            pass
        self.destroy()

if __name__ == "__main__":
    app = AyumiAssistant()
    app.iconify()
    app.mainloop()
