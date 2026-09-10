#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Server web kecil untuk membuat video AI lewat browser."""
import json
import os
import time
import sys
import tempfile
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

from video_ai import buat_narasi, buat_slide, pecah_kalimat, gabung_video

FOLDER_HASIL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hasils")
os.makedirs(FOLDER_HASIL, exist_ok=True)

HTML = chr(10).join([
"<!DOCTYPE html>",
"<html lang=id><head><meta charset=UTF-8>",
"<meta name=viewport content=width=device-width,initial-scale=1>",
"<title>Pembuat Video AI</title>",
"<style>",
"*{margin:0;padding:0;box-sizing:border-box}",
"body{font-family:Segoe UI,system-ui,sans-serif;background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 100%);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}",
".card{background:rgba(255,255,255,.06);backdrop-filter:blur(14px);border:1px solid rgba(255,255,255,.15);border-radius:22px;padding:34px;max-width:620px;width:100%;box-shadow:0 20px 60px rgba(0,0,0,.45)}",
"h1{font-size:1.6rem;color:#fff;margin-bottom:6px;display:flex;align-items:center;gap:10px}",
"p.sub{color:#93c5fd;margin-bottom:22px;font-size:.95rem}",
"label{display:block;color:#cfe4ff;font-size:.9rem;margin:14px 0 6px}",
"input,textarea,select{width:100%;padding:12px 14px;border-radius:12px;border:1px solid rgba(255,255,255,.2);background:rgba(2,6,23,.55);color:#fff;font-size:1rem;outline:none;transition:.2s}",
"input:focus,textarea:focus,select:focus{border-color:#60a5fa;box-shadow:0 0 0 3px rgba(96,165,250,.25)}",
"textarea{min-height:130px;resize:vertical}",
"button{width:100%;margin-top:22px;padding:14px;font-size:1.05rem;font-weight:700;color:#04122b;background:linear-gradient(90deg,#38bdf8,#818cf8);border:none;border-radius:12px;cursor:pointer;transition:.25s}",
"button:hover:not(:disabled){transform:translateY(-2px);box-shadow:0 10px 26px rgba(56,189,248,.4)}",
"button:disabled{opacity:.55;cursor:wait}",
".status{margin-top:18px;font-size:.92rem;color:#a7f3d0;min-height:22px;text-align:center}",
"video{width:100%;border-radius:14px;margin-top:16px;background:#000;display:none}",
"</style>",
"</head><body>",
"<div class=card>",
"<h1>🎬 AI Video Maker</h1>",
"<p class=sub>Gratis — tanpa watermark. Ketik teks, klik buat, langsung jadi video MP4.</p>",
"<form id=form>",
"<label for=judul>Judul video</label>",
"<input id=judul placeholder=Contoh: Tips Menabung cover>",
"<label for=narasi>Teks narasi</label>",
"<textarea id=narasi placeholder=Tulis kalimat narasi anda di sini. Tiap kalimat jadi satu slide.></textarea>",
"<label for=bahasa>Bahasa suara</label>",
"<select id=bahasa><option value=id>🇮🇩 Indonesia</option><option value=en>🇬🇧 English</option><option value=ar>🇸🇦 Arab</option><option value=es>🇪🇸 Spanyol</option><option value=ja>🇯🇵 Jepang</option></select>",
"<button id=btn type=submit>✨ Buat Video Sekarang</button>",
"</form>",
"<div class=status id=status></div>",
"<video id=player controls></video>",
"</div>",
"<script>",
"const f=document.getElementById(forma);const judulI=document.getElementById(judul);const narasiI=document.getElementById(narasi);const bh=document.getElementById(bahasa);const btn=document.getElementById(btn);const st=document.getElementById(status);const vid=document.getElementById(player);",
"f.addEventListener(submit,async e=>{e.preventDefault();btn.disabled=true;st.textContent=⏳ Membuat video... mohon tunggu 10-60 detik;vid.style.display=none;try{const r=await fetch(/buat,{method:POST,headers:Content-Type,application/json},body:JSON.stringify({judul:judulI.value,narasi:narasiI.value,bahasa:bh.value})});const d=await r.json();if(d.ok){st.textContent=✅ Video jadi. Klik tombol putar atau ikon unduh. Langsung ke folder: hasils/;vid.src=d.url;vid.style.display=block;vid.load();}else{st.textContent=❌ Gugal: +d.error;}}catch(err){st.textContent=❌ Error: +err.message;}finally{btn.disabled=false;}});",
"</script></body></html>"
])

def buat_video(judul, narasi, bahasa="id"):
    """Buat video dari teks; kembalikan nama file hasil."""
    kalimat = [k for k in pecah_kalimat(narasi) if k.strip()]
    if not kalimat:
        raise ValueError("Narasi kosong.")
    stempel = time.strftime("%Y%m%d-%H%M%S")
    tmp = tempfile.mkdtemp(prefix="webvid_")
    slides = []
    for i, kil in enumerate(kalimat, start=1):
        path = os.path.join(tmp, f"slide_{i:03d}.png")
        buat_slide(judul, kil, i, len(kalimat)).save(path)
        slides.append(path)
    mp3 = os.path.join(tmp, "narasi.mp3")
    buat_narasi(" ".join(kalimat), mp3, bahasa)
    nama_file = f"video_{stempel}.mp4"
    jalur_out = os.path.join(FOLDER_HASIL, nama_file)
    gabung_video(slides, mp3, jalur_out)
    return nama_file

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # senyap

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/index"):
            body = open("index.html", "rb").read() if os.path.exists("index.html") else HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self._cors()
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path.startswith("/hasil/"):
            nama = os.path.basename(urllib.parse.unquote(self.path[len("/hasil/"):]))
            jalur = os.path.join(FOLDER_HASIL, nama)
            if os.path.exists(jalur):
                body = open(jalur, "rb").read()
                self.send_response(200)
                self.send_header("Content-Type", "video/mp4")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Content-Disposition", f"attachment; filename={nama}")
                self._cors()
                self.end_headers()
                self.wfile.write(body)
                return
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"Not found")

    def do_POST(self):
        if self.path != "/buat":
            self.send_response(404)
            self.end_headers()
            return
        panjang = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(panjang)
        try:
            data = json.loads(body.decode("utf-8"))
            judul = str(data.get("judul", "")).strip()
            narasi = str(data.get("narasi", "")).strip()
            bahasa = str(data.get("bahasa", "id")).strip()
            if not narasi:
                raise ValueError("Teks narasi masih kosong.")
            nama = buat_video(judul, narasi, bahasa)
            balasan = json.dumps({"ok": True, "url": "/hasil/" + nama})
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self._cors()
            self.end_headers()
            self.wfile.write(balasan.encode("utf-8"))
        except Exception as e:
            err = json.dumps({"ok": False, "error": str(e)})
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self._cors()
            self.end_headers()
            self.wfile.write(err.encode("utf-8"))

def main():
    port = int(sys.argv[1] if len(sys.argv) > 1 else 8000)
    print(f"URL: http://localhost:{port}/")
    print("Tekan Ctrl+C untuk menghentikan server.")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()

if __name__ == "__main__":
    main()
