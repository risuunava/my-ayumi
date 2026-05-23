# 🎙️ Ayumi - AI Voice Assistant

Ayumi adalah asisten suara AI pintar berbasis Desktop (Windows) berbahasa Indonesia. Dirancang menggunakan Python, Ayumi berjalan secara otomatis di latar belakang dan mendengarkan perintah Anda melalui *Wake Word* ("Ayumi"). Anda cukup mengucapkan perintah dalam satu langkah (contoh: "Ayumi buka youtube") untuk mendapatkan respons.

---

## ✨ Fitur Utama
- **Always Listening (Latar Belakang)**: Ayumi terus berjaga mendengarkan suara Anda tanpa membebani memori, berkat penggunaan arsitektur *daemon thread*.
- **One-Step Command**: Tidak perlu menunggu! Langsung gabungkan panggilan dan perintah Anda dalam satu tarikan napas (misal: "Ayumi jam berapa sekarang?").
- **Auto Startup**: Terintegrasi penuh dengan Windows Startup menggunakan file `.bat` agar Ayumi langsung aktif (secara tersembunyi/tanpa terminal) saat komputer menyala.
- **Antarmuka Futuristik**: Jika dimunculkan, Ayumi memiliki GUI interaktif bertema *Dark Mode* futuristik dengan *log* aktivitas secara *real-time*.

---

## 🛠️ Persyaratan Sistem (Prerequisites)
Pastikan sistem Anda memenuhi persyaratan berikut:
- **Sistem Operasi**: Windows 10 / 11
- **Python**: Versi 3.8 atau lebih baru.
- Mikrofon aktif untuk input suara.
- Koneksi internet stabil (dibutuhkan untuk *Google Speech-to-Text* dan *Wikipedia*).

---

## 🚀 Instalasi & Konfigurasi

1. **Clone repositori ini** atau unduh ke dalam direktori lokal komputer Anda.
   ```bash
   git clone https://github.com/username-anda/ayumi-ai.git
   cd ayumi-ai
   ```

2. **Instal Library / Dependencies yang dibutuhkan**
   Buka Terminal / Command Prompt dan jalankan:
   ```bash
   pip install -r requirements.txt
   ```
   *(Library utama meliputi: `SpeechRecognition`, `pyttsx3`, `wikipedia`, `PyAutoGUI`, dll.)*

3. **Cara Menjalankan Ayumi Secara Manual**
   Jalankan perintah berikut di dalam terminal:
   ```bash
   python ayumi_app.py
   ```

---

## ⚙️ Menambahkan Ayumi ke Windows Startup

Agar Ayumi menyala otomatis setiap kali Windows dihidupkan tanpa memunculkan jendela command prompt (CMD) hitam:
1. Tekan `Windows + R`, ketik `shell:startup`, lalu tekan **Enter**.
2. Buka folder proyek Ayumi Anda.
3. Klik kanan pada file `MulaiAyumi.bat` dan pilih **Copy**.
4. Kembali ke folder Startup yang baru saja dibuka, klik kanan di tempat kosong, lalu pilih **Paste Shortcut**.
5. Selesai! Ayumi akan langsung melayani Anda di latar belakang mulai *restart* berikutnya.

---

## 🗣️ Daftar Perintah Suara (Commands)

Anda **harus mengawali** setiap kalimat dengan kata "Ayumi" (atau "Yumi", "Halo Ayumi") agar perintah tidak salah memicu. 

*Format: `[Wake Word]` + `[Perintah]`*

| Kategori | Perintah Suara | Contoh |
| --- | --- | --- |
| **Informasi** | `wikipedia [topik]` | *"Ayumi wikipedia kecerdasan buatan"* |
| | `jam berapa` / `waktu` | *"Ayumi sekarang jam berapa?"* |
| | `tanggal berapa` | *"Ayumi hari ini tanggal berapa"* |
| **Aplikasi / Web** | `buka youtube` | *"Ayumi tolong buka youtube"* |
| | `buka google` | *"Ayumi buka google"* |
| | `buka chatgpt` | *"Ayumi buka chatgpt"* |
| **Kontrol Video** | `cari di youtube [kueri]` | *"Ayumi cari di youtube tutorial python"* |
| | `putar video [kueri]` | *"Ayumi putar video musik lo-fi"* |
| | `jeda video` / `lanjutkan` | *"Ayumi jeda video"* |
| | `layar penuh` | *"Ayumi buat layar penuh"* |
| **Sistem** | `keluar` / `tutup program` | *"Ayumi tutup program"* |

*(Ayumi juga bisa diajak berinteraksi sapaan biasa dengan memanggil namanya saja, lalu ia akan menanyakan apa yang bisa dibantu).*

---

## 🎨 Arsitektur Proyek
- `ayumi_app.py`: File utama aplikasi yang berisi logika *Speech-to-Text* (STT), *Text-to-Speech* (TTS), dan antarmuka *Tkinter*.
- `MulaiAyumi.bat`: Skrip *batch* yang menjalankan aplikasi menggunakan `pythonw` (mode hening tanpa GUI terminal).
- `requirements.txt`: Daftar dependensi pihak ketiga Python.

---

## 🤝 Kontribusi
Punya ide agar Ayumi menjadi lebih pintar? Silakan lakukan *Fork* repositori ini, buat *Pull Request*, atau buka *Issues* untuk saran fitur baru!
