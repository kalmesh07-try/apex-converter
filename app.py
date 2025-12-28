from flask import Flask, render_template_string, request, send_file
import yt_dlp
import os
import time
import re

app = Flask(__name__)

HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Apex Eternal</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Roboto, sans-serif; background-color: #000; color: #fff; display: flex; justify-content: center; align-items: center; min-height: 100vh; overflow: hidden; }
        .bg-pulse { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: radial-gradient(circle at center, #1a1a1a 0%, #000 70%); z-index: -1; animation: pulse 10s infinite alternate; }
        @keyframes pulse { 0% { opacity: 0.8; } 100% { opacity: 1; } }
        .glass-panel { background: rgba(20, 20, 20, 0.9); border: 1px solid #333; padding: 40px 30px; border-radius: 20px; width: 90%; max-width: 440px; text-align: center; box-shadow: 0 0 50px rgba(0,255,127,0.1); }
        h1 { font-size: 32px; font-weight: 800; letter-spacing: 5px; margin-bottom: 5px; color: #00ff7f; text-transform: uppercase; text-shadow: 0 0 15px rgba(0,255,127,0.5); }
        .subtitle { color: #888; font-size: 10px; letter-spacing: 3px; margin-bottom: 30px; font-weight: 700; text-transform: uppercase; }
        .input-group { position: relative; margin-bottom: 25px; }
        input[type="text"] { width: 100%; padding: 18px; padding-right: 45px; background: #111; border: 1px solid #333; border-radius: 10px; color: #fff; font-size: 14px; outline: none; transition: 0.3s; }
        input[type="text"]:focus { border-color: #00ff7f; box-shadow: 0 0 15px rgba(0,255,127,0.2); }
        .clear-btn { position: absolute; right: 15px; top: 50%; transform: translateY(-50%); color: #888; cursor: pointer; display: none; background: none; border: none; font-size: 18px; }
        .btn-stack { display: flex; flex-direction: column; gap: 12px; }
        button.action-btn { padding: 16px; border: none; border-radius: 10px; font-weight: 700; text-transform: uppercase; font-size: 12px; letter-spacing: 1px; cursor: pointer; transition: 0.2s; }
        .btn-mp3 { background: #222; color: #fff; border: 1px solid #444; }
        .btn-mute { background: #222; color: #aaa; border: 1px solid #444; }
        .btn-full { background: #00ff7f; color: #000; box-shadow: 0 5px 20px rgba(0,255,127,0.2); }
        button.action-btn:active { transform: scale(0.98); }
        .trim-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; padding: 0 5px; }
        .trim-label { font-size: 11px; color: #666; letter-spacing: 1px; font-weight: bold; }
        .switch { position: relative; display: inline-block; width: 36px; height: 18px; }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #333; transition: .4s; border-radius: 34px; }
        .slider:before { position: absolute; content: ""; height: 12px; width: 12px; left: 3px; bottom: 3px; background-color: #888; transition: .4s; border-radius: 50%; }
        input:checked + .slider { background-color: #00ff7f; }
        input:checked + .slider:before { transform: translateX(18px); background-color: #000; }
        .trim-box { display: none; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 25px; }
        .time-inp { background: #111; border: 1px solid #333; padding: 12px; color: #00ff7f; text-align: center; border-radius: 8px; font-family: monospace; }
        .loader { display: none; margin-top: 25px; color: #00ff7f; font-size: 11px; letter-spacing: 2px; }
        .footer { margin-top: 40px; padding-top: 25px; border-top: 1px solid #222; font-size: 10px; color: #555; }
        .insta { color: #fff; text-decoration: none; font-weight: bold; margin-top: 8px; display: inline-block; padding: 5px 10px; background: #111; border-radius: 20px; }
    </style>
</head>
<body>
    <div class="bg-pulse"></div>
    <div class="glass-panel">
        <h1>Apex</h1>
        <div class="subtitle">Eternal Engine</div>
        <div class="input-group"><input type="text" id="urlInput" placeholder="Paste Link..." oninput="checkClear()"><button class="clear-btn" id="clearBtn" onclick="wipeInput()">✕</button></div>
        <div class="trim-header"><span class="trim-label">TRIM MODE</span><label class="switch"><input type="checkbox" id="trimToggle" onchange="toggleTrim()"><span class="slider"></span></label></div>
        <div class="trim-box" id="trimBox"><input type="text" id="start" class="time-inp" placeholder="Start (00:10)"><input type="text" id="end" class="time-inp" placeholder="End (00:30)"></div>
        <div class="btn-stack">
            <button class="action-btn btn-mp3" onclick="run('audio')">Download Audio</button>
            <button class="action-btn btn-mute" onclick="run('video_only')">Video Only</button>
            <button class="action-btn btn-full" onclick="run('video_full')">Full HD Video</button>
        </div>
        <div class="loader" id="loader">AUTHENTICATING...</div>
        <div class="footer">DEVELOPED BY KALMESH<br><a href="https://www.instagram.com/kalmesh_nadgoud_18?igsh=bHBhaGJ1cWZoODZ5" target="_blank" class="insta">@kalmesh_nadgoud_18</a></div>
    </div>
<script>
    function checkClear() { document.getElementById('clearBtn').style.display = document.getElementById('urlInput').value ? 'block' : 'none'; }
    function wipeInput() { document.getElementById('urlInput').value = ''; checkClear(); }
    function toggleTrim() { document.getElementById('trimBox').style.display = document.getElementById('trimToggle').checked ? 'grid' : 'none'; }
    async function run(mode) {
        const url = document.getElementById('urlInput').value; const loader = document.getElementById('loader');
        const isTrim = document.getElementById('trimToggle').checked; const sTime = document.getElementById('start').value; const eTime = document.getElementById('end').value;
        if (!url) { alert("Paste a Link first!"); return; }
        if (isTrim && (!sTime || !eTime)) { alert("Enter Start/End Time!"); return; }
        loader.style.display = 'block'; loader.innerText = "AUTHENTICATING...";
        const data = new URLSearchParams(); data.append('url', url); data.append('mode', mode);
        if (isTrim) { data.append('trim', 'true'); data.append('start', sTime); data.append('end', eTime); }
        try {
            const res = await fetch('/download', { method: 'POST', headers: {'Content-Type': 'application/x-www-form-urlencoded'}, body: data });
            if (res.ok) {
                const disp = res.headers.get('Content-Disposition'); let fname = "Apex_Media";
                if (disp && disp.includes('filename=')) { fname = disp.split('filename=')[1].replace(/"/g, ''); }
                const blob = await res.blob(); const lnk = window.URL.createObjectURL(blob); const a = document.createElement('a');
                a.href = lnk; a.download = fname; document.body.appendChild(a); a.click(); a.remove();
                loader.innerText = "SUCCESS"; setTimeout(() => loader.style.display = 'none', 3000);
            } else { const txt = await res.text(); loader.innerText = "ERROR: " + txt; }
        } catch (e) { loader.innerText = "FAILED"; }
    }
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_CODE)

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    mode = request.form.get('mode')
    do_trim = request.form.get('trim') == 'true'
    start_time = request.form.get('start')
    end_time = request.form.get('end')
    timestamp = int(time.time())

    # --- USING YOUR PASTED COOKIES ---
    ydl_opts = {
        'quiet': True,
        'outtmpl': f"temp_{timestamp}.%(ext)s",
        'cookiefile': 'cookies.txt',  # <--- THIS IS THE KEY
        'nocheckcertificate': True,
        'ignoreerrors': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            rt = info.get('title', f'Apex_{timestamp}')
            if len(rt) > 50: rt = rt[:50]
            clean_title = re.sub(r'[\\/*?:"<>|]', "", rt).strip()
    except Exception as e:
        clean_title = f"Apex_{timestamp}"

    # Trim Logic
    if do_trim and start_time and end_time:
        ydl_opts['download_sections'] = [f"*{start_time}-{end_time}"]
        ydl_opts['force_keyframes_at_cuts'] = True
        clean_title += "_Cut"

    if mode == 'audio':
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3'}]
        f_ext = 'mp3'
    elif mode == 'video_only':
        ydl_opts['format'] = 'bestvideo'
        f_ext = 'mp4'
        clean_title += "_Mute"
    else:
        ydl_opts['format'] = 'bestvideo+bestaudio/best'
        ydl_opts['merge_output_format'] = 'mp4'
        f_ext = 'mp4'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        t_file = f"temp_{timestamp}.{f_ext}"
        if not os.path.exists(t_file):
            for f in os.listdir('.'):
                if f.startswith(f"temp_{timestamp}"):
                    t_file = f; break
        
        return send_file(t_file, as_attachment=True, download_name=f"{clean_title}.{f_ext}")
    except Exception as e: return str(e), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
