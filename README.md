# py_mega_account_generator

Unofficial Python port of crachkub-dev's [mega-account-generator](https://github.com/crackhub-dev/mega-account-generator) with added features.

Simple script for generating mega.nz accounts.

## Instructions

**This assumes you have [Git](https://git-scm.com/) and [Python](https://www.python.org/) (>= 3.10) installed.**

```
git clone https://github.com/qtchaos/py_mega_account_generator.git
cd py_mega_account_generator
pip install -r requirements.txt
python main.py
```

## Arguments

`-v, --verbose` | Shows storage left while using keepalive function.\
`-ka, --keepalive` | Logs into the accounts to keep them alive.\
`-f filename, --file filename` | Uploads a file to the generated account.\
`-p, --public` | Generates a shareable link to the file.

###### ~~Probably spaghetti code, but~~ it works!
