# 🕹️ Codex Model Shifter (H-Pattern Stick Shift)

An interactive, physics-driven manual gear shifter for AI models. Seamlessly shift and hot-swap LLM models in **VS Code Codex** in real time via **9Router** or custom OpenAI-compatible gateways.

Inspired by real-world manual transmission gated H-shifters and the *Model Shift* viral concept.

---

## ✨ Features

- **🏎️ Gated H-Pattern Shifter**: Constrained physical grooves (no teleporting across metal). The shifter stick moves strictly along column tracks and the neutral crossbar.
- **⚙️ Realistic Drag Physics & Inertia**: Drag-and-drop lever mechanics with simulated weight, damping, cornering turns, and audible mechanical clack feedback.
- **⚡ Hot-Swapping in Real Time**: Changes 9Router combo routes instantaneously without restarting VS Code, reloading windows, or disrupting active sessions.
- **🎛️ Interactive GUI Remapping**: Click *Remap Gears* to assign any model available on your gateway to any of the 8 gear positions (`1` through `7` and `R`).
- **🚀 Dual Mode (GUI & CLI)**:
  - **Desktop App**: Standalone floating widget window.
  - **CLI / Quick Shift**: Terminal command `gear 1`, `gear 2`, or full curses interactive TUI.
- **🔌 Hardware USB Shifter Support**: Includes daemon script (`shifter_daemon.py`) and 3D printable CAD models (`akaki-shifter/`) to build a physical USB H-shifter with an Arduino/ESP32.

---

## 🛠️ Architecture

```
                       ┌───────────────────────┐
                       │   VS Code (Codex)     │
                       └───────────┬───────────┘
                                   │ (model="codex")
                                   ▼
                       ┌───────────────────────┐
                       │   9Router Gateway     │
                       │   (Port 20128)        │
                       └───────────▲───────────┘
                                   │ Updates combo "codex"
               ┌───────────────────┴───────────────────┐
               │                                       │
    ┌───────────────────────┐               ┌───────────────────────┐
    │   Desktop H-Shifter   │               │   CLI / Terminal      │
    │   (Port 20129)        │               │   $ gear <number>     │
    └───────────────────────┘               └───────────────────────┘
```

---

## 🚀 Quick Start

### 1. Requirements

- Python 3.8+
- Modern Web Browser (Thorium / Chrome / Chromium / Edge / Firefox)
- Running [9Router](https://github.com/) or local AI gateway with a combo named `codex`.

### 2. Setup

Clone the repository and install:

```bash
git clone https://github.com/<your-username>/codex-shifter.git
cd codex-shifter
```

### 3. Running the Server

Start the local shifter backend:

```bash
python3 web_server.py
```

The GUI will be live at `http://127.0.0.1:20129`.

### 4. Running as a Standalone Desktop App

Make the launcher executable and run:

```bash
chmod +x codex-shifter
./codex-shifter
```

---

## ⌨️ Controls & Shortcuts

| Key | Gear | Default Profile | Description |
|:---:|:---:|:---|:---|
| `1` | **Gear 1** | `ag/gemini-3.8-flash-high` | High-speed drafting & quick chats |
| `2` | **Gear 2** | `ag/claude-sonnet-4-6` | Daily driver: code generation & refactoring |
| `3` | **Gear 3** | `ag/claude-opus-4-6-thinking` | Deep reasoning & hard algorithmic problems |
| `4` | **Gear 4** | `cx/gpt-5.6-sol-high` | Codex native solution model |
| `5` | **Gear 5** | `ds/deepseek-chat` | Economical token usage |
| `6` | **Gear 6** | `oc/mimo-v2.6-flash-free` | Xiaomi MiMo integration |
| `7` | **Gear 7** | `oc/nemotron-3-ultra-free` | Extreme context window & throughput |
| `R` | **Reverse**| `exec-fallback` | Fallback router pool |

---

## 🖨️ Physical USB H-Shifter (DIY Hardware)

Want an actual tactile mechanical shifter next to your keyboard?
The `akaki-shifter/` directory contains complete 3D printable files (`.STL`, `.STEP`) and Arduino firmware (`8_speed_shifter.ino`):

1. **3D Print**: Print the housing, shaft, knob, and ratchet mechanism.
2. **Electronics**: Connect 4–5 microswitches to an **Arduino Pro Micro (ATmega32U4)** or **Raspberry Pi Pico**.
3. **Daemon**: Run the hardware bridge:
   ```bash
   python3 shifter_daemon.py
   ```
Whenever you physically shift gears, the bridge translates USB HID/Serial signals directly into model updates.

---

## 📄 License

MIT License. Feel free to fork, customize, and share!
