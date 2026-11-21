#!/bin/bash
echo "[+] Updating packages..."
pkg update && pkg upgrade -y
pkg install python git -y
echo "[+] Installing required Python libraries..."
pip install flask flask-socketio
echo "[+] Setup completed! Run the tool using: python3 sv.py"
