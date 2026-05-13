import os
import time
import threading
import winreg
import re
import requests
import psutil
import pystray
from PIL import Image, ImageDraw

# Configuration
MOD_URL = "https://oopydoopy.github.io/renodx/renodx-crimsondesert.addon64"
MOD_FILENAME = "renodx-crimsondesert.addon64"
CHECK_INTERVAL = 600  # 10 minutes in seconds
GREEN_DURATION = 86400  # 24 hours in seconds

# State variables
run_flag = True
icon_state_green = False
last_update_time = 0


def get_steam_game_path():
    """Attempts to automatically find the Crimson Desert installation path."""
    try:
        # Read main Steam path from Registry
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
        steam_path, _ = winreg.QueryValueEx(key, "SteamPath")
        winreg.CloseKey(key)

        # Check default path
        default_path = os.path.join(steam_path, "steamapps", "common", "Crimson Desert")
        if os.path.exists(default_path):
            return os.path.normpath(os.path.join(default_path, "bin64"))

        # Check libraryfolders.vdf (if the game is installed on another drive)
        vdf_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
        if os.path.exists(vdf_path):
            with open(vdf_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Search for all library paths
                paths = re.findall(r'"path"\s+"([^"]+)"', content)
                for p in paths:
                    # Windows paths in VDF might contain double backslashes
                    clean_path = p.replace(r"\\\\", "\\").replace(r"\\", "\\")
                    test_path = os.path.join(
                        clean_path, "steamapps", "common", "Crimson Desert"
                    )
                    if os.path.exists(test_path):
                        return os.path.normpath(os.path.join(test_path, "bin64"))
    except Exception:
        pass

    # Last fallback, manually provided path
    return r"C:\Program Files (x86)\Steam\steamapps\common\Crimson Desert\bin64"


def is_game_running():
    """Checks if the game is currently running."""
    for proc in psutil.process_iter(["name"]):
        try:
            if proc.info["name"] and proc.info["name"].lower() == "crimsondesert.exe":
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def check_and_update():
    """
    Downloads the mod file and compares it.
    Returns True (update applied), False (no update needed), or None (error / game running).
    """
    if is_game_running():
        return None

    target_dir = get_steam_game_path()
    if not os.path.exists(target_dir):
        # Folder does not exist (game might not be installed)
        return None

    target_file = os.path.join(target_dir, MOD_FILENAME)

    try:
        req = requests.get(MOD_URL, timeout=15)
        if req.status_code == 200:
            new_content = req.content

            # Check if file exists and is identical
            if os.path.exists(target_file):
                with open(target_file, "rb") as f:
                    old_content = f.read()
                if old_content == new_content:
                    return False  # Files are identical, no update needed

            # Save/overwrite file
            with open(target_file, "wb") as f:
                f.write(new_content)
            return True  # Successfully updated
    except Exception:
        return None
    return False


def create_icon_image(is_green=False):
    """Generates a simple, Windows 11 matching tray icon."""
    image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Color scheme: Win11 Dark Gray for Normal, Green for "Recently updated"
    color = (46, 204, 113, 255) if is_green else (180, 180, 180, 255)

    # Draws a clean circle (classic indicator)
    draw.ellipse((8, 8, 56, 56), fill=color)
    # Small inner hole for a "ring" look
    draw.ellipse((20, 20, 44, 44), fill=(0, 0, 0, 0))

    return image


def set_icon_state(icon, state):
    global icon_state_green
    icon_state_green = state
    icon.icon = create_icon_image(is_green=state)


def manual_check(icon, item):
    """Executed when the user clicks 'Check now' or clicks the icon."""
    global last_update_time
    result = check_and_update()

    if result is True:
        last_update_time = time.time()
        set_icon_state(icon, True)
    elif result is False:
        # On manual check without needed update -> Reset green status
        set_icon_state(icon, False)


def quit_app(icon, item):
    """Quits the application cleanly."""
    global run_flag
    run_flag = False
    icon.stop()


def background_loop(icon):
    """The main loop that checks every 10 minutes in the background."""
    global last_update_time

    # Initial check on startup
    if check_and_update() is True:
        last_update_time = time.time()
        set_icon_state(icon, True)

    while run_flag:
        # Wait in small steps so the app can be quit immediately
        for _ in range(CHECK_INTERVAL):
            if not run_flag:
                break
            time.sleep(1)

        if not run_flag:
            break

        result = check_and_update()
        if result is True:
            last_update_time = time.time()
            set_icon_state(icon, True)

        # Check if 24 hours have passed to turn the icon gray again
        if icon_state_green and (time.time() - last_update_time > GREEN_DURATION):
            set_icon_state(icon, False)


def main():
    # Create menu
    menu = pystray.Menu(
        # default=True triggers this item on double-click (or single click depending on OS)
        pystray.MenuItem("Check now (Update)", manual_check, default=True),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", quit_app),
    )

    # Initialize icon
    icon = pystray.Icon(
        "RenoDXUpdater",
        create_icon_image(icon_state_green),
        "RenoDX Auto-Updater",
        menu=menu,
    )

    # Start background thread
    bg_thread = threading.Thread(target=background_loop, args=(icon,), daemon=True)
    bg_thread.start()

    # Start icon (blocks the main thread)
    icon.run()


if __name__ == "__main__":
    main()
