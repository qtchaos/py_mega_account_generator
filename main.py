"""
Generates a verified mega.nz account.
"""
import asyncio
import pyppeteer

from utilites.etc import p_print, clear_console, Colours, clear_tmp
from utilites.web import generate_mail, type_name, type_password, initial_setup, save_credentials, mail_login, get_mail


args = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-infobars",
    "--window-position=0,0",
    "--ignore-certificate-errors",
    "--ignore-certificate-errors-spki-list",
    '--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/95.0.4638.69 Safari/537.36" ',
]


async def register(credentials):
    """Registers and verifies mega.nz account."""
    browser = await pyppeteer.launch({
        "headless": True,
        "ignoreHTTPSErrors": True,
        "userDataDir": "./tmp",
        "args": args,
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


if __name__ == "__main__":
    clear_console()
    clear_tmp()
    asyncio.run(register(asyncio.run(generate_mail())))
