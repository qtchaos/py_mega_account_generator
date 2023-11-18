"""Functions related to the keepalive functionality."""
import os
import json

from mega import Mega
from mega.errors import RequestError

from utilities.etc import p_print, Colours

mega = Mega()


def keepalive(verbose: bool):
    """Keep the generated accounts alive by logging in."""

    files = os.listdir("./credentials")
    if len(files) == 0:
        p_print(
            "No credentials found, please remove all arguments and try again.", Colours.FAIL)
        return

    i = 0
    for file in files:
        if file.endswith(".json"):
            with open(f"./credentials/{file}", "r", encoding="utf-8") as f:
                credentials = json.JSONDecoder().decode(f.read())
                i += 1
                try:
                    mega.login(credentials["email"], credentials["password"])
                    storage_left = mega.get_quota() / 1024
                    p_print(
                        f"{i}/{len(files)} Successfully logged into {credentials['email']}", Colours.OKGREEN)
                    if verbose:
                        p_print(
                            f"    {storage_left}GB of storage left", Colours.OKGREEN)
                except RequestError:
                    p_print(
                        f"{i}/{len(files)} Failed to login to {credentials['email']}", Colours.FAIL)
                    continue
