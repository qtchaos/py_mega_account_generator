"""Functions related to the upload functionality."""
from mega import Mega

from utilities.etc import p_print, Colours


def upload_file(public: bool, file: bool, credentials: dict):
    """Uploads a file to the account."""
    mega = Mega()
    mega.login(credentials["email"], credentials["password"])
    p_print("Uploading file...", Colours.OKGREEN)
    
    if public:
        link = mega.get_upload_link(mega.upload(file))
        p_print(f"Shareable link: {link}", Colours.OKGREEN)
    else:
        mega.upload(file)
        p_print("Uploaded file successfully.", Colours.OKGREEN)