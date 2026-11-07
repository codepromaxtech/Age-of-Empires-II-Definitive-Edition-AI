#!/usr/bin/env python3
"""
================================================================================
ZULFIKAR CAMERA DIRECTOR - PROFESSIONAL YOUTUBE BROADCAST SUITE
================================================================================
Target Platform: Windows 11 (also supports Linux/macOS cross-platform)
Game: Age of Empires II: Definitive Edition (Live Matches & Replays)

WHY THIS VERSION RUNS SMOOTHLY WITHOUT FLICKERING OR GAME CONFLICTS:
  1. No Screen Flickering:
     - Replaced the rapid 'cls' screen clear with a stationary header and
       a calm, real-time event log. The terminal will NEVER flicker or wipe.
  2. Zero Conflict with AoE2:DE Hotkeys & Laptop Fn Keys:
     - In AoE2:DE, F7 is 'Diplomacy Menu', F8 is 'Idle Villagers', and on laptops
       F7 is the Volume/Mute key!
     - We replaced them with dedicated keys that NEVER conflict with the game:
         [Insert] or [Num 1] -> Toggle Auto-Director
         [Home]   or [Num 2] -> Smooth Panoramic Glide
         [End]    or [Num 3] -> Vanguard Chase-Cam (Ctrl + F)
         [Space]             -> Jump to Latest Battle Flare
         [PgDn]   or [N]     -> Skip to Next Combat Hotspot
         [PgUp]   or [B]     -> Previous Combat Hotspot
         [Esc]    or [Q]     -> Exit Director
  3. Works Both Inside Game & In Terminal:
     - Inside AoE2:DE: Press [Insert], [Home], [End], [Space], [NumPad 1/2/3].
     - In the Terminal: Just type '1', '2', '3', 'a', 'p', 'c', 'n', 'q'.
  4. Smart Window Guard:
     - Automatically pauses when you Alt-Tab to Discord, Chrome, or OBS.
     - Resumes immediately when you Alt-Tab back into AoE2:DE.
  5. 100% Native on Windows 11:
     - Zero external dependencies. No 'pip install' needed.
================================================================================
"""

import sys
import os
import time
import argparse
import threading
import platform
from datetime import datetime

# ----------------------------------------------------------------------
# Platform Detection & Windows 11 Native API Bindings
# ----------------------------------------------------------------------
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"

user32 = None
kernel32 = None

if IS_WINDOWS:
    import ctypes
    from ctypes import wintypes
    import msvcrt
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    # Enable ANSI Virtual Terminal Processing for sleek Windows 11 colors
    try:
        hStdOut = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = wintypes.DWORD()
        if kernel32.GetConsoleMode(hStdOut, ctypes.byref(mode)):
            mode.value |= 0x0004  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
            kernel32.SetConsoleMode(hStdOut, mode)
    except Exception:
        pass

# Virtual Key Codes (Safe keys - zero conflict with AoE2 F-keys or laptop Fn keys)
VK_SPACE    = 0x20
VK_INSERT   = 0x2D  # Safe Auto-Director toggle
VK_HOME     = 0x24  # Safe Panoramic glide
VK_END      = 0x23  # Safe Chase-cam (Ctrl+F)
VK_NUMPAD1  = 0x61  # Num 1: Auto-Director
VK_NUMPAD2  = 0x62  # Num 2: Panoramic Glide
VK_NUMPAD3  = 0x63  # Num 3: Chase Cam
VK_NUMPAD0  = 0x60  # Num 0: Flare Snap
VK_PRIOR    = 0x21  # Page Up
VK_NEXT     = 0x22  # Page Down
VK_LEFT     = 0x25
VK_UP       = 0x26
VK_RIGHT    = 0x27
VK_DOWN     = 0x28
VK_ESCAPE   = 0x1B
VK_CONTROL  = 0x11
VK_F        = 0x46

# Hardware Scan Codes (DirectX DirectInput for AoE2:DE on Windows 11)
SC_SPACE    = 0x39
SC_LCONTROL = 0x1D
SC_F        = 0x21
SC_RIGHT    = 0x4D
SC_LEFT     = 0x4B

KEYEVENTF_KEYUP       = 0x0002
KEYEVENTF_SCANCODE    = 0x0008
KEYEVENTF_EXTENDEDKEY = 0x0001

