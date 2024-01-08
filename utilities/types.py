from dataclasses import dataclass


@dataclass
class Colours:
    """Colours for the console."""
    HEADER: str = "\033[95m"
    OKBLUE: str = "\033[94m"
    OKCYAN: str = "\033[96m"
    OKGREEN: str = "\033[92m"
    WARNING: str = "\033[93m"
    FAIL: str = "\033[91m"
    ENDC: str = "\033[0m"


@dataclass
class Credentials:
    """Credentials for the account."""
    email: str = ""
    emailPassword: str = ""
    password: str = ""
    id = ""

    __delitem__ = dict.__delitem__
    __getitem__ = dict.__getitem__


@dataclass
class Config:
    """Config class."""
    executablePath: str = ""
    accountFormat: str = ""

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value
