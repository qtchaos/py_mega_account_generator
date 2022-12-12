"""Functions related to the upload functionality."""
try:
    from mega import Mega # pylint: disable=E0401
except AttributeError:
    print("Please use Python 3.10 or lower, see the issue below for details.")
    print("https://github.com/qtchaos/py_mega_account_generator/issues/4")
    exit(1)

from utilites.etc import p_print, Colours


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