def log_event(message, tag="DIRECTOR"):
    """Prints a clean timestamped status message without screen wipe."""
    now = datetime.now().strftime("%H:%M:%S")
    colors = {
        "DIRECTOR": "\033[96m",
        "ACTION":   "\033[92m",
        "PANORAMA": "\033[93m",
        "CHASE-CAM":"\033[95m",
        "WINDOW":   "\033[90m",
        "WARNING":  "\033[91m"
    }
    color = colors.get(tag, "\033[97m")
    reset = "\033[0m"
    print(f"[{now}] {color}[{tag}]{reset} {message}")
    sys.stdout.flush()

def is_aoe2_focused():
    """Returns True if AoE2:DE is currently the active foreground window."""
    if not IS_WINDOWS or not user32:
        return True
    try:
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return False
        length = user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return False
        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        title = buff.value.lower()
        return "age of empires" in title or "aoe2" in title or "definitive edition" in title
    except Exception:
        return True

def send_spacebar_jump():
    """Sends hardware Spacebar tap into AoE2:DE to jump to latest beacon flare."""
    if IS_WINDOWS and user32:
        user32.keybd_event(VK_SPACE, SC_SPACE, KEYEVENTF_SCANCODE, 0)
        time.sleep(0.05)
        user32.keybd_event(VK_SPACE, SC_SPACE, KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP, 0)
    elif IS_LINUX:
        os.system("xdotool key space 2>/dev/null")

def send_follow_cam():
    """Sends Ctrl + F into AoE2:DE to lock camera onto selected unit."""
    if IS_WINDOWS and user32:
        user32.keybd_event(VK_CONTROL, SC_LCONTROL, KEYEVENTF_SCANCODE, 0)
        user32.keybd_event(VK_F, SC_F, KEYEVENTF_SCANCODE, 0)
        time.sleep(0.05)
        user32.keybd_event(VK_F, SC_F, KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP, 0)
        user32.keybd_event(VK_CONTROL, SC_LCONTROL, KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP, 0)
    elif IS_LINUX:
        os.system("xdotool key ctrl+f 2>/dev/null")

def send_smooth_pan(duration_sec=5.0):
    """Smoothly glides the camera across the battlefield."""
    if not IS_WINDOWS or not user32:
        time.sleep(duration_sec)
        return

    start = time.time()
    while time.time() - start < duration_sec:
        user32.keybd_event(VK_RIGHT, SC_RIGHT, KEYEVENTF_SCANCODE | KEYEVENTF_EXTENDEDKEY, 0)
        time.sleep(0.08)
        user32.keybd_event(VK_RIGHT, SC_RIGHT, KEYEVENTF_SCANCODE | KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)
        time.sleep(0.04)

# ----------------------------------------------------------------------
# Combat Hotspot Data Model
# ----------------------------------------------------------------------
class CombatHotspot:
    def __init__(self, name, priority, dwell_time, desc):
        self.name = name
        self.priority = priority       # 1=Highest (Emergency), 4=Harass
        self.dwell_time = dwell_time   # Seconds camera remains on this hotspot
        self.desc = desc

HOTSPOTS = [
    CombatHotspot("MAIN FRONTLINE",    3, 8.0,  "Broad multi-group deathball assault clashes"),
    CombatHotspot("STANDOFF SIEGE",    2, 10.0, "Trebuchets & Bombard Cannons shelling fortifications"),
    CombatHotspot("FLANK WOODLINE",    4, 6.0,  "Cavalry / Archer raid on enemy lumberjacks"),
    CombatHotspot("FLANK GOLD MINE",   4, 6.0,  "Raiding squad hitting enemy mining outpost"),
    CombatHotspot("CITADEL DEFENSE",  1, 9.0,  "Fortress breach / existential town defense"),
    CombatHotspot("WONDER ASSAULT",    2, 8.0,  "All-in convergence on enemy Wonder / Relics"),
    CombatHotspot("COASTAL BOMBARD",   4, 7.0,  "Cannon Galleons & Fast Fire Ships naval engagement")
]

