#!/bin/bash

# Configuration
POX_DIR="/home/ubuntu/Desktop/SDN-Project/pox"

echo "--- SDN Bandwidth Monitor: Automated Launcher ---"

# 1. Clean up environment
echo "[*] Cleaning up existing sessions..."
sudo mn -c > /dev/null 2>&1
sudo pkill -f pox.py

# 2. Allow X-server access
xhost +local:root > /dev/null

# 3. Launch POX in GNOME Terminal (instead of xterm)
echo "[*] Launching POX Controller window..."
gnome-terminal -- bash -c "cd $POX_DIR && python3 pox.py forwarding.l2_learning monitor; exec bash" &

# 4. Wait for Controller to initialize
sleep 5

# 5. Launch Mininet in THIS window
echo "[*] Launching Mininet CLI..."
echo "--------------------------------------------------------"
echo "TESTING STEPS FOR YOUR DEMO:"
echo "1. Look at the NEW terminal window. It should show 0.00 bps."
echo "2. In THIS window, run: h1 ping -c 5 h2"
echo "3. To see high bandwidth utilization, run: iperf h1 h2"
echo "--------------------------------------------------------"

sudo mn --topo single,3 --controller remote,ip=127.0.0.1,port=6633 --mac
