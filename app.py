from flask import Flask, render_template_string, request, send_file
import yt_dlp
import os
import time
import re
import random

app = Flask(__name__)

HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Apex Midnight</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Roboto, sans-serif; background-color: #050505; color: #fff; display: flex; justify-content: center; align-items: center; min-height: 100vh; overflow: hidden; }
        .cyber-grid { position: fixed; top: 0; left: 0; width: 200%; height: 200%; background: linear-gradient(rgba(10, 10, 10, 0) 50%, #000 100%), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px); background-size: 80px 80px, 40px 40px, 40px 40px; transform: perspective(500px) rotateX(60deg) translateY(-100px) translateZ(-200px); animation: gridMove 25s linear infinite; z-index: -1; }
        @keyframes gridMove { 0% { transform: perspective(500px) rotateX(60deg) translateY(0) translateZ(-200px); } 100% { transform: perspective(500px) rotateX(60deg) translateY(80px) translateZ(-200px); } }
        .glass-panel { background: rgba(15, 15, 15, 0.85); backdrop-filter: blur(30px); -webkit-backdrop-filter: blur(30px); border: 1px solid rgba(255, 255, 255, 0.08); padding: 40px 30px; border-radius: 24px; width: 90%; max-width: 440px; text-align: center; box-shadow: 0 20px 50px rgba(0,0,0,0.8); animation: floatCard 6s ease-in-out infinite; }
        @keyframes floatCard { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
        h1 { font-size: 34px; font-weight: 800; letter-spacing: 4px; margin-bottom: 5px; background: linear-gradient(135deg, #fff 0%, #a5a5a5 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .subtitle { color: #666; font-size: 10px; letter-spacing: 3px; margin-bottom: 30px; font-weight: 700; text-transform: uppercase; }
        .input-group { position: relative; margin-bottom: 25px; }
        input[type="text"] { width: 100%; padding: 18px; padding-right: 45px; background: rgba(30, 30, 30, 0.6); border: 1px solid #333; border-radius: 12px; color: #fff; font-size: 14px; outline: none; transition: 0.3s; }
        input[type="text"]:focus { border-color: #555; background: rgba(40, 40, 40, 0.8); box-shadow: 0 0 20px rgba(255, 255, 255, 0.05); }
        .clear-btn { position: absolute; right: 15px; top: 50%; transform: translateY(-50%); color: #888; cursor: pointer; display: none; background: none; border: none; font-size: 18px; }
        .btn-stack { display: flex; flex-direction: column; gap: 15px; }
        button.action-btn { padding: 18px; border: none; border-radius: 12px; font-weight: 700; text-transform: uppercase; font-size: 12px; letter-spacing: 1px; cursor: pointer; transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); position: relative; overflow: hidden; display: flex; align-items: center; justify-content: center; gap: 10px; }
        .btn-mp3 { background: linear-gradient(145deg, #2a2a2a, #1a1a1a); color: #ccc; border: 1px solid #333; }
        .btn-mute { background: linear-gradient(145deg, #1e2a3a, #10151d); color: #8ab4f8; border: 1px solid #2c3e50; }
        .btn-full { background: linear-gradient(135deg, #eee, #ccc); color: #000; box-shadow: 0 4px 15px rgba(255,255,255,0.1); animation: subtlePulse 3s infinite; }
        button.action-btn:hover { transform: translateY(-3px) scale(1.02); filter: brightness(1.2); }
        button.action-btn:active { transform: translateY(0) scale(0.98); }
        @keyframes subtlePulse { 0% { box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.1); } 70% { box-shadow: 0 0 0 10px rgba(255, 255, 255, 0); } 100% { box-shadow: 0 0 0 0 rgba(255, 255, 255, 0); } }
        .trim-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; padding: 0 5px; }
        .trim-label { font-size: 11px; color: #777; letter-spacing: 2px; font-weight: bold; }
        .switch { position: relative; display: inline-block; width: 36px; height: 18px; }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #333; transition: .4s; border-radius: 34px; }
        .slider:before { position: absolute; content: ""; height: 12px; width: 12px; left: 3px; bottom: 3px; background-color: #888; transition: .4s; border-radius: 50%; }
        input:checked + .slider { background-color: #fff; }
        input:checked + .slider:before { transform: translateX(18px); background-color: #000; }
        .trim-box { display: none; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 25px; animation: slideIn 0.3s ease; }
        @keyframes slideIn { from { opacity: 0; transform: translateY(-5px); } to { opacity: 1; transform: translateY(0); } }
        .time-inp { background: #1a1a1a; border: 1px solid #333; padding: 12px; color: #fff; text-align: center; border-radius: 8px; font-family: monospace; }
        .loader { display: none; margin-top: 25px; color: #888; font-size: 11px; letter-spacing: 2px; }
        .footer { margin-top: 40px; padding-top: 25px; border-top: 1px solid #222; font-size: 10px; color: #555; }
        .insta { color: #fff; text-decoration: none; font-weight: bold; margin-top: 8px; display: inline-block; padding: 5px 10px; background: #111; border-radius: 20px; transition: 0.3s; }
    </style>
</head>
<body>
    <div class="cyber-grid"></div>
    <div class="glass-panel">
        <h1>Apex</h1>
        <div class="subtitle">Midnight Engine</div>
        <div class="input-group"><input type="text" id="urlInput" placeholder="Paste Link..." oninput="checkClear()"><button class="clear-btn" id="clearBtn" onclick="wipeInput()">✕</button></div>
        <div class="trim-header"><span class="trim-label">TRIM MODE</span><label class="switch"><input type="checkbox" id="trimToggle" onchange="toggleTrim()"><span class="slider"></span></label></div>
        <div class="trim-box" id="trimBox"><input type="text" id="start" class="time-inp" placeholder="Start (00:10)"><input type="text" id="end" class="time-inp" placeholder="End (00:30)"></div>
        <div class="btn-stack">
            <button class="action-btn btn-mp3" onclick="run('audio')"><span>🎵</span> Download Audio</button>
            <button class="action-btn btn-mute" onclick="run('video_only')"><span>🔇</span> Video Only</button>
            <button class="action-btn btn-full" onclick="run('video_full')"><span>🎬</span> Full HD Video</button>
        </div>
        <div class="loader" id="loader">INITIALIZING...</div>
        <div class="footer">DEVELOPED BY KALMESH<br><a href="https://www.instagram.com/kalmesh_nadgoud_18?igsh=bHBhaGJ1cWZoODZ5" target="_blank" class="insta">@kalmesh_nadgoud_18</a></div>
    </div>
<script>
    function checkClear() { document.getElementById('clearBtn').style.display = document.getElementById('urlInput').value ? 'block' : 'none'; }
    function wipeInput() { document.getElementById('urlInput').value = ''; checkClear(); }
    function toggleTrim() { document.getElementById('trimBox').style.display = document.getElementById('trimToggle').checked ? 'grid' : 'none'; }
    async function run(mode) {
        const url = document.getElementById('urlInput').value; const loader = document.getElementById('loader');
        const isTrim = document.getElementById('trimToggle').checked; const sTime = document.getElementById('start').value; const eTime = document.getElementById('end').value;
        if (!url) { alert("Please Paste a Link"); return; }
        if (isTrim && (!sTime || !eTime)) { alert("Enter Start/End Time"); return; }
        loader.style.display = 'block'; loader.innerText = isTrim ? "TRIMMING..." : "PROCESSING...";
        const data = new URLSearchParams(); data.append('url', url); data.append('mode', mode);
        if (isTrim) { data.append('trim', 'true'); data.append('start', sTime); data.append('end', eTime); }
        try {
            const res = await fetch('/download', { method: 'POST', headers: {'Content-Type': 'application/x-www-form-urlencoded'}, body: data });
            if (res.ok) {
                const disp = res.headers.get('Content-Disposition'); let fname = "Apex_Media";
                if (disp && disp.includes('filename=')) { fname = disp.split('filename=')[1].replace(/"/g, ''); }
                const blob = await res.blob(); const lnk = window.URL.createObjectURL(blob); const a = document.createElement('a');
                a.href = lnk; a.download = fname; document.body.appendChild(a); a.click(); a.remove();
                loader.innerText = "DONE"; setTimeout(() => loader.style.display = 'none', 3000);
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

    # --- CAMOUFLAGE (BYPASS YOUTUBE BOT DETECTION) ---
    ydl_opts = {
        'quiet': True,
        'outtmpl': f"temp_{timestamp}.%(ext)s",
        'nocheckcertificate': True,
        'geo_bypass': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'], # Pretend to be an Android Phone
                'player_skip': ['webpage', 'configs', 'js'], 
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            rt = info.get('title', f'Apex_{timestamp}')
            if len(rt) > 50: rt = rt[:50]
            clean_title = re.sub(r'[\\/*?:"<>|]', "", rt).strip()
    except:
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