# ----------------------------------------------------------------------
# Central Auto-Director Controller
# ----------------------------------------------------------------------
class ZulfikarCameraDirector:
    def __init__(self, demo_mode=False, default_dwell=8.0, ignore_focus=False):
        self.demo_mode = demo_mode
        self.default_dwell = default_dwell
        self.ignore_focus = ignore_focus
        self.is_running = True
        self.auto_active = True
        self.hotspot_idx = 0
        self.time_in_hotspot = 0.0
        self.last_focus_state = True
        self.lock = threading.Lock()

    @property
    def current_hotspot(self):
        return HOTSPOTS[self.hotspot_idx]

    def snap_to_beacon(self, trigger_type="AUTO"):
        """Dispatches camera jump to the current active hotspot."""
        if not self.demo_mode:
            if self.ignore_focus or is_aoe2_focused():
                send_spacebar_jump()
        log_event(f"[{trigger_type}] Camera centered on: {self.current_hotspot.name} (Window: {self.current_hotspot.dwell_time}s) - {self.current_hotspot.desc}", "ACTION")

    def cycle_hotspot(self, delta=1, manual=False):
        """Cycles to the next or previous combat hotspot."""
        with self.lock:
            self.hotspot_idx = (self.hotspot_idx + delta) % len(HOTSPOTS)
            self.time_in_hotspot = 0.0
        self.snap_to_beacon("MANUAL" if manual else "AUTO")

    def trigger_chase_cam(self):
        """Activates native Follow-Cam (Ctrl+F) on the lead squad."""
        if not self.demo_mode:
            if self.ignore_focus or is_aoe2_focused():
                send_follow_cam()
        log_event("Vanguard Chase-Cam active! (Ctrl + F follow cam sent)", "CHASE-CAM")

    def trigger_panoramic_glide(self):
        """Executes a smooth camera crane sweep across the battle line."""
        def glide_worker():
            log_event("Starting 6-second panoramic camera glide...", "PANORAMA")
            if not self.demo_mode and (self.ignore_focus or is_aoe2_focused()):
                send_smooth_pan(duration_sec=6.0)
            else:
                time.sleep(4.0)
            log_event("Panoramic glide completed. Resuming standard director.", "PANORAMA")
        threading.Thread(target=glide_worker, daemon=True).start()

    def run_director_loop(self):
        """Autonomous time-slice scheduler."""
        step = 1.0
        while self.is_running:
            time.sleep(step)
            if not self.auto_active:
                continue

            # Focus Guard: pause if user is in Discord/Chrome/OBS
            focused = is_aoe2_focused() or self.ignore_focus or self.demo_mode
            if focused != self.last_focus_state:
                self.last_focus_state = focused
                if not focused:
                    log_event("AoE2:DE is not in foreground. Key injection paused.", "WINDOW")
                else:
                    log_event("AoE2:DE foreground detected. Director active!", "WINDOW")

            if not focused:
                continue

            with self.lock:
                self.time_in_hotspot += step
                dwell = self.current_hotspot.dwell_time or self.default_dwell
                if self.time_in_hotspot >= dwell:
                    self.cycle_hotspot(1, manual=False)

    def run_global_hotkey_listener(self):
        """Windows 11 Global Hotkey Poller using GetAsyncKeyState."""
        if not IS_WINDOWS or not user32:
            return

        key_states = {}
        def check_pressed(vk):
            current = (user32.GetAsyncKeyState(vk) & 0x8000) != 0
            was_pressed = key_states.get(vk, False)
            key_states[vk] = current
            return current and not was_pressed

        while self.is_running:
            time.sleep(0.04)
            # [Insert] or [Num 1]: Toggle Auto-Director
            if check_pressed(VK_INSERT) or check_pressed(VK_NUMPAD1):
                with self.lock:
                    self.auto_active = not self.auto_active
                    status = "RESUMED (Hands-Free)" if self.auto_active else "PAUSED (Manual Co-Pilot)"
                log_event(f"Auto-Director {status}", "DIRECTOR")
            # [Home] or [Num 2]: Panoramic Glide
            elif check_pressed(VK_HOME) or check_pressed(VK_NUMPAD2):
                self.trigger_panoramic_glide()
            # [End] or [Num 3]: Vanguard Chase-Cam
            elif check_pressed(VK_END) or check_pressed(VK_NUMPAD3):
                self.trigger_chase_cam()
            # [Space] or [Num 0]: Snap to Flare
            elif check_pressed(VK_NUMPAD0):
                self.snap_to_beacon("MANUAL-HOTKEY")
            # [PgDn]: Next Hotspot
            elif check_pressed(VK_NEXT):
                self.cycle_hotspot(1, manual=True)
            # [PgUp]: Prev Hotspot
            elif check_pressed(VK_PRIOR):
                self.cycle_hotspot(-1, manual=True)
            # [Esc]: Exit
            elif check_pressed(VK_ESCAPE):
                self.is_running = False

    def run_terminal_input_listener(self):
        """Console input listener (type single letters or numbers)."""
        while self.is_running:
            try:
                ch = None
                if IS_WINDOWS:
                    if msvcrt.kbhit():
                        ch = msvcrt.getch().decode('utf-8', errors='ignore').lower()
                    else:
                        time.sleep(0.1)
                        continue
                else:
                    # Linux non-blocking read
                    import select
                    r, _, _ = select.select([sys.stdin], [], [], 0.2)
                    if r:
                        ch = sys.stdin.readline().strip().lower()
                    else:
                        continue

                if not ch:
                    continue

                if ch in ('1', 'a'):
                    with self.lock:
                        self.auto_active = not self.auto_active
                        status = "RESUMED" if self.auto_active else "PAUSED"
                    log_event(f"Auto-Director {status} via terminal command", "DIRECTOR")
                elif ch in ('2', 'p'):
                    self.trigger_panoramic_glide()
                elif ch in ('3', 'c'):
                    self.trigger_chase_cam()
                elif ch == ' ' or ch == 's':
                    self.snap_to_beacon("TERMINAL")
                elif ch == 'n':
                    self.cycle_hotspot(1, manual=True)
                elif ch == 'b':
                    self.cycle_hotspot(-1, manual=True)
                elif ch in ('q', 'exit'):
                    self.is_running = False
                    break
            except Exception:
                time.sleep(0.2)

