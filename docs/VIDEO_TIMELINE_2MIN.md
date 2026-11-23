# ⏱️ Under 2-Minute Silent Video Walkthrough (Non-Voiceovered)
## Intelligent Web Scraping & AI-Powered Data Intelligence Platform

**Total Duration**: ~1 Minute 50 Seconds  
**Format**: Non-voiceovered screen recording (Terminal only or Terminal + Code Editor)  
**Music**: Optional low-fi or corporate upbeat background track  

---

## 🎬 Pre-Recording Setup (10 Seconds)
1. Open PowerShell or Command Prompt at `E:\IntelligentWebCrawler`.
2. Set terminal font size to **14 or 16** (so text and character art are crisp on mobile and 1080p).
3. Maximize terminal window.

---

## ⏱️ Exact Video Timeline & Actions

### 📍 [0:00 – 0:25] Scene 1: The Main TUI Dashboard
- **Action**: In the terminal, type and press Enter:
  ```powershell
  .\run.bat
  # (or .\run.ps1 in PowerShell)
  ```
- **What Shows on Screen**:
  - Giant gradient ASCII art banner (**FRONTIER ATLAS**).
  - 4-card neon system status dashboard:
    - 🟢 `ONLINE` Platform Status
    - 🔵 `SQLite` Storage Engine
    - 🟣 `Gemini→Groq→Mock` LLM Chain
    - 🟡 `24h Strict` Freshness Policy
  - Double-bordered platform navigation menu with numbered options.
- *Pause for 5 seconds so viewers admire the character art and status.*

---

### 📍 [0:25 – 0:50] Scene 2: System Architecture Diagram
- **Action**: Type `8` and press Enter to select **"View System Architecture"**.
- **What Shows on Screen**:
  - Full ASCII flow diagram detailing the complete 6-stage lifecycle:
    - Sources (YC, arXiv, TechCrunch)
    - 🕷️ Two-Tier Adaptive Fetcher (`aiohttp` ➔ `Playwright`)
    - 🧹 DOM Sanitizer & HTTP 413 Chunker
    - 🤖 Multi-Provider LLM Fallback (Gemini ➔ Groq ➔ DeepSeek ➔ Mock)
    - 🛡️ Validation & 24h Freshness Filter
    - 💾 6-Tab Google Sheets & CSV Persistence
- *Pause for 6 seconds to let viewers scan the flow.*

---

### 📍 [0:50 – 1:15] Scene 3: Deterministic Entity Resolution
- **Action**: Press Enter to return to menu, type `3` (Entity Resolution Explorer), then at the prompt type:
  ```text
  Open AI Inc
  ```
  *(Press Enter to view the card, then press Enter with empty string to return).*
- **What Shows on Screen**:
  - Seed startup demonstration table (50 AI Startups, noise removal, aliases).
  - Glowing double-bordered **Entity Resolution Card**:
    - Raw Input: `Open AI Inc`
    - Canonical: `OpenAI`
    - Match Type: `⟳ Normalized / Alias Match`
    - Status: `🟢 Registered Seed Startup`

---

### 📍 [1:15 – 1:35] Scene 4: 6-Tab Data Intelligence Explorer
- **Action**: Type `4` (Inspect Data Records), then type `A` (Overview of All Tabs).
- **What Shows on Screen**:
  - Clean table displaying the 6 Google Sheets tabs:
    - Tab 1: Startups
    - Tab 2: Products
    - Tab 3: Research Papers
    - Tab 4: Jobs
    - Tab 5: News
    - Tab 6: Entity Mapping Log
  - Shows record counts, file paths in `data/processed/`, and status badges.

---

### 📍 [1:35 – 1:50] Scene 5: Platform Diagnostics & 100% Pass
- **Action**: Press Enter to return to menu, type `7` (Run Platform Diagnostics).
- **What Shows on Screen**:
  - Animated spinner while running all 30 tests.
  - Component Health Matrix table with 7 components (Date Detector, Entity Resolver, HTML Parser, URL Frontier, Chunker, Storage, E2E Pipeline) all marked `✓ PASS`.
  - Giant green framed banner:
    ```
    ╔══════════════════════════════════════════════════════╗
    ║   ✅  ALL 30 TESTS PASSED  ·  0 FAILURES            ║
    ║   System integrity verified across FR-01 → FR-17    ║
    ╚══════════════════════════════════════════════════════╝
    ```
- *End recording on this final winning shot!*

---

## ⚡ Quick Command Cheat Sheet (For Non-Interactive Recording)
If you prefer recording single quick commands one after another instead of the menu:

```powershell
# 1. Show banner & architecture
.\run.bat --arch

# 2. Show entity resolution result card
.\run.bat --resolve "Open AI Inc"

# 3. Show 6-tab data overview
.\run.bat --view A

# 4. Show 100% pass test suite
.\run.bat --test
```
