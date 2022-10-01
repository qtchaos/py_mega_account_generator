"""
Generates a verified mega.nz account.
"""
import asyncio
import json
import random
import re
import shutil
import string
import sys

import pymailtm
import pyppeteer
from faker import Faker
from pymailtm.pymailtm import CouldNotGetAccountException

try:
    shutil.rmtree("tmp")
except PermissionError:
    print("Failed to clear temp files... Chromium already running?")
    sys.exit(1)

fake = Faker()
args = [
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-infobars',
    '--window-position=0,0',
    '--ignore-certificate-errors',
    '--ignore-certificate-errors-spki-list',
    '--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/95.0.4638.69 Safari/537.36" '
]


def get_random_string(length):
    """Generate a random string with a given length."""
    letters = string.ascii_lowercase
    letters.join(string.ascii_uppercase)
    result_str = ''.join(random.choice(letters) for _ in range(length))
    return result_str


async def generate_mail():
    """Generate mail.tm account and return account credentials."""
    mail = pymailtm.MailTm()
    while True:
        try:
            account = mail.get_account()
        except CouldNotGetAccountException:
            print("Retrying mail.tm account generation...")
            continue
        break
    credentials = {
        "email": account.address,
        "emailPassword": account.password,
        "password": get_random_string(14),
        "id": account.id_
    }
    return credentials


async def register(credentials):
    """Registers and verifies mega.nz account."""
    name = str(fake.name()).split(" ", 2)
    firstname = name[0]
    lastname = name[1]
    browser = await pyppeteer.launch({
        "headless": True,
        "ignoreHTTPSErrors": True,
        "userDataDir": "./tmp",
        "args": args,
        "autoClose": False,
        "ignoreDefaultArgs": ['--enable-automation', '--disable-extensions']
    })
    context = await browser.createIncognitoBrowserContext()
    page = await context.newPage()
    await page.goto("https://mega.nz/register")
    await page.waitForSelector('#register_form')
    await page.type('#register-firstname-registerpage2', firstname)
    await page.type('#register-lastname-registerpage2', lastname)
    await page.type('#register-email-registerpage2', credentials["email"])
    await type_password(page, credentials)
    mail = await mail_login(credentials)
    await asyncio.sleep(1.5)  # Wait for confirm email.
    message = mail.get_messages()[0]
    confirm_link = (re.findall(r"(https?:[^ ]*)", str(message))[0]).replace("Best", "")[:-4]
    confirm_page = await context.newPage()
    await confirm_page.goto(confirm_link)
    confirm_field = "#login-password2"
    await confirm_page.waitForSelector(confirm_field)
    await confirm_page.click(confirm_field)
    await confirm_page.type(confirm_field, credentials["password"])
    await confirm_page.click(".login-button")
    await confirm_page.waitForSelector('#freeStart')  
    await confirm_page.click("#freeStart")
    await asyncio.sleep(0.5)
    await browser.close()
    print("Verified mega.nz account.")
    print(f"Email: {credentials['email']}\nPassword: {credentials['password']}")
    await save_credentials(credentials)
    return True


async def save_credentials(credentials):
    """Pass credentials into a file."""
    file = open(f"credentials/{credentials['email'][:-4]}.json", "w", encoding="UTF-8")
    del credentials["id"]
    json_file = json.dumps(credentials)
    file.write(json_file)
    file.close()


async def mail_login(credentials):
    """Logs into the mail.tm account with the generated credentials"""
    while True:
        try:
            print("Retrieving mail...")
            mail = pymailtm.Account(
                credentials["id"],
                credentials["email"],
                credentials["emailPassword"]
            )
            print("Got mail!")
            return mail
        except CouldNotGetAccountException:
            continue


async def type_password(page, credentials):
    """Types passwords into the password fields."""
    await page.click('#register-password-registerpage2')
    await page.type('#register-password-registerpage2', credentials["password"])
    await page.click('#register-password-registerpage3')
    await page.type('#register-password-registerpage3', credentials["password"])
    await page.click('#register-check-registerpage2')
    await page.querySelectorAllEval('.understand-check', "(elements) => {elements[0].click();}")
    await page.click('.register-button')
    print("Registered account successfully.")


asyncio.run(register(asyncio.run(generate_mail())))
