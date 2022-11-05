"""All functions related to the browser"""
import asyncio
import re
import os
import json
import string
import random
import pymailtm
from faker import Faker

from pymailtm.pymailtm import CouldNotGetAccountException

from utilites.etc import p_print, Colours

fake = Faker()


def get_random_string(length):
    """Generate a random string with a given length."""
    lower_letters = string.ascii_lowercase
    upper_letters = string.ascii_uppercase
    numbers = string.digits
    alphabet = lower_letters + upper_letters + numbers

    result_str = "".join(random.choice(alphabet) for _ in range(length))
    return result_str


async def initial_setup(context, message, credentials):
    """Initial setup for the account."""
    confirm_link = (re.findall(r"(https?:[^ ]*)",
                               str(message))[0]).replace("Best", "")[:-4]

    confirm_page = await context.newPage()
    await confirm_page.goto(confirm_link)
    confirm_field = "#login-password2"
    await confirm_page.waitForSelector(confirm_field)
    await confirm_page.click(confirm_field)
    await confirm_page.type(confirm_field, credentials["password"])
    await confirm_page.click(".login-button")
    await confirm_page.waitForSelector("#freeStart")
    await confirm_page.click("#freeStart")


async def save_credentials(credentials):
    """Pass credentials into a file."""
    if not os.path.exists("credentials"):
        os.mkdir("credentials")
    with open(f"credentials/{credentials['email'][:-4]}.json",
              "w",
              encoding="UTF-8") as file:
        del credentials["id"]
        json_file = json.dumps(credentials)
        file.write(json_file)


async def mail_login(credentials):
    """Logs into the mail.tm account with the generated credentials"""
    while True:
        try:
            mail = pymailtm.Account(credentials["id"], credentials["email"],
                                    credentials["emailPassword"])
            p_print("Retrieved mail successfully!", Colours.OKGREEN)
            return mail
        except CouldNotGetAccountException:
            continue


async def get_mail(mail):
    """Get the latest email from the mail.tm account"""
    while True:
        try:
            message = mail.get_messages()[0]
            p_print("Found mail!", Colours.OKGREEN)
            return message
        except IndexError:
            p_print("Failed to find mail... trying again in 1.5 seconds.",
                    Colours.WARNING)
            await asyncio.sleep(1.5)


async def type_name(page, credentials):
    """Types name into the name fields."""
    name = str(fake.name()).split(" ", 2)
    firstname = name[0]
    lastname = name[1]
    await page.goto("https://mega.nz/register")
    await page.waitForSelector("#register_form")
    await page.type("#register-firstname-registerpage2", firstname)
    await page.type("#register-lastname-registerpage2", lastname)
    await page.type("#register-email-registerpage2", credentials["email"])


async def type_password(page, credentials):
    """Types passwords into the password fields."""
    await page.click("#register-password-registerpage2")
    await page.type("#register-password-registerpage2", credentials["password"])
    await page.click("#register-password-registerpage3")
    await page.type("#register-password-registerpage3", credentials["password"])
    await page.click("#register-check-registerpage2")
    await page.querySelectorAllEval(".understand-check",
                                    "(elements) => {elements[0].click();}")
    await page.click(".register-button")
    p_print("Registered account successfully!", Colours.OKGREEN)


async def generate_mail():
    """Generate mail.tm account and return account credentials."""
    mail = pymailtm.MailTm()
    while True:
        try:
            account = mail.get_account()
            break
        except CouldNotGetAccountException:
            p_print("Retrying mail.tm account generation...", Colours.WARNING)
    credentials = {
        "email": account.address,
        "emailPassword": account.password,
        "password": get_random_string(14),
        "id": account.id_,
    }
    return credentials
