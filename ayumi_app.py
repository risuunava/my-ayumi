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
import subprocess
import random

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

        # ── Informasi & Pengetahuan ──

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

        elif command.startswith("cari di google"):
            query = command.replace("cari di google", "").strip()
            if query:
                self.speak(f"Mencari {query} di Google")
                webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
            else:
                self.speak("Apa yang ingin dicari di Google?")

        # ── Waktu & Tanggal ──

        elif "jam berapa" in command or "waktu sekarang" in command:
            now = datetime.datetime.now().strftime("%H:%M")
            self.speak(f"Sekarang jam {now}")

        elif "tanggal berapa" in command or "tanggal hari ini" in command:
            today = datetime.datetime.now().strftime("%d %B %Y")
            self.speak(f"Hari ini tanggal {today}")

        elif "hari apa" in command or "hari ini apa" in command:
            hari = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
            today = hari[datetime.datetime.now().weekday()]
            self.speak(f"Hari ini hari {today}")

        # ── YouTube ──

        elif command.startswith("cari di youtube"):
            search_query = command.replace("cari di youtube", "").strip()
            if search_query:
                self.speak(f"Mencari {search_query} di YouTube")
                webbrowser.open(f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}")
            else:
                self.speak("Video apa yang ingin dicari di YouTube?")

        elif command.startswith("putar video") or command.startswith("play"):
            search_query = command.replace("putar video", "").replace("play", "").strip()
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

        elif "jeda video" in command or "pause" in command or "lanjutkan video" in command or "resume" in command:
            self.speak("Oke")
            pyautogui.press("space")

        elif "layar penuh" in command or "fullscreen" in command or "keluar layar penuh" in command:
            self.speak("Siap")
            pyautogui.press("f")

        # ── Kontrol Volume ──

        elif "volume naik" in command or "kerasin" in command or "lebih keras" in command:
            self.speak("Menaikkan volume")
            for _ in range(5):
                pyautogui.press("volumeup")

        elif "volume turun" in command or "kecilin" in command or "lebih pelan" in command:
            self.speak("Menurunkan volume")
            for _ in range(5):
                pyautogui.press("volumedown")

        elif "mute" in command or "bisukan" in command or "diam" in command:
            self.speak("Volume dibisukan")
            pyautogui.press("volumemute")

        # ── Buka Website ──

        elif "buka youtube" in command:
            self.speak("Membuka YouTube")
            webbrowser.open("https://www.youtube.com")

        elif "buka google" in command:
            self.speak("Membuka Google")
            webbrowser.open("https://www.google.com")

        elif "buka chatgpt" in command:
            self.speak("Membuka ChatGPT")
            webbrowser.open("https://chat.openai.com")

        elif "buka github" in command:
            self.speak("Membuka GitHub")
            webbrowser.open("https://github.com")

        elif "buka gmail" in command or "buka email" in command:
            self.speak("Membuka Gmail")
            webbrowser.open("https://mail.google.com")

        elif "buka whatsapp" in command:
            self.speak("Membuka WhatsApp Web")
            webbrowser.open("https://web.whatsapp.com")

        elif "buka instagram" in command:
            self.speak("Membuka Instagram")
            webbrowser.open("https://www.instagram.com")

        elif "buka twitter" in command or "buka x" in command:
            self.speak("Membuka X")
            webbrowser.open("https://x.com")

        elif "buka tiktok" in command:
            self.speak("Membuka TikTok")
            webbrowser.open("https://www.tiktok.com")

        elif "buka spotify" in command:
            self.speak("Membuka Spotify")
            webbrowser.open("https://open.spotify.com")

        elif "buka maps" in command or "buka peta" in command:
            self.speak("Membuka Google Maps")
            webbrowser.open("https://maps.google.com")

        # ── Buka Aplikasi Windows ──

        elif "buka notepad" in command:
            self.speak("Membuka Notepad")
            subprocess.Popen("notepad.exe")

        elif "buka kalkulator" in command or "buka calculator" in command:
            self.speak("Membuka Kalkulator")
            subprocess.Popen("calc.exe")

        elif "buka file explorer" in command or "buka explorer" in command:
            self.speak("Membuka File Explorer")
            subprocess.Popen("explorer.exe")

        elif "buka task manager" in command:
            self.speak("Membuka Task Manager")
            subprocess.Popen("taskmgr.exe")

        elif "buka command prompt" in command or "buka cmd" in command:
            self.speak("Membuka Command Prompt")
            subprocess.Popen("cmd.exe")

        elif "buka pengaturan" in command or "buka settings" in command:
            self.speak("Membuka Pengaturan Windows")
            subprocess.Popen("start ms-settings:", shell=True)

        elif "buka paint" in command:
            self.speak("Membuka Paint")
            subprocess.Popen("mspaint.exe")

        # ── Kontrol Jendela ──

        elif "minimize" in command or "kecilkan jendela" in command:
            self.speak("Oke")
            pyautogui.hotkey("win", "down")

        elif "maximize" in command or "besarkan jendela" in command:
            self.speak("Oke")
            pyautogui.hotkey("win", "up")

        elif "tutup jendela" in command or "close window" in command:
            self.speak("Menutup jendela")
            pyautogui.hotkey("alt", "F4")

        elif "tab baru" in command or "new tab" in command:
            self.speak("Membuka tab baru")
            pyautogui.hotkey("ctrl", "t")

        elif "tutup tab" in command or "close tab" in command:
            self.speak("Menutup tab")
            pyautogui.hotkey("ctrl", "w")

        elif "pindah tab" in command or "tab selanjutnya" in command:
            pyautogui.hotkey("ctrl", "Tab")

        elif "pindah jendela" in command or "switch window" in command:
            pyautogui.hotkey("alt", "Tab")

        # ── Screenshot ──

        elif "screenshot" in command or "tangkap layar" in command:
            self.speak("Mengambil screenshot")
            screenshot_dir = os.path.join(os.path.expanduser("~"), "Pictures", "Ayumi Screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            filename = datetime.datetime.now().strftime("screenshot_%Y%m%d_%H%M%S.png")
            filepath = os.path.join(screenshot_dir, filename)
            img = pyautogui.screenshot()
            img.save(filepath)
            self.speak(f"Screenshot disimpan di folder Pictures")

        # ── Kontrol Sistem ──

        elif "kunci layar" in command or "lock" in command:
            self.speak("Mengunci layar")
            subprocess.Popen("rundll32.exe user32.dll,LockWorkStation")

        elif "matikan komputer" in command or "shutdown" in command:
            self.speak("Komputer akan dimatikan dalam 30 detik. Katakan batalkan shutdown untuk membatalkan.")
            subprocess.Popen("shutdown /s /t 30", shell=True)

        elif "restart komputer" in command or "restart" == command.strip():
            self.speak("Komputer akan restart dalam 30 detik. Katakan batalkan shutdown untuk membatalkan.")
            subprocess.Popen("shutdown /r /t 30", shell=True)

        elif "batalkan shutdown" in command or "cancel shutdown" in command:
            subprocess.Popen("shutdown /a", shell=True)
            self.speak("Shutdown dibatalkan.")

        elif "sleep" in command or "tidurkan komputer" in command:
            self.speak("Komputer akan masuk mode tidur")
            subprocess.Popen("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

        # ── Interaksi & Sapaan ──

        elif "siapa kamu" in command or "kamu siapa" in command:
            self.speak("Saya Ayumi, asisten suara pribadi Anda. Saya siap membantu Anda kapan saja.")

        elif "siapa yang buat kamu" in command or "siapa pembuatmu" in command:
            self.speak("Saya dibuat oleh pemilik saya sebagai asisten suara pribadi berbahasa Indonesia.")

        elif "apa kabar" in command:
            respon = random.choice([
                "Saya baik, terima kasih sudah bertanya!",
                "Selalu siap membantu Anda!",
                "Kabar saya baik. Ada yang bisa saya bantu?",
            ])
            self.speak(respon)

        elif "terima kasih" in command or "makasih" in command:
            respon = random.choice([
                "Sama-sama!",
                "Senang bisa membantu!",
                "Dengan senang hati!",
            ])
            self.speak(respon)

        elif "selamat pagi" in command:
            self.speak("Selamat pagi! Semoga harimu menyenangkan.")

        elif "selamat siang" in command:
            self.speak("Selamat siang! Sudah makan siang belum?")

        elif "selamat sore" in command:
            self.speak("Selamat sore! Semoga sorenya menyenangkan.")

        elif "selamat malam" in command:
            self.speak("Selamat malam! Jangan lupa istirahat ya.")

        elif "ceritakan lelucon" in command or "cerita lucu" in command or "bercanda" in command:
            lelucon = random.choice([
                "Kenapa ayam menyeberang jalan? Karena belum ada ojek online.",
                "Apa bedanya kamu sama kalender? Kalender selalu punya tanggal, kamu belum tentu.",
                "Kenapa matematika itu sedih? Karena banyak masalah.",
                "Apa nama ikan yang paling asin? Ikan gosip, karena suka nyebar garam.",
                "Kenapa semut tidak pernah sakit? Karena mereka punya anti-body kecil.",
            ])
            self.speak(lelucon)

        elif "motivasi" in command or "semangat" in command:
            motivasi = random.choice([
                "Percayalah pada prosesnya. Setiap langkah kecil membawamu lebih dekat ke tujuan.",
                "Kegagalan bukan akhir, tapi awal dari pembelajaran yang lebih baik.",
                "Kamu lebih kuat dari yang kamu kira. Terus maju!",
                "Hari ini mungkin sulit, tapi besok akan lebih baik. Semangat!",
            ])
            self.speak(motivasi)

        # ── Bantuan ──

        elif "bantuan" in command or "help" in command or "bisa apa" in command:
            self.speak(
                "Saya bisa membantu Anda dengan banyak hal. "
                "Misalnya: buka aplikasi, cari di Google atau YouTube, putar video, "
                "mengambil screenshot, mengontrol volume, "
                "memberitahu waktu dan tanggal, "
                "atau sekadar mengobrol. "
                "Awali setiap perintah dengan nama saya, Ayumi."
            )

        # ── Keluar ──

        elif "keluar" in command or "tutup program" in command:
            self.speak("Selamat tinggal!")
            self.running = False
            self.after(2000, self.destroy)

        else:
            self.speak("Maaf, saya belum mengerti perintah tersebut. Katakan 'bantuan' untuk melihat apa yang bisa saya lakukan.")

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
