"""All functions NOT related to the browser"""
import os
import shutil
import urllib
import json
from dataclasses import dataclass
from mega import Mega
import psutil
import sys

VERSION = "v1.4.1"
mega = Mega()
clear_attempts = 0

@dataclass
class Colours:
    """Colours for the console."""
    HEADER: str = "\033[95m"
    OKBLUE: str = "\033[94m"
    OKCYAN: str = "\033[96m"
    OKGREEN: str = "\033[92m"
    WARNING: str = "\033[93m"
    FAIL: str = "\033[91m"
    ENDC: str = "\033[0m"


def clear_tmp():
    """Clears tmp folder."""
    global clear_attempts
    if os.path.exists("tmp"):
        try:
            shutil.rmtree("tmp")
            p_print("Cleared tmp folder successfully!", Colours.OKGREEN)
        except PermissionError:
            matches = ["CrashpadMetrics-active.pma",
                       "CrashpadMetrics.pma"]
            p_print(
                "Failed to clear temporary files... killing previous instances.", Colours.FAIL)
            kill_process(matches)
            if clear_attempts >= 1:
                return False
            clear_attempts += 1
            clear_tmp()


def check_for_updates():
    request = urllib.request.urlopen(
        'https://api.github.com/repos/qtchaos/py_mega_account_generator/tags')
    json_data = json.loads(request.read().decode())
    latest_version = json_data[0]['name']
    if latest_version != VERSION:
        p_print(
            f"New version available! Please download it from https://github.com/qtchaos/py_mega_account_generator/releases/tag/{latest_version}", Colours.WARNING)


def delete_default(credentials: dict):
    """Deletes the default welcome file."""
    mega.login(credentials["email"], credentials["password"])
    mega.destroy(mega.find(filename="Welcome to MEGA.pdf")[0])


def reinstall_tenacity():  # sourcery skip: extract-method
    """Reinstalls tenacity because of a dependency problem within the mega.py library."""
    try:
        p_print("Reinstalling tenacity...", Colours.WARNING)
        os.system("python -m pip uninstall tenacity -y")
        os.system("python -m pip install tenacity")
        clear_console()
        p_print("Reinstalled tenacity successfully!", Colours.OKGREEN)
        p_print("Please rerun the program.", Colours.WARNING)
        sys.exit(0)
    except Exception as e:
        p_print("Failed to reinstall tenacity!", Colours.FAIL)
        print(e)
        sys.exit(1)


def kill_process(matches: list):
    """Kills processes."""
    for process in psutil.process_iter():
        try:
            for _ in process.open_files():
                if any(x in _.path for x in matches):
                    p_print(
                        f"Killing process {process.name()}...", Colours.WARNING)
                    process.kill()
        except psutil.AccessDenied:
            continue

    p_print("Killed previous instances successfully!", Colours.OKGREEN)


def p_print(
    text,
    colour=None,
):
    """Prints text in colour."""
    if colour is not None:
        print(colour + text + Colours.ENDC)
    else:
        print(text)


def clear_console():
    """Clears console."""
    os.system("cls" if os.name == "nt" else "clear")
