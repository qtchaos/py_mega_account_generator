"""All functions related to the browser"""

import asyncio
import re
import string
import random
import pymailtm
from faker import Faker

from pymailtm.pymailtm import CouldNotGetAccountException, CouldNotGetMessagesException
import pyppeteer
import pyppeteer.page

from utilities.etc import Credentials, p_print, Colours

fake = Faker()


def get_random_string(length):
	"""Generate a random string with a given length."""
	lower_letters = string.ascii_lowercase
	upper_letters = string.ascii_uppercase
	numbers = string.digits
	alphabet = lower_letters + upper_letters + numbers

	return "".join(random.choice(alphabet) for _ in range(length))


async def initial_setup(context, message, credentials):
	"""Initial setup for the account."""
	confirm_link = re.findall(
		r'href="(https:\/\/mega\.nz\/#confirm[^ ][^"]*)', str(message)
	)[0]

	confirm_page = await context.newPage()
	await confirm_page.goto(confirm_link)
	confirm_field = "#login-password2"
	await confirm_page.waitForSelector(confirm_field)
	await confirm_page.click(confirm_field)
	await confirm_page.type(confirm_field, credentials.password)
	await confirm_page.click(".login-button")
	try:
		await confirm_page.waitForSelector("#freeStart", timeout=30000)
		await confirm_page.click("#freeStart")
	except TimeoutError:
		pass


async def mail_login(credentials: Credentials):
	"""Logs into the mail.tm account with the generated credentials"""
	while True:
		try:
			mail = pymailtm.Account(
				credentials.id, credentials.email, credentials.emailPassword
			)
			p_print("Retrieved mail successfully!", Colours.OKGREEN)
			return mail
		except CouldNotGetAccountException:
			continue


async def get_mail(mail):
	"""Get the latest email from the mail.tm account"""
	attempts = 0

	while True:
		try:
			message = mail.get_messages()[0]
			p_print("Found mail!", Colours.OKGREEN)
			return message
		except (IndexError, CouldNotGetMessagesException):
			attempts += 1
			p_print(
				"Failed to find mail... trying again in 1.5 seconds.", Colours.WARNING
			)
			await asyncio.sleep(1.5)


async def type_name(page: pyppeteer.page.Page, credentials: Credentials):
	"""Types name into the name fields."""
	name = str(fake.name()).split(" ", 2)
	firstname = name[0]
	lastname = name[1]
	await page.goto("https://mega.nz/register")
	await page.waitForSelector("#register_form")
	await page.evaluate(
		f"const textInputs = document.querySelectorAll('input[type=text]'); textInputs[2].value = '{firstname}'; textInputs[3].value = '{lastname}'; textInputs[4].value = '{credentials.email}';"
	)


async def finish_form(page: pyppeteer.page.Page, credentials: Credentials):
	"""Checks the boxes for the register page."""
	await page.click("#register-check-registerpage2")
	await page.click(".register-button")


async def type_password(page: pyppeteer.page.Page, credentials: Credentials):
	"""Types passwords into the password fields."""
	await page.evaluate(
		f"const passwordInputs = document.querySelectorAll('input[type=password]'); passwordInputs[0].value = '{credentials.password}'; passwordInputs[1].value = '{credentials.password}';"
	)
	await page.querySelectorAllEval(
		".understand-check", "(elements) => {elements[0].click();}"
	)
	p_print("Registered account successfully!", Colours.OKGREEN)


async def generate_mail() -> Credentials:
	"""Generate mail.tm account and return account credentials."""
	mail = pymailtm.MailTm()
	try_count = 0

	while True:
		try:
			account = mail.get_account()
			break
		except CouldNotGetAccountException:
			p_print("Retrying mail.tm account generation...", Colours.WARNING)
			try_count += 1
			await asyncio.sleep(try_count)

	credentials = Credentials()
	credentials.email = account.address
	credentials.emailPassword = account.password
	credentials.password = get_random_string(14)
	credentials.id = account.id_
	return credentials
