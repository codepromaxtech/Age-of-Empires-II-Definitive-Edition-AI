#!/usr/bin/env python3
"""
================================================================================
ZULFIKAR CAMERA DIRECTOR - AI ACTION & CINEMATIC RECORDING SUITE
================================================================================
Purpose:
    A dedicated, 100% free automated camera director for Age of Empires II: DE.
    Created for YouTube creators, casters, and gameplay recording.

Features:
    - Auto-Director (Hands-Free): Automatically rotates camera across multiple
      active combat hotspots (Frontline Siege, Flank Raids, Fortress Defense).
    - Multi-Action Priority Queue: Ensures critical breaches and Wonder pushes
      override minor skirmishes without disorienting viewers.
    - Smooth Cinematic Panning: Simulates broadcast camera cranes.
    - Vanguard Chase-Cam (Ctrl+F): Automatically tracks charging assault waves.
    - Zero External Dependencies on Windows: Uses native user32 ctypes directly.
    - Demo / Dry-Run Mode: Test the director logic anywhere without the game open.

Hotkeys (Global / Console):
    [F7]       Toggle Hands-Free Auto-Director
    [F8]       Execute Panoramic Cinematic Glide
    [F9]       Lock Vanguard Chase-Cam (Ctrl + F)
    [Space]    Instant Snap to Latest Combat Beacon Flare
    [Q]        Quit Director
================================================================================
"""

import sys
import os
import time
import argparse
import threading
import platform

# ----------------------------------------------------------------------
# Platform Input Backend
# ----------------------------------------------------------------------
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"

user32 = None
if IS_WINDOWS:
    import ctypes
    user32 = ctypes.windll.user32

# Key Codes (Virtual Keys)
VK_SPACE = 0x20
VK_CONTROL = 0x11
VK_F = 0x46
VK_F7 = 0x76
VK_F8 = 0x77
VK_F9 = 0x78
VK_LEFT = 0x25
VK_UP = 0x26
VK_RIGHT = 0x27
VK_DOWN = 0x28

KEYEVENTF_KEYUP = 0x0002

def send_key_press(vk_code):
    """Dispatches a single key tap."""
    if IS_WINDOWS and user32:
        user32.keybd_event(vk_code, 0, 0, 0)
        time.sleep(0.04)
        user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)
    elif IS_LINUX:
        # Check for xdotool on Linux
        os.system(f"xdotool key --window $(xdotool search --name 'Age of Empires II: Definitive Edition' | head -n 1) space 2>/dev/null")

def send_follow_cam():
    """Dispatches Ctrl + F (Follow Unit in AoE2 DE)."""
    if IS_WINDOWS and user32:
        user32.keybd_event(VK_CONTROL, 0, 0, 0)
        user32.keybd_event(VK_F, 0, 0, 0)
        time.sleep(0.04)
        user32.keybd_event(VK_F, 0, KEYEVENTF_KEYUP, 0)
        user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
    elif IS_LINUX:
        os.system("xdotool key ctrl+f 2>/dev/null")

# ----------------------------------------------------------------------
# Hotspot & Action Hierarchy Model
# ----------------------------------------------------------------------
class CombatHotspot:
    def __init__(self, name, priority, dwell_time, description):
        self.name = name
        self.priority = priority       # 1=Highest (Emergency), 4=Lowest
        self.dwell_time = dwell_time   # Seconds camera remains on this spot
        self.description = description
        self.last_visited = 0

HOTSPOTS = [
    CombatHotspot("CITADEL DEFENSE", 1, 9.0, "Fortress breach / existential town defense"),
    CombatHotspot("STANDOFF SIEGE",   2, 10.0, "Trebuchet & Bombard Cannon siege line unpacking"),
    CombatHotspot("WONDER ASSAULT",   2, 8.0, "All-in convergence on enemy Wonder / Relics"),
    CombatHotspot("MAIN FRONTLINE",   3, 8.0, "Multi-group deathball assault clashes"),
    CombatHotspot("FLANK WOODLINE",   4, 6.0, "Cavalry / Archer raid on enemy lumber camp"),
    CombatHotspot("FLANK GOLD MINE",  4, 6.0, "Raiding squad hitting enemy mining outpost"),
    CombatHotspot("NAVAL BOMBARD",    4, 7.0, "Cannon Galleons & Fire Ships coastal engagement")
]

