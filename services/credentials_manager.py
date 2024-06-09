import os
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import tinydb
from tinydb import Query


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

    def update_account_mega(self,email,MegaLinkToAdd):
        Emails = Query()
        # self.db.search(Emails.email == f"{email}")
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
