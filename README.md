# RenoDX Auto-Updater

A lightweight, portable Python watchdog that automatically updates RenoDX HDR mods in the background. Currently optimized for Crimson Desert, with plans to expand support for additional games.

## Features
* **Automated Updates:** Checks for the latest RenoDX mod snapshot at regular intervals (default: every 10 minutes) and downloads it automatically.
* **Smart Steam Path Detection:** Automatically locates the game installation path via the Windows Registry and library folders.
* **Safe Execution:** Monitors running processes and pauses updates while the game is running to prevent file conflicts and crashes.
* **System Tray Integration:** Runs silently in the background with a clean, Windows 11-style system tray icon.
* **Visual Feedback:** The tray icon turns green to indicate that an update has been successfully applied within the last 24 hours.

## Requirements
* Windows 10/11
* Python 3.8+ (if running from source)

## Setup for Development
1. Clone the repository:
   ```bash
   git clone git@github.com:apalgen/renodx_updater.git
   cd renodx_updater
