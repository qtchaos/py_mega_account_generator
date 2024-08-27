import os
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import tinydb
from tinydb import Query
import tkinter as tk
from tkinter import ttk


class CredentialsManager:
	def __init__(self):
		self.db = tinydb.TinyDB("credentials.json")

	def encrypt_credentials(self, password, credentials):
		password = password.encode()  # convert to bytes
		salt = os.urandom(16)  # generate a random salt
		kdf = PBKDF2HMAC(
			algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000
		)
		key = base64.urlsafe_b64encode(kdf.derive(password))
		f = Fernet(key)
		encrypted_credentials = f.encrypt(credentials.encode())
		return encrypted_credentials, salt

	def decrypt_credentials(self, password, encrypted_credentials, salt):
		try:
			password = password.encode()  # convert to bytes
			kdf = PBKDF2HMAC(
				algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000
			)
			key = base64.urlsafe_b64encode(kdf.derive(password))
			f = Fernet(key)
			decrypted_credentials = f.decrypt(encrypted_credentials).decode()
			return decrypted_credentials
		except (ValueError, InvalidToken):
			return None

	def store_credentials(self, password, email, encrypted_credentials_hex, salt_hex):
		self.db.insert(
			{"email": email, "credentials": encrypted_credentials_hex, "salt": salt_hex}
		)

	def get_credentials(self, password):
		query = Query()
		results = self.db.search(query.email.exists())
		decrypted_credentials = []
		for result in results:
			try:
				encrypted_credentials_hex = result["credentials"]
				salt_hex = result["salt"]
				encrypted_credentials = bytes.fromhex(encrypted_credentials_hex)
				salt = bytes.fromhex(salt_hex)
				decrypted_credential = self.decrypt_credentials(
					password, encrypted_credentials, salt
				)
				if decrypted_credential:
					decrypted_credentials.append(decrypted_credential.split(":"))
			except (ValueError, IndexError):
				continue
		return decrypted_credentials

	def update_account_mega(self, email, MegaLinkToAdd):
		Emails = Query()
		self.db.update({"megaLinks": [str(MegaLinkToAdd)]}, Emails.email == f"{email}")
		return True

	def get_mega_links(self, email):
		Emails = Query()
		results = self.db.search(Emails.email == f"{email}")
		if len(results) == 0:
			return ["No Links found"]
		else:
			result = results[0]
			if "megaLinks" in result:
				return result["megaLinks"]
			else:
				return ["No megaLinks found"]


