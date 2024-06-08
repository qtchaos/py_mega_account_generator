"""All functions NOT related to the browser"""

import os
import shutil
import json
from urllib.request import urlopen
import sys
from mega import Mega
import psutil

from utilities.types import Colours, Credentials

VERSION = "v1.5.1"
mega = Mega()


def clear_tmp() -> bool:
	"""Clears tmp folder."""
	max_attempts = 1

	for _ in range(max_attempts):
		if os.path.exists("tmp"):
			try:
				shutil.rmtree("tmp")
				return True
			except PermissionError:
				matches = ["CrashpadMetrics-active.pma", "CrashpadMetrics.pma"]
				kill_process(matches)

	# If we've reached this point, all attempts have failed
	return False


def check_for_updates():
	"""Checks for updates via latest release tag."""
	with urlopen(
		"https://api.github.com/repos/qtchaos/py_mega_account_generator/tags"
	) as request:
		json_data = json.loads(request.read().decode())
		latest_version = json_data[0]["name"]
		if latest_version == VERSION:
			return False

		p_print(
			f"New version available! Please download it from https://github.com/qtchaos/py_mega_account_generator/releases/tag/{latest_version}",
			Colours.WARNING,
		)
	return True


def delete_default(credentials: Credentials):
	"""Deletes the default welcome file."""
	mega.login(credentials.email, credentials.password)
	pdf = mega.get_files_in_node(2)
	key = list(pdf.keys())[0]
	mega.destroy(key)


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
					p_print(f"Killing process {process.name()}...", Colours.WARNING)
					process.kill()
		except psutil.AccessDenied:
			continue

	p_print("Killed previous instances successfully!", Colours.OKGREEN)


def p_print(
	text,
	colour,
):
	"""Prints text in colour."""
	print(colour + text + Colours.ENDC)


def clear_console():
	"""Clears console."""
	os.system("cls" if os.name == "nt" else "clear")