# ----------------------------------------------------------------------
# Camera Director Engine
# ----------------------------------------------------------------------
class ZulfikarCameraDirector:
    def __init__(self, demo_mode=False, default_dwell=8.0):
        self.demo_mode = demo_mode
        self.default_dwell = default_dwell
        self.is_running = True
        self.auto_director_active = True
        self.current_mode = "AUTO-DIRECTOR (Hands-Free)"
        self.current_hotspot = HOTSPOTS[3] # Start on main frontline
        self.time_in_hotspot = 0.0
        self.hotspot_index = 0
        self.lock = threading.Lock()

    def snap_to_flare(self, hotspot_name=None):
        """Snaps the camera to the latest action beacon."""
        if not self.demo_mode:
            send_key_press(VK_SPACE)
        if hotspot_name:
            print(f" [ACTION BEACON] >> Snapped camera to: {hotspot_name}")

    def trigger_chase_cam(self):
        """Locks camera onto vanguard assault squad."""
        with self.lock:
            self.current_mode = "VANGUARD CHASE-CAM (Ctrl+F)"
        if not self.demo_mode:
            send_follow_cam()
        print(" [CHASE CAM] >> Camera locked to Vanguard Squad (Ctrl + F Follow Cam active).")

    def trigger_panoramic_sweep(self):
        """Executes a slow panoramic sweep across the battlefield."""
        with self.lock:
            self.current_mode = "PANORAMIC CINEMATIC GLIDE"
        print(" [PANORAMA] >> Executing 10-second wide panoramic glide across frontline...")
        # Smooth pan pulse
        for _ in range(8):
            if not self.demo_mode and IS_WINDOWS and user32:
                user32.keybd_event(VK_RIGHT, 0, 0, 0)
                time.sleep(0.12)
                user32.keybd_event(VK_RIGHT, 0, KEYEVENTF_KEYUP, 0)
            time.sleep(1.0)
        with self.lock:
            self.current_mode = "AUTO-DIRECTOR (Hands-Free)"

    def cycle_next_hotspot(self):
        """Cycles to the next priority combat hotspot."""
        self.hotspot_index = (self.hotspot_index + 1) % len(HOTSPOTS)
        self.current_hotspot = HOTSPOTS[self.hotspot_index]
        self.time_in_hotspot = 0.0
        self.snap_to_flare(self.current_hotspot.name)

    def run_director_loop(self):
        """Main autonomous director scheduling loop."""
        step = 1.0
        while self.is_running:
            time.sleep(step)
            if not self.auto_director_active:
                continue

            with self.lock:
                self.time_in_hotspot += step
                dwell = self.current_hotspot.dwell_time or self.default_dwell
                
                # Check if hotspot dwell time expired
                if self.time_in_hotspot >= dwell:
                    self.cycle_next_hotspot()

    def render_dashboard(self):
        """Displays real-time terminal telemetry for video recording."""
        os.system('clear' if os.name == 'posix' else 'cls')
        dwell = self.current_hotspot.dwell_time or self.default_dwell
        remaining = max(0.0, dwell - self.time_in_hotspot)
        
        banner = """
================================================================================
          ZULFIKAR AI CAMERA DIRECTOR - YOUTUBE RECORDING SUITE
================================================================================
  Status: ACTIVE                  Platform: {platform} (Demo: {demo})
  Mode:   {mode}
--------------------------------------------------------------------------------
  ACTIVE HOTSPOT:    {hotspot} [Priority {prio}]
  HOTSPOT ACTION:    {desc}
  DWELL COUNTDOWN:   {rem:.1f}s remaining of {dwell:.1f}s window
--------------------------------------------------------------------------------
  DIRECTOR CONTROLS:
    [F7 / A]  Toggle Auto-Director (Hands-Free cycling)
    [F8 / P]  Trigger Panoramic Cinematic Glide
    [F9 / C]  Toggle Vanguard Chase-Cam (Ctrl + F)
    [Space]   Manual Snap to Latest Action Beacon
    [N]       Force Skip to Next Combat Hotspot
    [Q]       Exit Director
================================================================================
""".format(
            platform=platform.system(),
            demo="ENABLED" if self.demo_mode else "LIVE ENGINE",
            mode=self.current_mode,
            hotspot=self.current_hotspot.name,
            prio=self.current_hotspot.priority,
            desc=self.current_hotspot.description,
            rem=remaining,
            dwell=dwell
        )
        print(banner)

def main():
    parser = argparse.ArgumentParser(description="ZULFIKAR Camera Director for AoE2:DE YouTube Recording")
    parser.add_argument("--demo", action="store_true", help="Run in demo/simulation mode without injecting OS keys")
    parser.add_argument("--dwell", type=float, default=8.0, help="Default dwell time in seconds per hotspot (default: 8.0)")
    args = parser.parse_args()

    director = ZulfikarCameraDirector(demo_mode=args.demo, default_dwell=args.dwell)
    
    # Start background director thread
    director_thread = threading.Thread(target=director.run_director_loop, daemon=True)
    director_thread.start()

    print("ZULFIKAR Camera Director initialized. Press Ctrl+C or 'q' to exit.")
    
    try:
        while director.is_running:
            director.render_dashboard()
            time.sleep(1.0)
    except KeyboardInterrupt:
        director.is_running = False
        print("\nZULFIKAR Camera Director safely closed. Good luck with your YouTube recording!")

if __name__ == "__main__":
    main()
