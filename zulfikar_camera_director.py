#!/usr/bin/env python3
"""
================================================================================
ZULFIKAR CAMERA DIRECTOR - PROFESSIONAL YOUTUBE BROADCAST SUITE
================================================================================
Target Platform: Windows 11 (DirectX 11 / DirectInput Native, Zero Pip Dependencies)
Game: Age of Empires II: Definitive Edition (Live Matches, AI Battles, & Replays)

KEY FIXES & CINEMATIC CAPABILITIES:
  1. Continuous DirectInput Arrow Holding:
     - Holds DirectInput extended arrow keys (Left, Right, Up, Down) down for
       the full duration of each panoramic glide.
     - Works seamlessly with AoE2:DE's natural camera acceleration and inertia,
       producing silky-smooth cinema glides instead of stalled micro-taps.
     - Always releases keys in try...finally blocks so keys never stick.
  2. Synthetic Input Feedback Loop Elimination:
     - Removed Space (' ') from terminal command listeners to prevent synthetic
       Spacebar re-injection storms.
     - Implemented console input buffer flushing (msvcrt.kbhit() drain) so
       spurious or synthetic keystrokes cannot lock up the director.
  3. Safe Global In-Game Hotkeys:
     - Removed in-game letter keys (e.g. 'G' for garrison/gate) from global
       GetAsyncKeyState polling. Focus guard toggle is mapped strictly to [Insert].
     - Added [F9] / 'f' to automatically find and bring the AoE2:DE window to front.
  4. Automatic AoE2:DE Window Focus:
     - On launch and via hotkey, locates the AoE2:DE process window handle, restores
       it if minimized, and brings it to foreground for instant key reception.
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
VK_F9       = 0x78
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
# Window Focus & Foreground Management
# ----------------------------------------------------------------------
def find_aoe2_window():
    """Locates the AoE2:DE game window handle."""
    if not IS_WINDOWS or not user32:
        return None
    aoe2_hwnd = None

    def enum_cb(hwnd, lparam):
        nonlocal aoe2_hwnd
        if not user32.IsWindowVisible(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        if length > 0:
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            title = buf.value.lower()
            if ("age of empires" in title or "aoe2" in title) and "visual studio" not in title:
                aoe2_hwnd = hwnd
                return False  # found, stop enumeration
        return True

    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    cb = WNDENUMPROC(enum_cb)
    user32.EnumWindows(cb, 0)
    return aoe2_hwnd

def bring_aoe2_to_front():
    """Brings AoE2:DE to the foreground so DirectX input is immediately received."""
    hwnd = find_aoe2_window()
    if hwnd and user32:
        try:
            # If minimized, restore it (SW_RESTORE = 9)
            user32.ShowWindow(hwnd, 9)
            user32.SetForegroundWindow(hwnd)
            user32.BringWindowToTop(hwnd)
            return True
        except Exception:
            pass
    return False

# ----------------------------------------------------------------------
# Hardware DirectInput Key Injection Routines
# ----------------------------------------------------------------------
def direct_key_down(scan_code, extended=False, vk=0):
    """Presses and holds a hardware scancode (DirectInput SendInput + keybd_event)."""
    if not IS_WINDOWS or not user32:
        return

    flags = KEYEVENTF_SCANCODE
    if extended:
        flags |= KEYEVENTF_EXTENDEDKEY

    # 1. Primary: Windows 11 SendInput (DirectX DirectInput standard)
    try:
        inp = INPUT()
        inp.type = INPUT_KEYBOARD
        inp.u.ki.wVk = vk
        inp.u.ki.wScan = scan_code
        inp.u.ki.dwFlags = flags
        inp.u.ki.time = 0
        inp.u.ki.dwExtraInfo = 0
        user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
    except Exception:
        pass

    # 2. Secondary fallback: keybd_event
    try:
        user32.keybd_event(vk, scan_code, flags, 0)
    except Exception:
        pass

def direct_key_up(scan_code, extended=False, vk=0):
    """Releases a hardware scancode (DirectInput SendInput + keybd_event)."""
    if not IS_WINDOWS or not user32:
        return

    flags = KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP
    if extended:
        flags |= KEYEVENTF_EXTENDEDKEY

    # 1. Primary: Windows 11 SendInput
    try:
        inp = INPUT()
        inp.type = INPUT_KEYBOARD
        inp.u.ki.wVk = vk
        inp.u.ki.wScan = scan_code
        inp.u.ki.dwFlags = flags
        inp.u.ki.time = 0
        inp.u.ki.dwExtraInfo = 0
        user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
    except Exception:
        pass

    # 2. Secondary fallback: keybd_event
    try:
        user32.keybd_event(vk, scan_code, flags, 0)
    except Exception:
        pass

def send_spacebar_jump():
    """Sends hardware Spacebar tap into AoE2:DE to jump to latest beacon flare."""
    if IS_WINDOWS and user32:
        direct_key_down(SC_SPACE, extended=False, vk=VK_SPACE)
        time.sleep(0.08)
        direct_key_up(SC_SPACE, extended=False, vk=VK_SPACE)
    elif IS_LINUX:
        os.system("xdotool key space 2>/dev/null")

def send_follow_cam():
    """Sends Ctrl + F into AoE2:DE to lock camera onto selected unit."""
    if IS_WINDOWS and user32:
        direct_key_down(SC_LCONTROL, extended=False, vk=VK_CONTROL)
        time.sleep(0.04)
        direct_key_down(SC_F, extended=False, vk=VK_F)
        time.sleep(0.08)
        direct_key_up(SC_F, extended=False, vk=VK_F)
        time.sleep(0.04)
        direct_key_up(SC_LCONTROL, extended=False, vk=VK_CONTROL)
    elif IS_LINUX:
        os.system("xdotool key ctrl+f 2>/dev/null")

def send_smooth_pan(direction="RIGHT", duration_sec=3.5, stop_check_fn=None):
    """
    Smoothly glides the camera across the battlefield in the specified direction.
    Holds the DirectInput extended arrow key continuously for duration_sec,
    enabling AoE2:DE's natural cinematic smooth camera acceleration.
    Guarantees key release in a finally block so keys never stick.
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

    try:
        # Hold key down continuously for cinematic camera acceleration
        direct_key_down(sc, extended=True, vk=vk)
        t_end = time.time() + duration_sec
        while time.time() < t_end:
            if stop_check_fn and stop_check_fn():
                break
            time.sleep(0.05)
    finally:
        # Guarantee key release
        direct_key_up(sc, extended=True, vk=vk)

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
            root_hwnd = user32.GetAncestor(hwnd, 2)
            if root_hwnd:
                title = get_hwnd_title(root_hwnd)

        is_aoe2 = ("age of empires" in title or "aoe2" in title or "definitive edition" in title)

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

        blacklist = ("chrome", "firefox", "msedge", "discord", "obs64", "code", "devenv", "windowsterminal", "cmd.exe", "powershell")
        if any(b in title for b in blacklist):
            return False

        if is_aoe2:
            _last_aoe2_seen_time = time.time()
            return True

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
        self.trigger_panoramic_glide(direction=self.current_hotspot.pan_dir, duration=3.5)

    def trigger_chase_cam(self):
        """Activates native Follow-Cam (Ctrl+F) on the lead squad."""
        if self.can_inject():
            send_follow_cam()
        log_event("Vanguard Chase-Cam active! (Ctrl + F follow cam sent)", "CHASE-CAM")

    def trigger_panoramic_glide(self, direction=None, duration=4.0):
        """Executes an asynchronous smooth camera sweep across the battle line."""
        with self.lock:
            if self.glide_in_progress:
                return
            self.glide_in_progress = True

        pan_dir = direction or self.current_hotspot.pan_dir

        def glide_worker():
            try:
                log_event(f"Executing smooth {duration:.1f}s panoramic glide ({pan_dir}) across {self.current_hotspot.name}...", "PANORAMA")
                if self.can_inject():
                    send_smooth_pan(direction=pan_dir, duration_sec=duration, stop_check_fn=lambda: not self.is_running)
                else:
                    time.sleep(duration)
            finally:
                with self.lock:
                    self.glide_in_progress = False

        threading.Thread(target=glide_worker, daemon=True).start()

    def run_director_loop(self):
        """Autonomous time-slice scheduler driving smooth YouTube camera cinematography."""
        step = 1.0
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
        """Windows 11 Global Hotkey Poller using GetAsyncKeyState (conflict-free)."""
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

            # [Insert]: Toggle Window Guard ON/OFF (clean hotkey, no clash with in-game G)
            if check_pressed(VK_INSERT):
                self.guard_enabled = not self.guard_enabled
                state = "ENABLED (Auto-pauses on Alt-Tab)" if self.guard_enabled else "DISABLED (Continuous Broadcast Mode)"
                log_event(f"Window Focus Guard {state}", "HOTKEY")

            # [F9]: Bring AoE2 Window to Front
            elif check_pressed(VK_F9):
                ok = bring_aoe2_to_front()
                if ok:
                    log_event("AoE2:DE window brought to foreground!", "WINDOW")
                else:
                    log_event("AoE2:DE window not found. Please ensure game is running.", "WARNING")

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

            # [Num 0]: Snap to Flare
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
        """
        Console input listener (type single letters or numbers).
        Flushes buffer after each action to eliminate input storms and echoes.
        """
        while self.is_running:
            try:
                ch = None
                if IS_WINDOWS:
                    if msvcrt.kbhit():
                        ch = msvcrt.getch().decode('utf-8', errors='ignore').lower()
                        # Flush any remaining chars in buffer to prevent input loop storms
                        while msvcrt.kbhit():
                            try:
                                msvcrt.getch()
                            except Exception:
                                break
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
                elif ch in ('s', 'j'):
                    self.snap_to_beacon("TERMINAL")
                elif ch in ('g', 'w'):
                    self.guard_enabled = not self.guard_enabled
                    state = "ENABLED" if self.guard_enabled else "DISABLED (Continuous Broadcast)"
                    log_event(f"Window Focus Guard {state}", "HOTKEY")
                elif ch == 'f':
                    ok = bring_aoe2_to_front()
                    if ok:
                        log_event("AoE2:DE window brought to foreground!", "WINDOW")
                    else:
                        log_event("AoE2:DE window not found. Please ensure game is running.", "WARNING")
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
    \033[92m[Insert]\033[0m              Toggle Window Focus Guard ON / OFF
    \033[92m[F9]\033[0m                  Bring AoE2:DE Game Window to Foreground
    \033[92m[Num 1]\033[0m               Toggle Auto-Director ON / OFF (Hands-Free recording)
    \033[93m[Home]   or [Num 2]\033[0m   Execute Smooth Panoramic Camera Glide
    \033[95m[End]    or [Num 3]\033[0m   Lock Vanguard Chase-Cam (Ctrl + F Follow Cam)
    \033[97m[Num 0]\033[0m               Snap Camera to Latest Battle Flare
    \033[97m[Num 4/6/8/5]\033[0m         Manual Glide Left / Right / Up / Down
    \033[97m[PageDown] / [PageUp]\033[0m Skip to Next / Previous Battle Hotspot
    \033[91m[Esc]    or [Q]\033[0m       Safe Exit

  \033[96mTERMINAL COMMANDS\033[0m (You can also type these directly into this console):
    Type \033[97m'f'\033[0m (Focus AoE2), \033[97m'g'\033[0m (Toggle Guard), \033[97m'1'\033[0m (Toggle), \033[97m'2'\033[0m (Glide),
    \033[97m'3'\033[0m (Chase), \033[97m's'\033[0m (Snap), \033[97m'n'\033[0m (Next), \033[97m'q'\033[0m (Quit)
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

    # Automatically detect and focus AoE2:DE window on startup if available
    if IS_WINDOWS and not args.demo:
        hwnd = find_aoe2_window()
        if hwnd:
            log_event(f"AoE2:DE window detected (HWND: {hex(hwnd)}). Bringing to foreground...", "WINDOW")
            bring_aoe2_to_front()
        else:
            log_event("AoE2:DE window not detected yet. Start the match, or press 'f' in terminal to focus.", "WINDOW")

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
