#!/usr/bin/env python3
"""
Hardware Shifter Daemon for 9Router
Reads physical USB Gear Shifter (Joystick / Gamepad HID / Serial) and shifts models automatically.
"""

import os
import sys
import time
import subprocess

# Model mappings for physical gears
GEAR_MAP = {
    1: "ag/gemini-3.8-flash-high",
    2: "ag/claude-sonnet-4-6",
    3: "ag/claude-opus-4-6-thinking",
    4: "cx/gpt-5.6-sol-high",
    5: "ds/deepseek-chat",
    6: "exec-fallback",
    7: "oc/mimo-v2.6-flash-free",
    8: "N0VA",
}

def shift(gear_num):
    model = GEAR_MAP.get(gear_num)
    if model:
        print(f"🕹️  [PHYSICAL SHIFTER]: Shifted to Gear {gear_num} -> {model}")
        subprocess.run(["gear", str(gear_num)], check=False)

def listen_evdev():
    try:
        import evdev
    except ImportError:
        print("evdev not installed. Install with `pip install evdev` or run serial mode.")
        return False

    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    shifter_dev = None
    for dev in devices:
        name_lower = dev.name.lower()
        if any(k in name_lower for k in ["shifter", "joystick", "gamepad", "arduino"]):
            shifter_dev = dev
            break

    if not shifter_dev:
        print("No USB Shifter device found via evdev.")
        return False

    print(f"Connected to USB Shifter: {shifter_dev.name} ({shifter_dev.path})")
    
    # Listen to events
    for event in shifter_dev.read_loop():
        if event.type == evdev.ecodes.EV_KEY and event.value == 1:
            # Map button codes (BTN_TRIGGER, BTN_THUMB, etc. or BTN_0..BTN_7)
            # Typically button index is event.code - evdev.ecodes.BTN_JOYSTICK or similar
            # If standard 8-button layout:
            btn_idx = event.code - 288 # Common offset for BTN_TRIGGER / BTN_JOYSTICK
            if 0 <= btn_idx < 8:
                gear_num = btn_idx + 1
                shift(gear_num)
    return True

def listen_serial(port="/dev/ttyACM0", baud=115200):
    try:
        import serial
    except ImportError:
        print("pyserial not installed. Install with `pip install pyserial`")
        return

    print(f"Connecting to Serial Shifter on {port}...")
    try:
        ser = serial.Serial(port, baud, timeout=1)
        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line.startswith("GEAR:"):
                try:
                    g = int(line.split(":")[1])
                    shift(g)
                except ValueError:
                    pass
    except Exception as e:
        print(f"Serial error: {e}")

if __name__ == "__main__":
    print("=== 9Router Hardware Shifter Listener ===")
    if not listen_evdev():
        # Fallback to serial probe if device connected via USB-CDC
        for p in ["/dev/ttyACM0", "/dev/ttyUSB0"]:
            if os.path.exists(p):
                listen_serial(p)
                sys.exit(0)
        print("Waiting for physical shifter device connection...")
