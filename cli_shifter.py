#!/usr/bin/env python3
"""
9Router Codex Shifter (Cần số đổi model)
Interactive terminal UI to shift models on the fly for 9Router & Codex VS Code.
"""

import sys
import os
import json
import urllib.request
import hashlib
import curses
import subprocess

ROUTER_URL = "http://127.0.0.1:20128"
COMBO_NAME = "codex"

def get_auth_token():
    try:
        mid = open(os.path.expanduser("~/.9router/machine-id")).read().strip()
        cs = open(os.path.expanduser("~/.9router/auth/cli-secret")).read().strip()
        return hashlib.sha256(f"{mid}9r-cli-auth{cs}".encode()).hexdigest()[:16]
    except Exception as e:
        print(f"Error reading 9Router auth secrets: {e}", file=sys.stderr)
        sys.exit(1)

def get_router_key():
    env_file = os.path.expanduser("~/.hermes/.env")
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                if line.startswith("HERMES_CUSTOM_CUSTOM_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"')
    return ""

def fetch_combos(token):
    req = urllib.request.Request(f"{ROUTER_URL}/api/combos", headers={"x-9r-cli-token": token})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())["combos"]

def fetch_all_models(api_key):
    req = urllib.request.Request(f"{ROUTER_URL}/v1/models", headers={"Authorization": f"Bearer {api_key}"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            return sorted([m["id"] for m in data.get("data", []) if m["id"] != COMBO_NAME])
    except Exception:
        return []

def update_codex_combo(combo_id, token, model_name):
    data = json.dumps({"name": COMBO_NAME, "models": [model_name]}).encode()
    req = urllib.request.Request(
        f"{ROUTER_URL}/api/combos/{combo_id}",
        data=data,
        headers={"x-9r-cli-token": token, "Content-Type": "application/json"},
        method="PUT"
    )
    with urllib.request.urlopen(req) as resp:
        return resp.status == 200

# Quick gear shortcuts
GEARS = [
    ("Gear 1", "ag/gemini-3.8-flash-high", "Siêu nhanh, thông minh (Antigravity Gemini 3.8 Flash High)"),
    ("Gear 2", "ag/claude-sonnet-4-6", "Code & Refactor đỉnh (Antigravity Claude Sonnet 4.6)"),
    ("Gear 3", "ag/claude-opus-4-6-thinking", "Tư duy sâu, giải bài khó (Claude Opus 4.6 Thinking)"),
    ("Gear 4", "cx/gpt-5.6-sol-high", "OpenAI Codex Native High Reasoning"),
    ("Gear 5", "ds/deepseek-chat", "DeepSeek V3 / Chat kinh tế"),
    ("Gear R", "exec-fallback", "Combo Fallback mặc định 9Router"),
]

def notify_desktop(model_name):
    try:
        subprocess.run(["notify-send", "9Router Codex Shifter", f"Đã vào số: {model_name}"], check=False)
    except Exception:
        pass

def run_curses(stdscr, combo_id, token, current_model, all_models):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1)     # Header / Borders
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN) # Highlight
    curses.init_pair(3, curses.COLOR_GREEN, -1)    # Active model
    curses.init_pair(4, curses.COLOR_YELLOW, -1)   # Gear tag
    curses.init_pair(5, curses.COLOR_MAGENTA, -1)  # Hint

    # Combine preset gears and rest of models
    gear_model_ids = {g[1] for g in GEARS}
    items = []
    for tag, mid, desc in GEARS:
        items.append({"tag": tag, "id": mid, "desc": desc, "is_gear": True})
    
    other_models = [m for m in all_models if m not in gear_model_ids]
    for m in other_models:
        items.append({"tag": "Extra", "id": m, "desc": "Upstream 9Router model", "is_gear": False})

    selected = 0
    # pre-select current model if found
    for i, it in enumerate(items):
        if it["id"] == current_model:
            selected = i
            break

    filter_text = ""
    offset = 0

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        # Filter items
        filtered = [it for it in items if filter_text.lower() in it["id"].lower() or filter_text.lower() in it["desc"].lower() or filter_text.lower() in it["tag"].lower()]
        if selected >= len(filtered):
            selected = max(0, len(filtered) - 1)

        # Header box
        title = " 🕹️  9ROUTER CODEX SHIFTER (CẦN SỐ ĐỔI MODEL) "
        stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(1, 2, "┌" + "─" * (min(w - 6, 76)) + "┐")
        stdscr.addstr(2, 2, f"│{title.center(min(w - 6, 76))}│")
        
        status_line = f" [ Đang chạy: {current_model} ] "
        stdscr.addstr(3, 2, f"│{status_line.center(min(w - 6, 76))}│")
        stdscr.addstr(4, 2, "└" + "─" * (min(w - 6, 76)) + "┘")
        stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

        # Search bar
        search_prompt = f" 🔍 Lọc số: {filter_text}_"
        stdscr.addstr(5, 2, search_prompt[:w-4], curses.color_pair(5))

        # List viewport
        list_top = 7
        visible_lines = max(5, h - list_top - 3)

        if selected < offset:
            offset = selected
        elif selected >= offset + visible_lines:
            offset = selected - visible_lines + 1

        for idx in range(visible_lines):
            item_idx = offset + idx
            if item_idx >= len(filtered):
                break
            it = filtered[item_idx]
            y = list_top + idx

            is_active = (it["id"] == current_model)
            is_cur = (item_idx == selected)

            bullet = "▶ " if is_cur else "  "
            active_marker = " 🟢 [ACTIVE]" if is_active else ""
            
            line_str = f"{bullet}[{it['tag']:<6}] {it['id']:<30} {active_marker}"
            if len(line_str) > w - 4:
                line_str = line_str[:w-7] + "..."

            if is_cur:
                stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
                stdscr.addstr(y, 2, line_str.ljust(min(w - 4, 78)))
                stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
            else:
                if it["is_gear"]:
                    stdscr.attron(curses.color_pair(4) | curses.A_BOLD)
                    stdscr.addstr(y, 2, bullet + f"[{it['tag']:<6}] ")
                    stdscr.attroff(curses.color_pair(4) | curses.A_BOLD)
                else:
                    stdscr.addstr(y, 2, bullet + f"[{it['tag']:<6}] ")
                
                name_color = curses.color_pair(3) | curses.A_BOLD if is_active else curses.A_NORMAL
                stdscr.addstr(it['id'], name_color)
                if is_active:
                    stdscr.addstr(active_marker, curses.color_pair(3) | curses.A_BOLD)

        # Footer instructions
        footer = " [↑/↓]: Lái cần số | [Enter]: Vào số | [Số 1-5]: Số nhanh | [Esc/q]: Thoát "
        stdscr.addstr(h - 2, 2, footer[:w-4], curses.color_pair(1))
        stdscr.refresh()

        ch = stdscr.getch()

        if ch in (curses.KEY_UP, ord('k')):
            if selected > 0:
                selected -= 1
        elif ch in (curses.KEY_DOWN, ord('j')):
            if selected < len(filtered) - 1:
                selected += 1
        elif ch in (curses.KEY_ENTER, 10, 13):
            if filtered:
                target = filtered[selected]["id"]
                update_codex_combo(combo_id, token, target)
                notify_desktop(target)
                return target
        elif ch in (27, ord('q')) and not filter_text:
            return None
        elif ch in (ord('1'), ord('2'), ord('3'), ord('4'), ord('5')):
            if not filter_text:
                gear_num = int(chr(ch)) - 1
                if gear_num < len(GEARS):
                    target = GEARS[gear_num][1]
                    update_codex_combo(combo_id, token, target)
                    notify_desktop(target)
                    return target
        elif ch in (curses.KEY_BACKSPACE, 127, 8):
            if filter_text:
                filter_text = filter_text[:-1]
                selected = 0
        elif 32 <= ch <= 126:
            filter_text += chr(ch)
            selected = 0

