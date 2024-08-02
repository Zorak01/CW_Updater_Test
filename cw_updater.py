import bpy
import requests
import zipfile
import os
import shutil
from pathlib import Path
import importlib

# Dynamically import the __init__.py module of the addon
addon_main = importlib.import_module(__package__)

# Define the URL of your GitHub repository and the path to the zip file
GITHUB_REPO_URL = "https://github.com/Zorak01/CW_Updater_Test"
GITHUB_ZIP_URL = GITHUB_REPO_URL + "/archive/refs/heads/main.zip"
ADDON_DIR = Path(__file__).parent

def check_for_updates():
    # Get the current version of the addon from bl_info
    current_version = addon_main.bl_info['version']
    latest_version = get_latest_version()

    if current_version < latest_version:
        download_and_install_update()
        bpy.ops.wm.restart_blender('INVOKE_DEFAULT')
        print(f"Addon updated to version {latest_version}. Please restart Blender.")
    else:
        print("Addon is up-to-date.")

def get_latest_version():
    # Placeholder for the latest version, you can improve this by fetching the version dynamically
    return (1, 7, 7)  # Example of a newer version

def download_and_install_update():
    # Download the latest version from GitHub
    response = requests.get(GITHUB_ZIP_URL)
    zip_path = ADDON_DIR / "update.zip"

    with open(zip_path, 'wb') as f:
        f.write(response.content)

    # Extract the zip file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(ADDON_DIR.parent)

    # Replace old files with new ones
    extracted_folder = ADDON_DIR.parent / "CW_Updater_Test-main"
    for item in extracted_folder.iterdir():
        s = extracted_folder / item.name
        d = ADDON_DIR / item.name

        if d.exists():
            if d.is_dir():
                shutil.rmtree(d)
            else:
                d.unlink()

        shutil.move(str(s), str(d))

    # Cleanup
    shutil.rmtree(extracted_folder)
    zip_path.unlink()
