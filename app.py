from flask import Flask, render_template_string, request, redirect
import requests
import json

app = Flask(__name__)

# --- THE APEX PROXY UI ---
HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Apex Proxy</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Roboto, sans-serif; background-color: #050505; color: #fff; display: flex; justify-content: center; align-items: center; min-height: 100vh; overflow: hidden; }
        .cyber-grid { position: fixed; top: 0; left: 0; width: 200%; height: 200%; background: linear-gradient(rgba(10, 10, 10, 0) 50%, #000 100%), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px); background-size: 80px 80px, 40px 40px, 40px 40px; transform: perspective(500px) rotateX(60deg) translateY(-100px) translateZ(-200px); animation: gridMove 25s linear infinite; z-index: -1; }
        @keyframes gridMove { 0% { transform: perspective(500px) rotateX(60deg) translateY(0) translateZ(-200px); } 100% { transform: perspective(500px) rotateX(60deg) translateY(80px) translateZ(-200px); } }
        .glass-panel { background: rgba(15, 15, 15, 0.85); backdrop-filter: blur(30px); border: 1px solid rgba(255, 255, 255, 0.08); padding: 40px 30px; border-radius: 24px; width: 90%; max-width: 440px; text-align: center; box-shadow: 0 20px 50px rgba(0,0,0,0.8); }
        h1 { font-size: 34px; font-weight: 800; letter-spacing: 4px; margin-bottom: 5px; background: linear-gradient(135deg, #fff 0%, #a5a5a5 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .subtitle { color: #666; font-size: 10px; letter-spacing: 3px; margin-bottom: 30px; font-weight: 700; text-transform: uppercase; }
        input[type="text"] { width: 100%; padding: 18px; background: rgba(30, 30, 30, 0.6); border: 1px solid #333; border-radius: 12px; color: #fff; margin-bottom: 25px; outline: none; transition: 0.3s; }
        input[type="text"]:focus { border-color: #00ff7f; box-shadow: 0 0 15px rgba(0,255,127,0.1); }
        .btn-stack { display: flex; flex-direction: column; gap: 15px; }
        button { width: 100%; padding: 18px; border: none; border-radius: 12px; font-weight: 700; text-transform: uppercase; cursor: pointer; transition: 0.3s; }
        .btn-mp3 { background: #222; color: #ccc; border: 1px solid #333; }
        .btn-full { background: #fff; color: #000; box-shadow: 0 0 15px rgba(255,255,255,0.2); }
        .footer { margin-top: 40px; padding-top: 25px; border-top: 1px solid #222; font-size: 10px; color: #555; }
        .loader { display: none; margin-top: 20px; color: #00ff7f; font-weight: bold; font-size: 12px; letter-spacing: 1px; }
    </style>
</head>
<body>
    <div class="cyber-grid"></div>
    <div class="glass-panel">
        <h1>Apex</h1>
        <div class="subtitle">Proxy Engine</div>
        <form action="/process" method="POST" onsubmit="document.getElementById('loader').style.display='block'">
            <input type="text" name="url" placeholder="Paste Instagram or YouTube Link..." required>
            <div class="btn-stack">
                <button type="submit" name="mode" value="audio" class="btn-mp3">🎵 Audio Only</button>
                <button type="submit" name="mode" value="video" class="btn-full">🎬 Download Video</button>
            </div>
        </form>
        <div class="loader" id="loader">CONNECTING TO SERVER...</div>
        <div class="footer">POWERED BY COBALT • DEV BY KALMESH</div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_CODE)

@app.route('/process', methods=['POST'])
def process():
    url = request.form.get('url')
    mode = request.form.get('mode')
    
    # --- THE COBALT CONNECTION ---
    # Instead of downloading it ourselves, we send the link to Cobalt.
    api_url = "https://api.cobalt.tools/api/json"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "ApexConverter/1.0"
    }
    
    # Configure the request
    payload = {
        "url": url,
        "videoQuality": "1080",
        "audioFormat": "mp3",
        "downloadMode": "audio" if mode == "audio" else "auto"
    }

    try:
        # Send request to Cobalt
        response = requests.post(api_url, json=payload, headers=headers)
        data = response.json()
        
        # Check if Cobalt gave us a download link
        if 'url' in data:
            return redirect(data['url'])
        elif 'status' in data and data['status'] == 'error':
            return f"<h3 style='color:white;text-align:center;font-family:sans-serif;'>Error: {data.get('text', 'Unknown')}</h3>"
        else:
            return f"<h3 style='color:white;text-align:center;font-family:sans-serif;'>Server Busy. Try again in 5 seconds.</h3>"
            
    except Exception as e:
        return f"<h3 style='color:white;text-align:center;font-family:sans-serif;'>Connection Failed: {str(e)}</h3>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