def main():
    token = get_auth_token()
    api_key = get_router_key()
    combos = fetch_combos(token)
    
    codex_combo = next((c for c in combos if c["name"] == COMBO_NAME), None)
    if not codex_combo:
        print(f"Combo '{COMBO_NAME}' not found in 9Router!", file=sys.stderr)
        sys.exit(1)

    combo_id = codex_combo["id"]
    current_model = codex_combo["models"][0] if codex_combo["models"] else "Unknown"

    # Direct arg mode: e.g. `shift-model sonnet` or `shift-model 1`
    if len(sys.argv) > 1:
        arg = sys.argv[1].strip()
        target = None
        if arg in ("1", "2", "3", "4", "5"):
            target = GEARS[int(arg) - 1][1]
        elif arg.lower() in ("r", "fallback"):
            target = "exec-fallback"
        else:
            # Match partial name
            all_m = fetch_all_models(api_key)
            matches = [m for m in all_m if arg.lower() in m.lower()]
            if matches:
                target = matches[0]
            else:
                target = arg

        if target:
            if update_codex_combo(combo_id, token, target):
                notify_desktop(target)
                print(f"🕹️  [CẦN SỐ ĐÃ VÀO]: {target}")
                print(f"⚡ Combo 'codex' trên 9Router đã chuyển sang: {target}")
                sys.exit(0)
            else:
                print(f"Lỗi khi cập nhật combo 9Router.", file=sys.stderr)
                sys.exit(1)

    all_models = fetch_all_models(api_key)
    chosen = curses.wrapper(run_curses, combo_id, token, current_model, all_models)
    if chosen:
        print(f"🕹️  [CẦN SỐ ĐÃ VÀO]: {chosen}")
        print(f"⚡ Codex trong VS Code sẽ tự động dùng model: {chosen}")
    else:
        print("Đã giữ nguyên số hiện tại.")

if __name__ == "__main__":
    main()
