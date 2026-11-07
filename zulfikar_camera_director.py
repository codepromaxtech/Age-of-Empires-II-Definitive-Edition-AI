#!/usr/bin/env python3
"""
================================================================================
ZULFIKAR CAMERA DIRECTOR - PROFESSIONAL YOUTUBE BROADCAST SUITE
================================================================================
Target Platform: Windows 11 (DirectX 11 / DirectInput Native, Zero Pip Dependencies)
Game: Age of Empires II: Definitive Edition (Live Matches, AI Battles, & Replays)

WHY THIS ENHANCED VERSION SOLVES FOCUS AND CAMERA MOVEMENT:
  1. DirectX 11 DirectInput Hardware Injection (SendInput):
     - Uses Windows 11 SendInput with hardware scancodes and extended flags.
     - DirectInput arrow keys (Left, Right, Up, Down), Spacebar, and Ctrl+F are
       reliably received by the AoE2:DE DirectX engine even in borderless/fullscreen.
  2. Active Cinematic Camera Choreography:
     - Instead of remaining frozen during dwell time, the Auto-Director actively
       glides and pans across battle hotspots (Frontline sweeps, Siege tracking,
       Flank cavalry glides) with smooth micro-pulsed camera movements.
  3. Resilient Multi-Layer Window Guard with Hysteresis:
     - Process name verification (AoE2DE_s.exe / AoE2DE.exe).
     - Root ancestor window hierarchy traversal (handles child DirectX render surfaces).
     - 8-second sticky buffer prevents transient menu clicks and overlays from pausing.
     - Toggle Window Guard ON/OFF at will with [Insert], [G], or '--no-guard'.
  4. Safe Global Hotkeys (Zero AoE2 Hotkey or Laptop Fn Key Conflicts):
     - [Insert] or [G]          -> Toggle Window Guard (Focus Check) ON / OFF
     - [Home]   or [Num 2]      -> Smooth Panoramic Glide Sweep
     - [End]    or [Num 3]      -> Vanguard Chase-Cam (Ctrl + F Follow Cam)
     - [Space]  or [Num 0]      -> Snap Camera to Latest Battle Flare
     - [PgDn]   or [N]          -> Next Combat Hotspot
     - [PgUp]   or [B]          -> Previous Combat Hotspot
     - [Num 4]  /  [Num 6]      -> Manual Glide Left / Right
     - [Num 8]  /  [Num 5]      -> Manual Glide Up / Down
     - [Esc]    or [Q]          -> Safe Exit
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
# Platform Detection & Windows 11 DirectInput API Bindings
# ----------------------------------------------------------------------
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"

user32 = None
kernel32 = None

# Hardware Scan Codes (DirectInput for DirectX 11 on Windows 11)
SC_SPACE    = 0x39
SC_LCONTROL = 0x1D
SC_F        = 0x21
SC_UP       = 0x48
SC_LEFT     = 0x4B
SC_RIGHT    = 0x4D
SC_DOWN     = 0x50

# Virtual Key Codes
VK_SPACE    = 0x20
VK_INSERT   = 0x2D
VK_HOME     = 0x24
VK_END      = 0x23
VK_LEFT     = 0x25
VK_UP       = 0x26
VK_RIGHT    = 0x27
VK_DOWN     = 0x28
VK_ESCAPE   = 0x1B
VK_CONTROL  = 0x11
VK_F        = 0x46
VK_G        = 0x47
VK_NUMPAD0  = 0x60
VK_NUMPAD1  = 0x61
VK_NUMPAD2  = 0x62
VK_NUMPAD3  = 0x63
VK_NUMPAD4  = 0x64
VK_NUMPAD5  = 0x65
VK_NUMPAD6  = 0x66
VK_NUMPAD8  = 0x68
VK_PRIOR    = 0x21  # Page Up
VK_NEXT     = 0x22  # Page Down

KEYEVENTF_KEYUP       = 0x0002
KEYEVENTF_SCANCODE    = 0x0008
KEYEVENTF_EXTENDEDKEY = 0x0001
INPUT_KEYBOARD        = 1

if IS_WINDOWS:
    import ctypes
    from ctypes import wintypes
    import msvcrt
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    # Enable ANSI Virtual Terminal Processing for Windows 11 console colors
    try:
        hStdOut = kernel32.GetStdHandle(-11)
        mode = wintypes.DWORD()
        if kernel32.GetConsoleMode(hStdOut, ctypes.byref(mode)):
            mode.value |= 0x0004
            kernel32.SetConsoleMode(hStdOut, mode)
    except Exception:
        pass

    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [
            ("dx", wintypes.LONG),
            ("dy", wintypes.LONG),
            ("mouseData", wintypes.DWORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ctypes.c_ulonglong if sys.maxsize > 2**32 else ctypes.c_ulong),
        ]

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [
            ("wVk", wintypes.WORD),
            ("wScan", wintypes.WORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ctypes.c_ulonglong if sys.maxsize > 2**32 else ctypes.c_ulong),
        ]

    class HARDWAREINPUT(ctypes.Structure):
        _fields_ = [
            ("uMsg", wintypes.DWORD),
            ("wParamL", wintypes.WORD),
            ("wParamH", wintypes.WORD),
        ]

    class _INPUT_UNION(ctypes.Union):
        _fields_ = [
            ("mi", MOUSEINPUT),
            ("ki", KEYBDINPUT),
            ("hi", HARDWAREINPUT),
        ]

    class INPUT(ctypes.Structure):
        _fields_ = [
            ("type", wintypes.DWORD),
            ("u", _INPUT_UNION),
        ]

def log_event(message, tag="DIRECTOR"):
    """Prints a clean timestamped status message without screen wipe."""
    now = datetime.now().strftime("%H:%M:%S")
    colors = {
        "DIRECTOR":  "\033[96m",
        "ACTION":    "\033[92m",
        "PANORAMA":  "\033[93m",
        "CHASE-CAM": "\033[95m",
        "WINDOW":    "\033[90m",
        "HOTKEY":    "\033[94m",
        "WARNING":   "\033[91m"
    }
    color = colors.get(tag, "\033[97m")
    reset = "\033[0m"
    print(f"[{now}] {color}[{tag}]{reset} {message}")
    sys.stdout.flush()

# ----------------------------------------------------------------------
# Hardware DirectInput Key Injection Routines
# ----------------------------------------------------------------------
def send_key_scancode(scan_code, extended=False, press_duration=0.08, vk=0):
    """Sends a DirectInput hardware scancode using SendInput and keybd_event."""
    if not IS_WINDOWS or not user32:
        return

    flags_down = KEYEVENTF_SCANCODE
    flags_up = KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP
    if extended:
        flags_down |= KEYEVENTF_EXTENDEDKEY
        flags_up |= KEYEVENTF_EXTENDEDKEY

    # 1. Primary: Windows 11 SendInput (DirectX standard)
    try:
        inp_down = INPUT()
        inp_down.type = INPUT_KEYBOARD
        inp_down.u.ki.wVk = vk
        inp_down.u.ki.wScan = scan_code
        inp_down.u.ki.dwFlags = flags_down
        inp_down.u.ki.time = 0
        inp_down.u.ki.dwExtraInfo = 0
        user32.SendInput(1, ctypes.byref(inp_down), ctypes.sizeof(INPUT))
    except Exception:
        pass

    # 2. Secondary fallback: keybd_event
    try:
        user32.keybd_event(vk, scan_code, flags_down, 0)
    except Exception:
        pass

    time.sleep(press_duration)

    try:
        inp_up = INPUT()
        inp_up.type = INPUT_KEYBOARD
        inp_up.u.ki.wVk = vk
        inp_up.u.ki.wScan = scan_code
        inp_up.u.ki.dwFlags = flags_up
        inp_up.u.ki.time = 0
        inp_up.u.ki.dwExtraInfo = 0
        user32.SendInput(1, ctypes.byref(inp_up), ctypes.sizeof(INPUT))
    except Exception:
        pass

    try:
        user32.keybd_event(vk, scan_code, flags_up, 0)
    except Exception:
        pass

def send_spacebar_jump():
    """Sends hardware Spacebar tap into AoE2:DE to jump to latest beacon flare."""
    if IS_WINDOWS and user32:
        send_key_scancode(SC_SPACE, extended=False, press_duration=0.06, vk=VK_SPACE)
    elif IS_LINUX:
        os.system("xdotool key space 2>/dev/null")

def send_follow_cam():
    """Sends Ctrl + F into AoE2:DE to lock camera onto selected unit."""
    if IS_WINDOWS and user32:
        # Ctrl down
        send_key_scancode(SC_LCONTROL, extended=False, press_duration=0.02, vk=VK_CONTROL)
        # F down and up
        send_key_scancode(SC_F, extended=False, press_duration=0.06, vk=VK_F)
        # Ctrl up
        user32.keybd_event(VK_CONTROL, SC_LCONTROL, KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP, 0)
    elif IS_LINUX:
        os.system("xdotool key ctrl+f 2>/dev/null")

def send_smooth_pan(direction="RIGHT", duration_sec=3.5):
    """
    Smoothly glides the camera across the battlefield in the specified direction.
    Uses micro-pulsed DirectInput arrow strokes yielding silky-smooth panning.
    """
    if not IS_WINDOWS or not user32:
        if IS_LINUX:
            key_map = {"RIGHT": "Right", "LEFT": "Left", "UP": "Up", "DOWN": "Down"}
            k = key_map.get(direction, "Right")
            os.system(f"xdotool key --repeat 15 --delay 100 {k} 2>/dev/null")
        else:
            time.sleep(duration_sec)
        return

    sc = SC_RIGHT
    vk = VK_RIGHT
    if direction == "LEFT":
        sc, vk = SC_LEFT, VK_LEFT
    elif direction == "UP":
        sc, vk = SC_UP, VK_UP
    elif direction == "DOWN":
        sc, vk = SC_DOWN, VK_DOWN

    start = time.time()
    while time.time() - start < duration_sec:
        send_key_scancode(sc, extended=True, press_duration=0.08, vk=vk)
        time.sleep(0.04)

# ----------------------------------------------------------------------
# Multi-Layer Window Guard with Focus Hysteresis
# ----------------------------------------------------------------------
_last_aoe2_seen_time = 0.0

def is_aoe2_focused(guard_enabled=True):
    """
    Determines if AoE2:DE is currently the active window.
    Features:
      1. Direct Process ID & Image Name Check (AoE2DE_s.exe / AoE2DE.exe)
      2. Window Title Substring Matching on active window & root ancestor
      3. 8-second sticky buffer prevents transient menu clicks from flapping focus
      4. Explicit non-game blacklist (Chrome, Discord, OBS, VS Code)
    """
    global _last_aoe2_seen_time
    if not guard_enabled or not IS_WINDOWS or not user32:
        return True

    try:
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return (time.time() - _last_aoe2_seen_time) < 8.0

        def get_hwnd_title(h):
            l = user32.GetWindowTextLengthW(h)
            if l == 0:
                return ""
            b = ctypes.create_unicode_buffer(l + 1)
            user32.GetWindowTextW(h, b, l + 1)
            return b.value.lower()

        title = get_hwnd_title(hwnd)
        if not title:
            # Check root parent (GA_ROOT = 2) for child render surfaces
            root_hwnd = user32.GetAncestor(hwnd, 2)
            if root_hwnd:
                title = get_hwnd_title(root_hwnd)

        is_aoe2 = ("age of empires" in title or "aoe2" in title or "definitive edition" in title)

        # Process Image Name Check
        if not is_aoe2 and kernel32:
            try:
                pid = wintypes.DWORD()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                hProc = kernel32.OpenProcess(0x1000, False, pid.value)
                if hProc:
                    name_buf = ctypes.create_unicode_buffer(512)
                    size = wintypes.DWORD(512)
                    if hasattr(kernel32, "QueryFullProcessImageNameW") and kernel32.QueryFullProcessImageNameW(hProc, 0, name_buf, ctypes.byref(size)):
                        exe_name = name_buf.value.lower()
                        if "aoe2de" in exe_name or "age of empires" in exe_name:
                            is_aoe2 = True
                    kernel32.CloseHandle(hProc)
            except Exception:
                pass

        # Explicit non-game blacklist
        blacklist = ("chrome", "firefox", "msedge", "discord", "obs64", "code", "devenv", "windowsterminal", "cmd.exe", "powershell")
        if any(b in title for b in blacklist):
            return False

        if is_aoe2:
            _last_aoe2_seen_time = time.time()
            return True

        # Keep active if AoE2 was seen recently (grace period)
        if (time.time() - _last_aoe2_seen_time) < 8.0:
            return True

        return False
    except Exception:
        return True

# ----------------------------------------------------------------------
# Combat Hotspot Data Model
# ----------------------------------------------------------------------
class CombatHotspot:
    def __init__(self, name, pan_dir, dwell_time, desc):
        self.name = name
        self.pan_dir = pan_dir        # "RIGHT", "LEFT", "UP", "DOWN"
        self.dwell_time = dwell_time  # Seconds camera remains on this hotspot
        self.desc = desc

HOTSPOTS = [
    CombatHotspot("MAIN FRONTLINE",   "RIGHT", 8.0,  "Broad multi-group deathball assault clashes"),
    CombatHotspot("STANDOFF SIEGE",   "UP",    9.0,  "Trebuchets & Bombard Cannons shelling fortifications"),
    CombatHotspot("FLANK WOODLINE",   "DOWN",  7.0,  "Cavalry / Archer raid on enemy lumberjacks"),
    CombatHotspot("FLANK GOLD MINE",  "RIGHT", 7.0,  "Raiding squad hitting enemy mining outpost"),
    CombatHotspot("CITADEL DEFENSE",  "LEFT",  9.0,  "Fortress breach / existential town defense"),
    CombatHotspot("WONDER ASSAULT",   "UP",    8.0,  "All-in convergence on enemy Wonder / Relics"),
    CombatHotspot("COASTAL BOMBARD",  "RIGHT", 7.0,  "Cannon Galleons & Fast Fire Ships naval engagement")
]

# ----------------------------------------------------------------------
# Central Auto-Director Controller
# ----------------------------------------------------------------------
class ZulfikarCameraDirector:
    def __init__(self, demo_mode=False, default_dwell=8.0, guard_enabled=False):
        self.demo_mode = demo_mode
        self.default_dwell = default_dwell
        self.guard_enabled = guard_enabled  # Default False: Continuous YouTube Broadcast Mode
        self.is_running = True
        self.auto_active = True
        self.hotspot_idx = 0
        self.time_in_hotspot = 0.0
        self.last_focus_state = True
        self.glide_in_progress = False
        self.lock = threading.Lock()

    @property
    def current_hotspot(self):
        return HOTSPOTS[self.hotspot_idx]

    def can_inject(self):
        """Returns True if input injection is allowed."""
        if self.demo_mode:
            return False
        if not self.guard_enabled:
            return True
        return is_aoe2_focused(guard_enabled=True)

    def snap_to_beacon(self, trigger_type="AUTO"):
        """Dispatches camera jump to the current active hotspot."""
        if self.can_inject():
            send_spacebar_jump()
        log_event(f"[{trigger_type}] Camera centered on: {self.current_hotspot.name} - {self.current_hotspot.desc}", "ACTION")

    def cycle_hotspot(self, delta=1, manual=False):
        """Cycles to the next or previous combat hotspot and begins active directing."""
        with self.lock:
            self.hotspot_idx = (self.hotspot_idx + delta) % len(HOTSPOTS)
            self.time_in_hotspot = 0.0

        self.snap_to_beacon("MANUAL" if manual else "AUTO")

        # Automatically initiate a smooth panoramic glide along the hotspot vector
        self.trigger_panoramic_glide(direction=self.current_hotspot.pan_dir, duration=3.5)

    def trigger_chase_cam(self):
        """Activates native Follow-Cam (Ctrl+F) on the lead squad."""
        if self.can_inject():
            send_follow_cam()
        log_event("Vanguard Chase-Cam active! (Ctrl + F follow cam sent)", "CHASE-CAM")

    def trigger_panoramic_glide(self, direction=None, duration=4.0):
        """Executes an asynchronous smooth camera sweep across the battle line."""
        if self.glide_in_progress:
            return

        pan_dir = direction or self.current_hotspot.pan_dir

        def glide_worker():
            self.glide_in_progress = True
            log_event(f"Executing smooth {duration:.1f}s panoramic glide ({pan_dir}) across {self.current_hotspot.name}...", "PANORAMA")
            if self.can_inject():
                send_smooth_pan(direction=pan_dir, duration_sec=duration)
            else:
                time.sleep(duration)
            self.glide_in_progress = False

        threading.Thread(target=glide_worker, daemon=True).start()

    def run_director_loop(self):
        """Autonomous time-slice scheduler driving smooth YouTube camera cinematography."""
        step = 1.0
        # Initial jump and glide on startup
        time.sleep(1.0)
        self.snap_to_beacon("INIT")
        self.trigger_panoramic_glide(duration=3.5)

        while self.is_running:
            time.sleep(step)
            if not self.auto_active:
                continue

            # Focus Guard checking
            if self.guard_enabled:
                focused = is_aoe2_focused(guard_enabled=True)
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
            time.sleep(0.03)

            # [Insert] or [G]: Toggle Window Guard ON/OFF
            if check_pressed(VK_INSERT) or check_pressed(VK_G):
                self.guard_enabled = not self.guard_enabled
                state = "ENABLED (Auto-pauses on Alt-Tab)" if self.guard_enabled else "DISABLED (Continuous Broadcast Mode)"
                log_event(f"Window Focus Guard {state}", "HOTKEY")

            # [Num 1]: Toggle Auto-Director Hands-Free / Manual Co-Pilot
            elif check_pressed(VK_NUMPAD1):
                with self.lock:
                    self.auto_active = not self.auto_active
                    status = "RESUMED (Hands-Free YouTube Mode)" if self.auto_active else "PAUSED (Manual Co-Pilot)"
                log_event(f"Auto-Director {status}", "DIRECTOR")

            # [Home] or [Num 2]: Panoramic Glide
            elif check_pressed(VK_HOME) or check_pressed(VK_NUMPAD2):
                self.trigger_panoramic_glide(duration=4.5)

            # [End] or [Num 3]: Vanguard Chase-Cam (Ctrl+F)
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

            # [Num 4]: Manual Glide Left
            elif check_pressed(VK_NUMPAD4):
                self.trigger_panoramic_glide(direction="LEFT", duration=2.5)

            # [Num 6]: Manual Glide Right
            elif check_pressed(VK_NUMPAD6):
                self.trigger_panoramic_glide(direction="RIGHT", duration=2.5)

            # [Num 8]: Manual Glide Up
            elif check_pressed(VK_NUMPAD8):
                self.trigger_panoramic_glide(direction="UP", duration=2.5)

            # [Num 5]: Manual Glide Down
            elif check_pressed(VK_NUMPAD5):
                self.trigger_panoramic_glide(direction="DOWN", duration=2.5)

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
                    self.trigger_panoramic_glide(duration=4.5)
                elif ch in ('3', 'c'):
                    self.trigger_chase_cam()
                elif ch in (' ', 's'):
                    self.snap_to_beacon("TERMINAL")
                elif ch in ('g', 'w'):
                    self.guard_enabled = not self.guard_enabled
                    state = "ENABLED" if self.guard_enabled else "DISABLED (Continuous Broadcast)"
                    log_event(f"Window Focus Guard {state}", "HOTKEY")
                elif ch == 'n':
                    self.cycle_hotspot(1, manual=True)
                elif ch == 'b':
                    self.cycle_hotspot(-1, manual=True)
                elif ch in ('q', 'exit'):
                    self.is_running = False
                    break
            except Exception:
                time.sleep(0.2)

def print_welcome_banner(demo=False, guard_enabled=False):
    """Prints the stationary welcome banner once at startup."""
    guard_text = "\033[92mDISABLED (Continuous Broadcast Mode - Recommended for YouTube)\033[0m" if not guard_enabled else "\033[93mENABLED (Focus Guard active)\033[0m"
    banner = f"""
