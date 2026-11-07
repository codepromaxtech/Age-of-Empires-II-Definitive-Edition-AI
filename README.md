# Age-of-Empires-II-Definitive-Edition-AI
# ZULFIKAR (AL-AMIN2.0) - Age of Empires II: Definitive Edition AI

**ZULFIKAR v3.5 (Universal Multi-Style Adaptation Engine)** is a high-level custom AI script for *Age of Empires II: Definitive Edition*. It is engineered to dynamically adjust its strategy, build orders, and army compositions based on **map geometry, map size, game stage, real-time resource banks, and all 45 civilizations** — delivering human-like grandmaster play with 100% fair gameplay (no resource cheats).

---

## Universal Multi-Style Adaptation Features

### 1. Map Geometry & Style Adaptation
- **Open Maps (Arabia, Runestones, Gold Rush, Ghost Lake, Steppe, Valley):**
  - Tight defense, early palisade funnel-walling connecting woodlines, defensive towers on vulnerable resources, and Feudal military skirmishes (Scouts/Archers) to contest map control.
- **Closed / Fortified Maps (Arena, Fortress, Black Forest, Hideout, Michi):**
  - Bypasses unnecessary Feudal military and open palisades to execute a clean **Fast Castle (FC)** build into an immediate 3-TC / 4-TC economic boom.
  - Early Monk deployment to secure all 5 relics while enemies are enclosed.
  - Drops Castles directly on chokepoints and techs into heavy siege (Siege Onagers, Siege Rams).
- **Water & Island Maps (Islands, Team Islands, Migration, Baltic, Mediterranean):**
  - Dark Age Dock placement on shoreline with Fishing Ships to boost food economy by 30–50%.
  - Feudal naval battles (Fire Galleys, Galleys) scaling to Galleons, Fast Fire Ships, and Cannon Galleons.
  - Deploys Transport Ships with ground invasion forces to launch amphibious landings on enemy islands.
- **Nomad Maps (Nomad, Land Nomad, African Clearing):**
  - Detects 0 starting Town Centers: immediately tasks villagers to explore, locate rich wood/food deposits, and erect the primary Town Center with top priority.

### 2. Map Size Scaling (Tiny to Ludikris)
- **Tiny & Small (1v1 / 2–3 Players):** Tightens town perimeter (`sn-maximum-town-size 22`), fast-tracks defensive sentries, and responds rapidly to early rush timings.
- **Medium & Normal:** Standard human macro spacing and dropsite distancing.
- **Large, Huge, Gigantic & Ludikris:** Expands exploration and dropsite radii (`sn-lumber-camp-max-distance 45`, `sn-mining-camp-max-distance 45`), scales maximum town size up to 130 to prevent building placement failures when expanding, and deploys up to 38 Trade Carts to maximize long-distance trade profits.

### 3. Dynamic Real-Time Macro (Resource Feedback Loop)
Instead of relying on rigid, hardcoded percentages, ZULFIKAR continuously monitors its stockpiles:
- **Wood Surplus (>500):** Reallocates gatherers to Food and Gold; accelerates farm seeding.
- **Food Surplus (>1000) & Gold Low (<200):** Increases gold miners and sells surplus food at Market.
- **Gold Surplus (>1200):** Shifts gatherers to Food & Wood to replenish trash units and siege.
- **Castle Age Stone Surge:** Temporarily assigns 18% gatherers to Stone until the 1st Castle is under construction (650 stone), then drops stone allocation back to 5–8% to focus on military resources.
- **Trash War Transition:** When gold mines on the map deplete, shifts gatherers to 50% Food / 42% Wood, flooding the battlefield with Halberdiers, Elite Skirmishers, and Hussars.

### 4. Complete 45-Civilization Mastery & Castle Unique Units
Detects every civilization in AoE2 DE and aligns its army and technology tree:
- **Cavalry Civs:** Franks, Magyars, Berbers, Lithuanians, Huns, Teutons, Persians, Burgundians, Poles, Bulgarians, Cumans, Georgians.
- **Archer Civs:** Britons, Mayans, Ethiopians, Vietnamese, Tatars, Koreans, Italians.
- **Infantry / Siege Civs:** Goths, Celts, Japanese, Romans, Vikings, Slavs, Malians, Armenians.
- **Gunpowder Civs:** Turks, Bohemians, Spanish, Portuguese, Hindustanis.
- **Mesoamerican Civs:** Aztecs, Incas (no Stables — trains lethal Eagle Warriors as mobile strike forces).
- **Camel Civs:** Saracens, Gurjaras, Berbers.
- **Universal Unique Units:** Trains `my-unique-unit-line` at Castles for all civilizations, researching both Unique Technologies and Elite upgrades.

### 5. Tactical Wave Combat & Fair Play
- **Coordinated Wave Attacks:** Paces assaults in synchronized waves (Feudal raids of 8+, Castle pushes of 20+ with siege, Imperial deathballs of 40–80+ with Trebuchets).
- **Intelligent Regrouping:** When army strength drops below safety margins, units fall back to Castles and Town Centers to reinforce before launching the next wave.
- **100% Fair Play:** Completely free of resource cheats (`up-cc-add-resource` removed). Wins through superior scouting, macro, and tactical decision-making.

---

## Installation & Usage

### 1. Locate your AoE2 DE AI Folder
- **For Steam on Linux/Proton:**
  `~/.steam/steam/steamapps/compatdata/813780/pfx/drive_c/users/steamuser/Games/Age of Empires 2 DE/[YourSteamID]/resources/_common/ai/`
- **For Windows:**
  `C:\Users\[YourUsername]\Games\Age of Empires 2 DE\[YourSteamID]\resources\_common\ai\`

### 2. Copy the AI Files
Copy both `ZULFIKAR.ai` and `ZULFIKAR.per` (and optionally `AL-AMIN2.0.ai`) into that folder.

### 3. Launch the Game
1. Start *Age of Empires II: Definitive Edition*.
2. Go to **Single Player** -> **Skirmish**.
3. In the game lobby, click on any Player slot dropdown and select **ZULFIKAR** (or **AL-AMIN2.0**).
4. Start the match and enjoy!

---

## Playing as Player 1 (AI Controlling Your Civ)

- **Method 1: Direct Selection**
  In the Skirmish lobby, set Player 1 from "Human" to **ZULFIKAR**. The AI will play for you from second 1.
- **Method 2: In-Game Switch (Cheats Enabled)**
  Start a match as Human with "Enable Cheats" checked. Press `Ctrl + Shift + F2` to switch to Player 2; the AI will take full control of your civilization (Player 1). Switch back anytime with `Ctrl + Shift + F1`.

***

*Developed by Md. Al-Amin & Google DeepMind Antigravity*
