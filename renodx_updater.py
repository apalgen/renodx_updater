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
    """Checks if the game is currently running to avoid file access conflicts."""
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
        return None  # Skip update if game is active

    target_dir = get_steam_game_path()
    if not os.path.exists(target_dir):
        return None  # Game folder not found

    target_file = os.path.join(target_dir, MOD_FILENAME)

    try:
        req = requests.get(MOD_URL, timeout=15)
        if req.status_code == 200:
            new_content = req.content

            # Check if file exists and content is identical
            if os.path.exists(target_file):
                with open(target_file, "rb") as f:
                    old_content = f.read()
                if old_content == new_content:
                    return False  # No update needed

            # Write new mod file
            with open(target_file, "wb") as f:
                f.write(new_content)
            return True  # Update successful
    except Exception:
        return None  # Network or file system error
    return False


def create_icon_image(is_green=False):
    """Generates a simple, Windows 11 matching tray icon."""
    image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Color scheme: Win11 Dark Gray for Normal, Green for "Recently updated"
    color = (46, 204, 113, 255) if is_green else (180, 180, 180, 255)

    # Draws a clean circle
    draw.ellipse((8, 8, 56, 56), fill=color)
    # Small inner hole for a "ring" look
    draw.ellipse((20, 20, 44, 44), fill=(0, 0, 0, 0))

    return image


def set_icon_state(icon, state):
    """Updates the icon color state globally and visually."""
    global icon_state_green
    icon_state_green = state
    icon.icon = create_icon_image(is_green=state)


def get_last_update_string():
    """Returns the formatted timestamp (YYYY-MM-DD HH:MM) of the last update or file modification."""
    if last_update_time > 0:
        # Use timestamp from the current session if an update occurred
        return time.strftime("%Y-%m-%d %H:%M", time.localtime(last_update_time))

    # Fallback: Read the actual file modification time if the app just started
    target_dir = get_steam_game_path()
    target_file = os.path.join(target_dir, MOD_FILENAME)
    if os.path.exists(target_file):
        mtime = os.path.getmtime(target_file)
        return time.strftime("%Y-%m-%d %H:%M", time.localtime(mtime))

    return "Unknown"


def manual_check(icon, item):
    """Executed when the user clicks 'Check now' or left-clicks the icon."""
    global last_update_time
    result = check_and_update()

    if result is True:
        last_update_time = time.time()
        set_icon_state(icon, True)
        time_str = get_last_update_string()
        # Trigger native Windows notification for a successful update
        icon.notify(
            f"Mod successfully updated!\nLast Update: {time_str}", "RenoDX Auto-Updater"
        )

    elif result is False:
        set_icon_state(icon, False)  # Reset to gray if already up to date
        time_str = get_last_update_string()
        # Trigger native Windows notification stating no update was needed
        icon.notify(
            f"No new updates available.\nLast Update: {time_str}", "RenoDX Auto-Updater"
        )

    elif result is None:
        # Trigger native Windows warning notification
        icon.notify(
            "Update skipped.\nGame is currently running or path not found.",
            "RenoDX Auto-Updater",
        )


def quit_app(icon, item):
    """Quits the application cleanly by stopping the background loop."""
    global run_flag
    run_flag = False
    icon.stop()


def background_loop(icon):
    """The main loop that checks for updates periodically in the background."""
    global last_update_time

    # Initial check on startup
    if check_and_update() is True:
        last_update_time = time.time()
        set_icon_state(icon, True)

    while run_flag:
        # Wait in 1-second steps to allow immediate shutdown when quit_app is called
        for _ in range(CHECK_INTERVAL):
            if not run_flag:
                break
            time.sleep(1)

        if not run_flag:
            break

        # Periodic update check
        result = check_and_update()
        if result is True:
            last_update_time = time.time()
            set_icon_state(icon, True)

        # Revert icon to gray if the green duration (24h) has passed
        if icon_state_green and (time.time() - last_update_time > GREEN_DURATION):
            set_icon_state(icon, False)


def main():
    # Setup context menu for the system tray icon
    menu = pystray.Menu(
        # default=True binds the left-click/double-click action to this item
        pystray.MenuItem("Check now (Update)", manual_check, default=True),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", quit_app),
    )

    # Initialize the system tray icon
    icon = pystray.Icon(
        "RenoDXUpdater",
        create_icon_image(icon_state_green),
        "RenoDX Auto-Updater",
        menu=menu,
    )

    # Start the periodic background check in a separate daemon thread
    bg_thread = threading.Thread(target=background_loop, args=(icon,), daemon=True)
    bg_thread.start()

    # Run the icon event loop (this blocks the main thread)
    icon.run()


if __name__ == "__main__":
    main()
