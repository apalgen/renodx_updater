# RenoDX Auto-Updater

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.14%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%2011-lightgrey)

A lightweight, portable Python watchdog designed to automatically keep [RenoDX](https://github.com/clshortfuse/renodx) mods up to date.

> [!IMPORTANT]
> **Roadmap:** This application is currently optimized specifically for [**Crimson Desert**](https://store.steampowered.com/app/3321460/Crimson_Desert) on Steam. However, the architecture is designed to be modular. Expanding support for other RenoDX-supported titles is easily achievable and is officially on the project roadmap.

---

## 🚀 Quick Start (End-Users)

1. **Download:** Get the latest `RenoDX-Updater_vX.X.X_windows_x64.exe` from the [Releases](../../releases) page.
2. **Run:** Simply double-click the `.exe`. The app starts silently in your System Tray (bottom right).
3. **Usage:**
   - **Green Icon:** A new mod version was successfully installed within the last 24 hours.
   - **Grey Icon:** The mod is already up to date or the app is performing a routine check.
   - **Left-Click:** Manually trigger an update check and show the last update timestamp.
   - **Right-Click:** Open the menu to quit the application.
4. **Autostart:**
   - Press `Win + R`, type `shell:startup`, and press Enter.
   - Move the downloaded `.exe` into this folder.
   - **Pro Tip:** Rename the file to `RenoDX-Updater.exe` **before** you move it to the `shell:startup` folder. This makes future updates easier as you only need to overwrite the existing file. Ensure only **one** updater file is present in this folder.

---

## ⚠️ Important: Pre-requisites & Setup

This application is an **Auto-Updater**, not a full installer. It only automates the update process of the `renodx-crimsondesert.addon64` snapshot file.

**You must perform the initial setup manually first:**
1. Follow the **official instructions** for the RenoDX mod: [Crimson Desert Mod Discussion](https://github.com/clshortfuse/renodx/discussions/535).
2. You **must** have ReShade (with Add-on Support) correctly installed and configured, as RenoDX relies on it.
3. Once the initial setup is complete and the mod is working, this updater will handle all future updates of the addon file automatically.

---

## 🛠 Features
* **Automated Background Updates:** Monitors the latest RenoDX mod snapshots every 10 minutes.
* **Smart Steam Path Detection:** Automatically resolves the game directory using Windows Registry and Steam library configurations.
* **Conflict Prevention:** Monitors active processes (e.g., `CrimsonDesert.exe`) and pauses updates while the game is running to ensure file integrity.
* **Native Integration:** Uses Windows 11-style icons and native Toast notifications for status updates.

---

## 📂 Project Structure
```text
renodx_updater/
├── .vscode/               
│   ├── extensions.json    # VS Code extension recommendations
│   └── settings.json      # Workspace formatting rules (Ruff)
├── scripts/
│   └── bundle_project.py  # Utility to bundle project files for review
├── .gitignore             # Excludes venv, build artifacts, and cache
├── LICENSE                # MIT License
├── README.md              # Project documentation
├── renodx_updater.py      # Core application source code
└── requirements.txt       # Python dependencies with pinned versions
```

---

## 💻 Development Environment
This project was developed and tested under the following environment:
* **OS:** Windows 11
* **IDE:** Visual Studio Code
* **Shell:** PowerShell 7
* **Language:** Python 3.14+

### Setup & Installation
1. **Clone & Environment:**
   ```powershell
   git clone git@github.com:apalgen/renodx_updater.git
   cd renodx_updater
   python -m venv .venv
   ```
2. **Activation (PowerShell 7):**
   ```powershell
   .\.venv\Scripts\activate
   ```
3. **Dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

### Building the Portable Executable
To generate the standalone `.exe` for distribution, use the following PyInstaller command:
```powershell
pyinstaller --onefile --noconsole --name "RenoDX-Updater_v1.0.0_windows_x64" renodx_updater.py
```

---

## 🧪 Testing the "Game Running" Logic
To verify the process detection without launching the actual game:
1. Open `renodx_updater.py` and locate the `is_game_running()` function.
2. Temporarily change `'crimsondesert.exe'` to an active process like `'code.exe'` (VS Code).
3. Run the script (`python renodx_updater.py`) and trigger a manual check via the tray icon.
4. **Revert the change** back to `'crimsondesert.exe'` before building the final executable.

---

## 🤝 Credits & Acknowledgments
Special thanks go to the author and everyone involved with **RenoDX** for their excellent work.
* **RenoDX Repository:** [clshortfuse/renodx](https://github.com/clshortfuse/renodx)
* **Crimson Desert Discussion:** [Mod Discussion](https://github.com/clshortfuse/renodx/discussions/535)

---

## 📜 License
This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