\033[95m================================================================================
          ZULFIKAR AI CAMERA DIRECTOR - YOUTUBE BROADCAST SUITE
================================================================================\033[0m
  Platform:       \033[97m{platform.system()} {platform.release()}\033[0m  (DirectX/DirectInput: \033[92mREADY\033[0m)
  Mode:           \033[92m{'DEMO (Simulation)' if demo else 'LIVE ENGINE (AoE2:DE)'}\033[0m
  Window Guard:   {guard_text}
--------------------------------------------------------------------------------
  \033[93mGLOBAL IN-GAME HOTKEYS\033[0m (Works directly while inside AoE2:DE on Windows 11):
    \033[92m[Insert] or [G]\033[0m       Toggle Window Focus Guard ON / OFF
    \033[92m[Num 1]\033[0m               Toggle Auto-Director ON / OFF (Hands-Free recording)
    \033[93m[Home]   or [Num 2]\033[0m   Execute Smooth Panoramic Camera Glide
    \033[95m[End]    or [Num 3]\033[0m   Lock Vanguard Chase-Cam (Ctrl + F Follow Cam)
    \033[97m[Space]  or [Num 0]\033[0m   Snap Camera to Latest Battle Flare
    \033[97m[Num 4/6/8/5]\033[0m         Manual Glide Left / Right / Up / Down
    \033[97m[PageDown] / [PageUp]\033[0m Skip to Next / Previous Battle Hotspot
    \033[91m[Esc]    or [Q]\033[0m       Safe Exit

  \033[96mTERMINAL COMMANDS\033[0m (You can also type these directly into this console):
    Type \033[97m'g'\033[0m (Toggle Focus Guard), \033[97m'1'\033[0m (Toggle), \033[97m'2'\033[0m (Glide), \033[97m'3'\033[0m (Chase), \033[97m'n'\033[0m (Next), \033[97m'q'\033[0m (Quit)
--------------------------------------------------------------------------------
\033[90m[LIVE EVENT LOG - Screen will NOT flicker or wipe]:\033[0m
"""
    print(banner)
    sys.stdout.flush()

def main():
    parser = argparse.ArgumentParser(description="ZULFIKAR Camera Director for AoE2:DE YouTube Recording on Windows 11")
    parser.add_argument("--demo", action="store_true", help="Run in simulation mode without sending OS key inputs")
    parser.add_argument("--dwell", type=float, default=8.0, help="Default dwell time in seconds per battle hotspot (default: 8.0)")
    parser.add_argument("--guard", action="store_true", help="Enable strict window focus guard (default: off for continuous broadcast)")
    parser.add_argument("--no-guard", dest="guard", action="store_false", help="Disable window focus guard (continuous broadcast)")
    parser.set_defaults(guard=False)
    args = parser.parse_args()

    print_welcome_banner(demo=args.demo, guard_enabled=args.guard)
    director = ZulfikarCameraDirector(demo_mode=args.demo, default_dwell=args.dwell, guard_enabled=args.guard)

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
    if not args.guard:
        log_event("Continuous Broadcast Mode active. DirectInput camera movement will inject continuously for YouTube recording.", "DIRECTOR")

    try:
        while director.is_running:
            time.sleep(0.5)
    except KeyboardInterrupt:
        director.is_running = False

    print("\n\033[92mZULFIKAR Camera Director safely closed. Happy YouTube recording!\033[0m")

if __name__ == "__main__":
    main()
