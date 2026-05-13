"""
Helper Script: Bundles the entire project into a single text file.
Usage from project root: python scripts/bundle_project.py
"""

import os
from pathlib import Path
from datetime import datetime

# Config
SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "build",
    "dist",
    "scripts",  # Ignore the scripts folder itself when bundling
    "dumps",  # Ignore the new dumps folder
}

EXTENSIONS = {".py", ".md", ".txt"}
ALWAYS_INCLUDE = {".gitignore", "requirements.txt", "LICENSE"}

SKIP_FILES = {
    "bundle_project.py",
}


def check_ignore(path):
    for part in path.parts:
        if part in SKIP_DIRS:
            return True
    return False


def bundle_source_files():
    # .parent.parent goes up one level from the 'scripts' folder to the main directory
    root = Path(__file__).parent.parent
    proj_name = root.name
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    fname = f"{proj_name}_dump_{ts}.txt"

    # Create dumps directory if it doesn't exist
    dumps_dir = root / "dumps"
    dumps_dir.mkdir(exist_ok=True)

    # Set output path to the dumps directory
    out_path = dumps_dir / fname

    with open(out_path, "w", encoding="utf-8") as out:
        out.write("=== PROJECT DUMP ===\n")
        out.write(f"Project: {proj_name}\n")
        out.write(f"Root: {root}\n")
        out.write(f"Generated: {ts}\n\n")

        for dirpath, dirs, files in os.walk(root):
            # Filter directories in-place
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

            for file in files:
                # Skip self and previous dumps (just in case they are somewhere else)
                if file == fname or ("_dump_" in file and file.endswith(".txt")):
                    continue

                if file in SKIP_FILES:
                    continue

                f_path = Path(dirpath) / file

                # Check inclusion rules
                is_named = file in ALWAYS_INCLUDE
                is_ext = f_path.suffix in EXTENSIONS

                if not (is_named or is_ext):
                    continue

                rel_path = f_path.relative_to(root)
                if check_ignore(rel_path):
                    continue

                # Write content
                out.write(f"\n{'=' * 60}\n")
                out.write(f"FILE: {rel_path}\n")
                out.write(f"{'=' * 60}\n")

                try:
                    with open(f_path, "r", encoding="utf-8") as f:
                        out.write(f.read())
                    out.write("\n")
                except Exception as e:
                    out.write(f"[Error reading file: {e}]\n")

    print(f"✅ Bundled: {out_path.name}")
    print(f"📂 Path: {out_path}")


if __name__ == "__main__":
    bundle_source_files()
