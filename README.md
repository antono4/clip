# Pembuat Video AI Gratis (video_ai.py)

Skrip Python sederhana untuk membuat video MP4 bergaya slide dengan narasi suara,
sepenuhnya **gratis**, **tanpa watermark**, dan **100% lokal** di komputer Anda.

## Fitur

- Teks menjadi video otomatis: tiap kalimat menjadi satu slide bergradasi.
- Narasi suara bahasa Indonesia (atau bahasa lain) memakai gTTS milik Google.
- Tanpa biaya, tanpa daftar, tanpa watermark.
- Output MP4 HD 1280x720.

## Cara Instalasi

> **Catatan:** Bila muncul error `externally-managed-environment` (PEP 668), gunakan
> virtual environment seperti di bawah ini — ini juga cara yang paling disarankan.

```bash
# 1. Buat virtual environment (sekali saja
python3 -m venv venv

# 2. Aktifkan
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate        # Windows (cmd#

# 3. Pasang dependensi
pip install moviepy pillow gtts
python -m pip install imageio-ffmpeg   # ffmpeg untuk menulis MP4

# 4. Jalankan
python video_ai.py "Judul Video" -n "Kalimat pertama. Kalimat kedua."
```

## Cara Pakai

### 1. Langsung lewat terminal
```bash
python3 video_ai.py "Judul Video" -n "Kalimat pertama. Kalimat kedua."
```

### 2. Lewat file skenario
Buat file misalnya `skenario.txt`:

```
Pembuatan Video dengan AI
Ini adalah contoh skenario. Video ini dibuat otomatis dari teks.
```

Lalu jalankan:
```bash
python3 video_ai.py -f skenario.txt -o hasil.mp4
```

## Opsi

| Argumen | Keterangan |
|---|---|---|
| judul | Judul video (opsional, default "Video AI Gratis") |
| -f, --file | File skenario (baris 1 = judul, sisanya = narasi) |
| -n, --narasi | Teks narasi langsung |
| -o, --output | Nama file output (default video_hasil.mp4) |
| --bahasa | Kode bahasa suara (default id) |

## Cara Kerja

1. Teks dipecah menjadi kalimat-kalimat.
2. Tiap kalimat dirender menjadi slide bergaya gradasi (Pillow).
3. Narasi dibuat dengan gTTS (text-to-speech).
4. Slide dan suara digabung menjadi MP4 (MoviePy + ffmpeg.

## Contoh Hasil

```bash
python3 video_ai.py "Contoh Video AI" -n "Halo. Ini video gratis."
```

## Alternatif AI Video Generator Online (Gratis

- **Luma Dream Machine** - 30 video/bulan gratis, tanpa watermark pada kualitas standar.
- **Seedance 2.0 (ByteDance)** - 10 generasi/hari gratis.
- **Google Veo 3 (via AI Studio/Gemini)** - kualitas sinematik, rate-limited.
- **Kling AI** - kredit harian gratis, bagus untuk gerakan tubuh manusia.
- **Pixverse** - kredit gratis harian, cocok untuk gaya anime.
- **Hailuo (MiniMax)** - kredit gratis harian, klip sinematik.
- **HeyGen** - avatar AI bicara, 3 video/bulan gratis.
- **CapCut Desktop** - editor gratis tanpa watermark (ekspor desktop).

## Catatan Lisensi

Kode ini bebas digunakan. Pastikan Anda mematuhi ketentuan layanan masing-masing
situs online bila memakai alternatif di atas.

Dibuat oleh AI agent (OpenHands) atas permintaan pengguna.
 