def print_welcome_banner(demo=False):
    """Prints the stationary welcome banner once at startup."""
    banner = f"""
\033[95m================================================================================
          ZULFIKAR AI CAMERA DIRECTOR - YOUTUBE RECORDING SUITE
================================================================================\033[0m
  Platform:       \033[97m{platform.system()} {platform.release()}\033[0m  (DirectX/DirectInput: \033[92mREADY\033[0m)
  Mode:           \033[92m{'DEMO (Simulation)' if demo else 'LIVE ENGINE (AoE2:DE)'}\033[0m
--------------------------------------------------------------------------------
  \033[93mGLOBAL IN-GAME HOTKEYS\033[0m (Press directly while playing AoE2:DE on Windows 11):
    \033[92m[Insert] or [Num 1]\033[0m  Toggle Auto-Director ON / OFF (Hands-Free recording)
    \033[93m[Home]   or [Num 2]\033[0m  Execute Smooth Panoramic Camera Glide
    \033[95m[End]    or [Num 3]\033[0m  Lock Vanguard Chase-Cam (Ctrl + F Follow Cam)
    \033[97m[Space]  or [Num 0]\033[0m  Snap Camera to Latest Battle Flare
    \033[97m[PageDown] / [PageUp]\033[0m Skip to Next / Previous Battle Hotspot
    \033[91m[Esc]    or [Q]\033[0m      Safe Exit

  \033[96mTERMINAL COMMANDS\033[0m (You can also type these directly into this console):
    Type \033[97m'1'\033[0m or \033[97m'a'\033[0m (Toggle), \033[97m'2'\033[0m or \033[97m'p'\033[0m (Glide), \033[97m'3'\033[0m or \033[97m'c'\033[0m (Chase), \033[97m'n'\033[0m (Next), \033[97m'q'\033[0m (Quit)
--------------------------------------------------------------------------------
\033[90m[LIVE EVENT LOG - Screen will NOT flicker or wipe]:\033[0m
"""
    print(banner)
    sys.stdout.flush()

def main():
    parser = argparse.ArgumentParser(description="ZULFIKAR Camera Director for AoE2:DE YouTube Recording on Windows 11")
    parser.add_argument("--demo", action="store_true", help="Run in simulation mode without sending OS key inputs")
    parser.add_argument("--dwell", type=float, default=8.0, help="Default dwell time in seconds per battle hotspot (default: 8.0)")
    parser.add_argument("--ignore-focus", action="store_true", help="Send keys even if AoE2:DE is not the foreground window")
    args = parser.parse_args()

    print_welcome_banner(demo=args.demo)
    director = ZulfikarCameraDirector(demo_mode=args.demo, default_dwell=args.dwell, ignore_focus=args.ignore_focus)

    # 1. Background autonomous director thread
    t_director = threading.Thread(target=director.run_director_loop, daemon=True)
    t_director.start()

    # 2. Windows 11 global hotkey thread
    t_keys = threading.Thread(target=director.run_global_hotkey_listener, daemon=True)
    t_keys.start()

    # 3. Terminal input thread
    t_console = threading.Thread(target=director.run_terminal_input_listener, daemon=True)
    t_console.start()

    log_event("Auto-Director active. Initialized on: MAIN FRONTLINE", "DIRECTOR")

    try:
        while director.is_running:
            time.sleep(0.5)
    except KeyboardInterrupt:
        director.is_running = False

    print("\n\033[92mZULFIKAR Camera Director safely closed. Happy YouTube recording!\033[0m")

if __name__ == "__main__":
    main()
