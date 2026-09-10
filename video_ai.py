#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pembuat video AI gratis dan lokal. Tanpa watermark dan tanpa langganan.

Alur kerja:
 1. Teks -> narasi suara (gTTS
 2. Teks -> slide gambar per kalimat (Pillow
 3. Slide + suara -> video MP4 (MoviePy + ffmpeg

Cara pakai:
     python3 video_ai.py "Judul Video" -n "Kalimat pertama. Kalimat kedua."
     python3 video_ai.py -f skenario.txt
"""

import argparse
import os
import re
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# BAGIAN 1: FONT
# ---------------------------------------------------------------------------
def cari_font(ukuran):
    """Cari font TTF yang tersedia di sistem."""
    kandidat = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ]
    for p in kandidat:
        if os.path.exists(p):
            return ImageFont.truetype(p, ukuran)
    return ImageFont.load_default(size=ukuran)

# ---------------------------------------------------------------------------
# BAGIAN 2: TEKS -> SLIDE
# ---------------------------------------------------------------------------
def bungkus_teks(teks, font, lebar_maks):
    """Pecah teks menjadi baris-baris yang muat dalam lebar."""
    baris = []
    for kata in teks.split():
        if not baris:
            baris.append(kata)
        elif font.getlength(baris[-1] + " " + kata) <= lebar_maks:
            baris[-1] += " " + kata
        else:
            baris.append(kata)
    return baris

def pecah_kalimat(teks):
    """Pecah narasi menjadi kalimat utuh; fallback per 12 kata."""
    potongan = re.split(r"(?<=[.!?])\s+", teks.strip())
    if len(potongan) > 1:
        return [c.strip() for c in potongan if c.strip()]
    kata = teks.split()
    if not kata:
        return [""]
    return [" ".join(kata[i:i+12]) for i in range(0, len(kata), 12)]

def buat_slide(judul, kalimat, nomor, total, lebar=1280, tinggi=720):
    """Buat satu frame bergaya gradasi gelap dengan aksen."""
    gambar = Image.new("RGB", (lebar, tinggi), (24, 30, 48))
    gbr = ImageDraw.Draw(gambar)
    atas = (28, 140,  255)
    bawah = (8, 16,  30)
    for y in range(tinggi):
        t = y / tinggi
        warna = tuple(int(atas[i] * (1 - t) + bawah[i] * t) for i in range(3))
        gbr.line([(0, y), (lebar, y)], fill=warna)
    # Aksen lingkaran samar
    # Aksen lingkaran samar    for cx, cy, r in [(lebar - 140, 120, 240), (80, 880,  ́ 320), (lebar //2, -60, 180)]:        gbr.ellipse([(cx - r, cy - r), (cx + r, cy + r)], outline=(60, 130,,180), width=4)

    font_besar = cari_font(56)
    font_kecil = cari_font(38)
    putih = (245,248,255)
    biru_muda = (150,200,255)
    # Judul pendek di bagian atas
    if judul:
        judul_dipotong = judul if len(judul) <= 46 else judul[:46] + "..."
        gbr.text((60,45), judul_dipotong, font=font_kecil, fill=biru_muda)
        gbr.rectangle([(60,118), (60 + font_kecil.getlength(judul_dipotong), 130)], fill=(110,170,240))
    # Kalimat utama di tengah
    bersih = " ".join(kalimat.split())
    lebar_maks = lebar - 120
    baris_kalimat = bungkus_teks(bersih, font_kecil, lebar_maks)
    if len(baris_kalimat) > 4:
        baris_kalimat = baris_kalimat[:4]
    y_mulai = tinggi //2 - (len(baris_kalimat) * 58) //2
    for i, baris in enumerate(baris_kalimat):
        gbr.text((60, y_mulai + i * 58), baris, font=font_kecil, fill=putih)
    # Indikator halaman
    if total > 1:
        label = f"{nomor} / {total}"
        gbr.text((lebar - 95, tinggi - 55), label, font=font_kecil, fill=(170,195,225))
    # Bingkai tipis
    gbr.rectangle([(24,24), (lebar -24, tinggi -24)], outline=(90,150,220), width=2)
    return gambar

# ---------------------------------------------------------------------------
# BAGIAN 3: TEKS -> SUARA (gTTS
# ---------------------------------------------------------------------------
def buat_narasi(teks, jalur_mp3, bahasa="id"):
    from gtts import gTTS
    gTTS(text=teks, lang=bahasa, slow=False).save(jalur_mp3)

# ---------------------------------------------------------------------------
# BAGIAN 4: GABUNG SLIDE + SUARA -> VIDEO
# ---------------------------------------------------------------------------
def gabung_video(jalur_slide, jalur_mp3, jalur_out, fps=24):
    """Gabungkan slide; tiap slide ditahan sesuai durasi narasi."""
    from moviepy import AudioFileClip, ImageClip, concatenate_videoclips

    audio = AudioFileClip(jalur_mp3)
    n = max(len(jalur_slide), 1)
    dur_per_slide = audio.duration / n
    klip = []
    for path in jalur_slide:
        klip.append(ImageClip(path).with_duration(max(dur_per_slide, 1.0)).resized((1280,720)))
    video = concatenate_videoclips(klip, method="chain")
    video = video.with_audio(audio)
    video.write_videofile(jalur_out, fps=fps, codec="libx264", audio_codec="aac",
                             temp_audiofile=os.path.join(tempfile.gettempdir(), "audio_tmp.m4a"),
                             logger=None)
    audio.close()

# ---------------------------------------------------------------------------
# BAGIAN 5: MAIN
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Pembuat video AI gratis dan lokal")
    ap.add_argument("judul", nargs="?", default="Video AI Gratis")
    ap.add_argument("-f", "--file", help="file skenario")
    ap.add_argument("-n", "--narasi", help="teks narasi langsung")
    ap.add_argument("-o", "--output", default="video_hasil.mp4")
    ap.add_argument("--bahasa", default="id", help="kode bahasa suara gTTS")
    args = ap.parse_args()

    if args.file:
        if not os.path.exists(args.file):
            sys.exit(f"File tidak ditemukan: {args.file}")
        with open(args.file, encoding="utf-8")as fh:
            baris = [b.strip() for b in fh if b.strip()]
        if not baris:
            sys.exit("File skenario kosong.")
        judul = baris[0]
        narasi_penuh = " ".join(baris[1:])
    else:
        judul = args.judul.strip()
        narasi_penuh = (args.narasi or "").strip()
        if not narasi_penuh:
            sys.exit("Tidak ada narasi. Pakai -n atau -f.")

    kalimat_list = pecah_kalimat(narasi_penuh)
    if not " ".join(kalimat_list).strip():
        sys.exit("Narasi kosong.")

    tmp = tempfile.mkdtemp(prefix="ai_video_")
    print(f"[1/4] Membuat {len(kalimat_list)} slide...")
    jalur_slide = []
    for i, kal in enumerate(kalimat_list, start=1):
        path = os.path.join(tmp, f"slide_{i:03d}.png")
        buat_slide(judul, kal, i, len(kalimat_list)).save(path)
        jalur_slide.append(path)

    print("[2/4] Membuat narasi suara dengan gTTS...")
    mp3 = os.path.join(tmp, "narasi.mp3")
    buat_narasi(" ".join(kalimat_list), mp3, bahasa=args.bahasa)

    print("[3/4] Menggabungkan slide dan suara menjadi video...")
    gabung_video(jalur_slide, mp3, args.output)

    print(f"[4/4] Selesai. Video tersimpan di: {args.output}")
    print("Durasi video menyesuaikan panjang narasi.")

if __name__ == "__main__":
    main()
