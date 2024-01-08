"""Functions related to the upload functionality."""

from mega import Mega

from utilities.etc import Credentials, p_print, Colours


def upload_file(public: bool, file: str, credentials: Credentials):
    """Uploads a file to the account."""

    mega = Mega()
    mega.login(credentials.email, credentials.password)
    p_print("Uploading file... this might take a while.", Colours.OKGREEN)
    uploaded_file = mega.upload(file)
    p_print("File uploaded successfully.", Colours.OKGREEN)

    if public:
        link = mega.get_upload_link(uploaded_file)
        p_print(f"Shareable link: {link}", Colours.OKGREEN)
