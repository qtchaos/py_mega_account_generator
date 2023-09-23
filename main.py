"""Main file for the project, handles the arguments and calls the other files."""
import asyncio
import argparse
import os
import sys
import pyppeteer

from utilities.etc import p_print, clear_console, Colours, clear_tmp, reinstall_tenacity

# Spooky import to check if the correct version of tenacity is installed.
if sys.version_info.major == 3 and sys.version_info.minor <= 11:
    try:
        from mega import Mega
    except AttributeError:
        reinstall_tenacity()

from services.alive import keepalive  # pylint: disable=E0611
from services.upload import upload_file
from utilities.web import generate_mail, type_name, type_password, initial_setup, save_credentials, mail_login, get_mail


chromium_exec = ""
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
    '--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0"',
]

parser = argparse.ArgumentParser()
parser.add_argument('-ka', '--keepalive', required=False, action='store_true',
                    help='Logs into the accounts to keep them alive.')
parser.add_argument('-v', '--verbose', required=False, action='store_true',
                    help='Shows storage left while using keepalive function.')
parser.add_argument('-f', '--file', required=False,
                    help='Uploads a file to the account.')
parser.add_argument('-p', '--public', required=False, action='store_true',
                    help='Generates a public link to the uploaded file, use with -f')

console_args = parser.parse_args()


async def register(credentials):
    """Registers and verifies mega.nz account."""
    browser = await pyppeteer.launch({
        "headless": True,
        "ignoreHTTPSErrors": True,
        "userDataDir": "./tmp",
        "args": args,
        "executablePath": chromium_exec,
        "autoClose": False,
        "ignoreDefaultArgs": ["--enable-automation", "--disable-extensions"],
    })

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
        f"Email: {credentials['email']}\nPassword: {credentials['password']}",
        Colours.OKCYAN,
    )

    await save_credentials(credentials)

    if console_args.file is not None:
        if os.path.exists(console_args.file):
            upload_file(console_args.public, console_args.file, credentials)
        else:
            p_print("File not found.", Colours.FAIL)
    exit(0)


if __name__ == "__main__":
    clear_console()

    if os.path.exists("config.json"):
        with open("config.json", "r", encoding="utf-8") as f:
            tmp = f.read().split('"')[3]
            if os.path.exists(tmp):
                chromium_exec = tmp
    else:
        # Check default_installs for a Chromium based browser. (Windows paths only for now)
        # since I don't have a Linux machine to test on.
        for i in default_installs:
            if os.path.exists(i):
                chromium_exec = i
                break

    # If no Chromium based browser is found, ask the user for the path to one.
    if not chromium_exec:
        p_print(
            "Failed to find a Chromium based browser. Please make sure you have one installed.", Colours.FAIL)
        chromium_exec = input(
            "Please enter the path to a Chromium based browser's executable: ")
        if os.path.exists(chromium_exec):
            p_print("Found executable!", Colours.OKGREEN)
            with open("config.json", "w", encoding="utf-8") as f:
                f.write('{"executablePath": "' + chromium_exec + '"}')
        else:
            p_print("Failed to find executable!", Colours.FAIL)
            exit(1)

    if console_args.keepalive:
        keepalive(console_args.verbose)
    else:
        clear_tmp()
        asyncio.run(register(asyncio.run(generate_mail())))
