"""All functions NOT related to the browser"""
import os
import shutil
from dataclasses import dataclass

import psutil


@dataclass
class Colours:
    """Colours for the console."""
    # pylint: disable=invalid-name
    HEADER: str = "\033[95m"
    OKBLUE: str = "\033[94m"
    OKCYAN: str = "\033[96m"
    OKGREEN: str = "\033[92m"
    WARNING: str = "\033[93m"
    FAIL: str = "\033[91m"
    ENDC: str = "\033[0m"


def clear_tmp():
    """Clears tmp folder."""
    matches = ["CrashpadMetrics-active.pma",
               "CrashpadMetrics.pma"]

    if os.path.exists("tmp"):
        try:
            shutil.rmtree("tmp")
            p_print("Cleared tmp folder successfully!", Colours.OKGREEN)
        except PermissionError:
            p_print(
                "Failed to clear temporary files... killing previous instances.", Colours.FAIL)
            kill_process(matches)

            clear_tmp()


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
