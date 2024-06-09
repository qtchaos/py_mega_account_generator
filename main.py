"""Main file for the project, handles the arguments and calls the other files."""

import asyncio
import argparse
import os
import sys
from typing import Tuple
import pyppeteer

from services.alive import keepalive
from services.upload import upload_file
from utilities.web import (
    generate_mail,
    type_name,
    type_password,
    initial_setup,
    mail_login,
    get_mail,
)
from utilities.etc import (
    Credentials,
    p_print,
    clear_console,
    Colours,
    clear_tmp,
    reinstall_tenacity,
    check_for_updates,
    delete_default,
)
import getpass
from services.credentials_manager import CredentialsManager
import getpass
from tinydb import TinyDB, Query

# Create an instance of the CredentialsManager class
cm = CredentialsManager()

# Spooky import to check if the correct version of tenacity is installed.
if sys.version_info.major == 3 and sys.version_info.minor <= 11:
    try:
        pass
    except AttributeError:
        reinstall_tenacity()

default_installs = [
    "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
    "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe",
    "C:/Program Files (x86)/BraveSoftware/Brave-Browser/Application/brave.exe",
    "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
]
args = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-infobars",
    "--window-position=0,0",
    "--ignore-certificate-errors",
    "--ignore-certificate-errors-spki-list",
    '--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0"',
]

parser = argparse.ArgumentParser()
parser.add_argument(
    "-ka",
    "--keepalive",
    required=False,
    action="store_true",
    help="Logs into the accounts to keep them alive.",
)
parser.add_argument(
    "-e",
    "--extract",
    required=False,
    action="store_true",
    help="Extracts the credentials to a file.",
)
parser.add_argument(
    "-v",
    "--verbose",
    required=False,
    action="store_true",
    help="Shows storage left while using keepalive function.",
)
parser.add_argument(
    "-f", "--file", required=False, help="Uploads a file to the account."
)
parser.add_argument(
    "-p",
    "--public",
    required=False,
    action="store_true",
    help="Generates a public link to the uploaded file, use with -f",
)
parser.add_argument(
    "-l",
    "--loop",
    required=False,
    help="Loops the program for a specified amount of times.",
    type=int,
)

console_args = parser.parse_args()
config_db = TinyDB("config.json")


def setup() -> str:
    """Sets up the configs so everything runs smoothly."""

    if os.path.exists("config.json"):
        s = config_db.all()
        print(s)
        account_format_exists = False
        executable_path_exists = False
        for item in s:
            if "accountFormat" in item:
                account_format_exists = True
            if "executablePath" in item:
                executable_path_exists = True
                executable_path = item["executablePath"]
        if not account_format_exists:
            config_db.insert({"accountFormat": "{email}:{password}"})
        if not executable_path_exists:
            config_db.insert({"executablePath": ""})
    else:
        config_db.insert({"accountFormat": "{email}:{password}"})
        config_db.insert({"executablePath": ""})
        executable_path = ""

    # If no Chromium based browser is found, ask the user for the path to one.
    if not executable_path_exists:
        p_print(
            "Failed to find a Chromium based browser. Please make sure you have one installed.",
            Colours.FAIL,
        )
        executable_path = input(
            "Please enter the path to a Chromium based browser's executable: "
        )
        if os.path.exists(executable_path):
            p_print("Found executable!", Colours.OKGREEN)
            config_db.update(
                {"executablePath": executable_path}, Query().executablePath == ""
            )
        else:
            p_print("Failed to find executable!", Colours.FAIL)
            sys.exit(1)
    elif executable_path_exists:
        p_print("Found executable!", Colours.OKGREEN)

    return executable_path


def loop_registrations(loop_count: int, executable_path: str):
    """Registers accounts in a loop."""
    for _ in range(loop_count):
        p_print(f"Loop {_ + 1}/{loop_count}", Colours.OKGREEN)
        clear_tmp()

        credentials = asyncio.run(generate_mail())
        asyncio.run(register(credentials, executable_path))


def get_matching_password():
    """
    Prompts the user to enter and confirm a password.
    Returns the password if both inputs match.
    Prompts again if the passwords don't match.
    """
    while True:
        password = getpass.getpass("Enter password to encrypt credentials: ")
        password_2 = getpass.getpass("Re-enter password to confirm credentials: ")

        if password == password_2:
            print("Passwords match.")
            return password
        else:
            print("Passwords do not match. Please try again.")


async def register(credentials: Credentials, executable_path: str):
    """Registers and verifies mega.nz account."""
    browser = await pyppeteer.launch(
        {
            "headless": True,
            "ignoreHTTPSErrors": True,
            "userDataDir": f"{os.getcwd()}/tmp",
            "args": args,
            "executablePath": executable_path,
            "autoClose": False,
            "ignoreDefaultArgs": ["--enable-automation", "--disable-extensions"],
        }
    )

    context = await browser.createIncognitoBrowserContext()
    page = await context.newPage()

    await type_name(page, credentials)
    await type_password(page, credentials)
    mail = await mail_login(credentials)

    await asyncio.sleep(1.5)
    message = await get_mail(mail)

    await initial_setup(context, message, credentials)
    await asyncio.sleep(0.5)
    await browser.close()

    p_print("Verified account.", Colours.OKGREEN)
    p_print(
        f"Email: {credentials.email}\nPassword: {credentials.password}",
        Colours.OKCYAN,
    )

    # Store the credentials using the CredentialsManager class
    password = get_matching_password()

    encrypted_credentials, salt = cm.encrypt_credentials(
        password,
        f"{credentials.email}:{credentials.emailPassword}:{credentials.id}:{credentials.password}",
    )
    encrypted_credentials_hex = encrypted_credentials.hex()
    salt_hex = salt.hex()

    cm.store_credentials(
        password, credentials.email, encrypted_credentials_hex, salt_hex
    )

    delete_default(credentials)

    if console_args.file is not None:
        file_size = os.path.getsize(console_args.file)
        if os.path.exists(console_args.file) and 0 < file_size < 2e10:
            if file_size >= 5e9:
                p_print(
                    "File is larger than 5GB, mega.nz limits traffic to 5GB per IP.",
                    Colours.WARNING,
                )
            successful = upload_file(console_args.public, console_args.file, credentials)
            if successful is not None:
                successful = str(successful)
                cm.update_account_mega(str(credentials.email),successful)
                
        else:
            p_print("File not found.", Colours.FAIL)
    if console_args.loop is None or console_args.loop <= 1:
        sys.exit(0)


if __name__ == "__main__":
    clear_console()
    check_for_updates()

    executable_path = setup()
    if not executable_path:
        p_print("Failed while setting up!", Colours.FAIL)
        sys.exit(1)

    if console_args.extract:
        ...
        # extract_credentials(config.accountFormat)
    elif console_args.keepalive:
        keepalive(console_args.verbose)
    elif console_args.loop is not None and console_args.loop > 1:
        loop_registrations(console_args.loop, executable_path)
    else:
        clear_tmp()
        credentials = asyncio.run(generate_mail())
        asyncio.run(register(credentials, executable_path))