class CredentialsViewer:
	"""
	Theme:
	Black #24262C
	Pink #C9ADA7
	Rose quartz #9A8C98
	"""

	def __init__(self, master):
		self.master = master
		master.title("Credentials Viewer")

		self.toast_canvas = None  # Canvas for toast messages
		self.toast_message_id = None  # Text id for the toast message

		self.dark_mode = tk.BooleanVar()
		self.dark_mode.set(True)  # Start in dark mode

		self.style = ttk.Style()
		self.configure_dark_mode()
		ttk.Style().configure(
			"green/black.TLabel",
			foreground="#9A8C98",
			background="#111111",
			font=("Helvetica", 10, "bold"),
		)
		ttk.Style().configure(
			"green/black.TButton", foreground="#9A8C98", background="#111111"
		)
		ttk.Style().configure(
			"green/black.TEntry", foreground="#9A8C98", background="#111111"
		)
		ttk.Style().configure(
			"green/black.TCheckbutton", foreground="#9A8C98", background="#111111"
		)
		ttk.Style().configure(
			"green/black.THeading", foreground="#9A8C98", background="#111111"
		)

		master.configure(background="#24262C")

		self.dark_mode_checkbox = ttk.Checkbutton(
			master,
			style="green/black.TCheckbutton",
			text="Dark Mode",
			variable=self.dark_mode,
			command=self.toggle_dark_mode,
		)
		self.dark_mode_checkbox.grid(row=0, column=0, padx=5, pady=5)

		self.password_label = ttk.Label(master, text="Password:")
		self.password_label.grid(row=1, column=0, padx=5, pady=5)

		self.password_entry = ttk.Entry(master, show="*", style="green/black.TEntry")
		self.password_entry.grid(row=1, column=1, padx=5, pady=5)

		self.decrypt_button = ttk.Button(
			master,
			text="Decrypt",
			command=self.decrypt_credentials,
			style="green/black.TButton",
		)
		self.decrypt_button.grid(row=1, column=2, padx=5, pady=5)

		self.credentials_tree = ttk.Treeview(
			master,
			style="green/black.TLabel",
			columns=(
				"Email",
				"Email Password",
				"Account ID",
				"Account Password",
				"Mega LINKs",
			),
			show="headings",
		)
		self.credentials_tree.heading("Email", text="Email")
		self.credentials_tree.heading("Email Password", text="Email Password")
		self.credentials_tree.heading("Account ID", text="Account ID")
		self.credentials_tree.heading("Account Password", text="Account Password")
		self.credentials_tree.heading("#5", text="MEGA DL Links")
		self.credentials_tree.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

		self.status_label = ttk.Label(master, text="")
		self.status_label.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

		self.cm = CredentialsManager()

		# Apply dark mode styling initially
		self.configure_dark_mode()

		# Context Menu
		self.context_menu = tk.Menu(master, tearoff=0)
		self.context_menu.add_command(label="Copy", command=self.copy_selected_value)

		# Keep track of the right-clicked event
		self.right_click_event = None

		# Bind right-click to show the context menu
		self.credentials_tree.bind("<Button-3>", self.show_context_menu)

	def configure_dark_mode(self):
		if self.dark_mode.get():
			self.master.configure(background="#24262C")
			self.style.configure("TLabel", background="#24262C", foreground="#C9ADA7")
			self.style.configure(
				"TEntry",
				background="#9A8C98",
				foreground="#24262C",
				insertcolor="#C9ADA7",
				fieldbackground="#9A8C98",
			)
			self.style.configure(
				"TButton",
				background="#9A8C98",
				foreground="#24262C",
				relief="flat",
				borderwidth=0,
			)
			self.style.configure(
				"Treeview",
				background="#24262C",
				foreground="#C9ADA7",
				fieldbackground="#33353F",
				selectbackground="#9A8C98",
				selectforeground="#24262C",
				rowheight=30,
				font=("Helvetica", 20, "bold"),
			)
			self.style.configure(
				"Treeview.Heading",
				background="#33353F",
				foreground="#C9ADA7",
				relief="flat",
				font=("Helvetica", 13, "bold"),
			)

			self.style.map(
				"Treeview",
				background=[("selected", "#9A8C98")],
				foreground=[("selected", "#24262C")],
			)
		else:
			self.master.configure(background="white")
			self.style.configure("TLabel", background="white", foreground="black")
			self.style.configure("TEntry", background="white", foreground="black")
			self.style.configure(
				"TButton", background="SystemButtonFace", foreground="black"
			)
			self.style.configure(
				"Treeview",
				background="white",
				foreground="black",
				fieldbackground="white",
			)
			self.style.configure(
				"Treeview.Heading", background="SystemButtonFace", foreground="black"
			)

	def toggle_dark_mode(self):
		self.configure_dark_mode()

	def decrypt_credentials(self):
		password = self.password_entry.get()
		credentials_list = self.cm.get_credentials(password)

		if credentials_list:
			self.credentials_tree.delete(*self.credentials_tree.get_children())
			for credentials in credentials_list:
				email = credentials[0] if credentials else ""
				email_password = credentials[1] if len(credentials) > 1 else ""
				account_id = credentials[2] if len(credentials) > 2 else ""
				account_password = credentials[3] if len(credentials) > 3 else ""
				temp_links = self.cm.get_mega_links(email)
				mega_links = temp_links if temp_links else ""
				self.credentials_tree.insert(
					"",
					"end",
					values=(
						email,
						email_password,
						account_id,
						account_password,
						mega_links,
					),
				)
			self.status_label.config(text="Credentials decrypted successfully.")
		else:
			self.status_label.config(
				text="Failed to decrypt credentials. Please check the password and try again."
			)

	def show_context_menu(self, event):
		self.right_click_event = event
		try:
			self.credentials_tree.selection_set(
				self.credentials_tree.identify_row(event.y)
			)
			self.context_menu.post(event.x_root, event.y_root)
		finally:
			self.context_menu.grab_release()

	def copy_selected_value(self):
		if not self.right_click_event:
			return

		region = self.credentials_tree.identify(
			"region", self.right_click_event.x, self.right_click_event.y
		)
		if region != "cell":
			return

		column = self.credentials_tree.identify_column(self.right_click_event.x)
		item = self.credentials_tree.identify_row(self.right_click_event.y)
		if not column or not item:
			return

		column_id = (
			int(column.replace("#", "")) - 1
		)  # Convert column index to zero-based
		selected_value = self.credentials_tree.item(item)["values"][column_id]

		if selected_value:
			self.master.clipboard_clear()
			self.master.clipboard_append(selected_value)
			self.master.update()  # Keeps the clipboard data persistent
			self.show_toast("Text copied!", "#28a745")

	def show_toast(self, message, color):
		"""
		Displays a toast message at a location that won't cover other widgets.
		The message is rounded and styled.
		"""
		# Destroy any existing toast
		if self.toast_canvas:
			self.toast_canvas.destroy()

		# Avoid covering other widgets by positioning at the bottom-right corner
		x = self.master.winfo_width() - 250
		y = self.master.winfo_height() - 80

		# Create a new canvas for the toast
		width, height = 200, 40
		radius = 20
		self.toast_canvas = tk.Canvas(
			self.master, width=width, height=height, bg="#111111", highlightthickness=0
		)
		self.toast_canvas.place(x=x, y=y)

		# Draw a rounded rectangle using arcs and rectangles
		self.toast_canvas.create_arc(
			(0, 0, 2 * radius, 2 * radius),
			start=90,
			extent=90,
			fill=color,
			outline=color,
		)
		self.toast_canvas.create_arc(
			(width - 2 * radius, 0, width, 2 * radius),
			start=0,
			extent=90,
			fill=color,
			outline=color,
		)
		self.toast_canvas.create_arc(
			(0, height - 2 * radius, 2 * radius, height),
			start=180,
			extent=90,
			fill=color,
			outline=color,
		)
		self.toast_canvas.create_arc(
			(width - 2 * radius, height - 2 * radius, width, height),
			start=270,
			extent=90,
			fill=color,
			outline=color,
		)
		self.toast_canvas.create_rectangle(
			radius, 0, width - radius, height, fill=color, outline=color
		)
		self.toast_canvas.create_rectangle(
			0, radius, width, height - radius, fill=color, outline=color
		)

		# Add the text to the toast
		self.toast_message_id = self.toast_canvas.create_text(
			width / 2,
			height / 2,
			text=message,
			fill="white",
			font=("Helvetica", 12, "bold"),
		)

		# Auto-destroy after 2500 ms
		self.master.after(2500, self.toast_canvas.destroy)


root = tk.Tk()
viewer = CredentialsViewer(root)
root.mainloop()
