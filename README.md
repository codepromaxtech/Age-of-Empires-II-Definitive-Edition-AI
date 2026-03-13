# Age-of-Empires-II-Definitive-Edition-AI
# AL-AMIN2.0 - Age of Empires II: Definitive Edition AI

AL-AMIN2.0 is a custom AI script for Age of Empires II: Definitive Edition, designed for a highly defensive, "boom and turtle" playstyle. It focuses on building a beautiful, heavily fortified city and only attacking when provoked.

## Features

- **Strictly Defensive Posture:** The AI will not initiate attacks on other players. It focuses entirely on economy and defense until an enemy breaches its walls or attacks its units/buildings.
- **Beautiful Fortress City:** 
  - Automatically builds a sprawling, well-spaced town expanding to 3-4 Town Centers for a massive economic boom.
  - Constructs defensive walls with Gates (Palisades in Feudal Age, upgrading to Stone Walls & Gates in Castle Age).
  - Builds a comprehensive network of Watch Towers and Castles to secure the perimeter.
- **Smart Retaliatory Counter-Attacks:** Monitors for attacks and unleashes its standby army in three distinct tiers. Small raids are met with a swift 20-unit counter. If a massive army is built up and the town is attacked, it will counter-attack with overwhelming force (80+ units), then intelligently reset its targeting (`up-reset-attack-now`) to return to a defensive posture.
- **Zero Idle Time Economy:** Continuously trains villagers up to a cap of 130, dynamically allocating them to food, wood, gold, and stone based on the current Age. Uses advanced dropsite distancing and actively hunts Boar in the Dark Age.
- **Dynamic Market & Trade System:** Automatically sells off excess resources to generate gold. In emergencies, it will buy stone for castles/towers or buy wood/food to keep production alive. Automatically deploys Trade Carts in the late game for infinite gold.
- **Monks & Relics:** Builds multiple Monasteries, trains up to 8 monks, and actively commands them to scour the map to collect relics for passive gold generation.
- **Complete Tech Tree Mastery:** Automatically researches **all** essential economic upgrades and the *entire* military tech tree for Archery Ranges, Barracks, Stables, Siege Workshops, Universities, and Castles based on the official DE dataset.
- **Age-Scaled Garrison Force:** Maintains a balanced defensive army that scales in size per Age. Features Archers and Hand Cannoneers (to garrison inside towers/castles), Skirmishers, Pikemen, Knights, Hussars, Cavalry Archers, Champions, and a full Siege compliment (Mangonels, Scorpions, Battering Rams, Trebuchets, and Bombard Cannons).

## Installation & Usage

1. **Locate your AI Folder:**
   You need to place the `AL-AMIN2.0.ai` and `AL-AMIN2.0.per` files into your Age of Empires 2 DE `ai` folder.
   
   - **For Steam on Linux/Proton:** The path typically looks like:
     `~/.steam/steam/steamapps/compatdata/813780/pfx/drive_c/users/steamuser/Games/Age of Empires 2 DE/[YourSteamID]/resources/_common/ai/`
   - **For Windows (if transferring):** 
     `C:\Users\[YourUsername]\Games\Age of Empires 2 DE\[YourSteamID]\resources\_common\ai\`

2. **Copy the Files:**
   Copy both `AL-AMIN2.0.ai` and `AL-AMIN2.0.per` into that folder.

3. **Play with the AI:**
   - Start Age of Empires II: Definitive Edition.
   - Go to **Single Player** -> **Skirmish**.
   - In the lobby, click on the **Player** dropdown for an AI slot (or your own Player 1 slot if you want it to play for you).
   - Select **AL-AMIN2.0** from the list of available AIs.
   - Start the game!

## How to Let the AI Play For You (Player 1)

**Method 1: Direct Assignment (Recommended)**
In the Skirmish lobby, look at the Player 1 row. Click the dropdown that says "Human" and change it to "AL-AMIN2.0". The AI will take full control from the start.

**Method 2: Mid-Game Takeover (Requires Cheats)**
Start a game as a Human (ensure "Enable Cheats" is checked in the lobby). Once in-game, press `Ctrl + Shift + F2` to switch control to Player 2. The AI will instantly take over your original civilization (Player 1). You can switch back at any time with `Ctrl + Shift + F1`.

***

*Developed by Google Deepmind Antigravity*
