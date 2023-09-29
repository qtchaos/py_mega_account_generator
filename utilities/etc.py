"""All functions NOT related to the browser"""
import os
import shutil
import urllib
import json
from dataclasses import dataclass

import psutil

VERSION = "1.2.0"


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

            clear_tmp()


def check_for_updates():
    request = urllib.request.urlopen(
        'https://api.github.com/repos/qtchaos/py_mega_account_generator/tags')
    json_data = json.loads(request.read().decode())
    latest_version = json_data[0]['name']
    if latest_version != VERSION:
        p_print(
            f"New version available! Please download it from https://github.com/qtchaos/py_mega_account_generator/releases/tag/{latest_version}", Colours.WARNING)


def reinstall_tenacity():
    """Reinstalls tenacity because of a dependency problem within the mega.py library."""
    try:
        p_print("Reinstalling tenacity...", Colours.WARNING)
        os.system("pip uninstall tenacity -y")
        os.system("pip install tenacity")
        clear_console()
        p_print("Reinstalled tenacity successfully!", Colours.OKGREEN)
        p_print("Please rerun the program.", Colours.WARNING)
        exit(0)
    except Exception as e:
        p_print("Failed to reinstall tenacity!", Colours.FAIL)
        print(e)
        exit(1)


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
