# py_mega_account_generator

Generate mega.nz accounts with a single command, upload files, get shareable links and do all of the above with looping to generate as many accounts and upload a file as many times as you want.

## Instructions

**This assumes you have [Git](https://git-scm.com/) and [Python](https://www.python.org/) installed.**

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
`-p, --public` | Generates a shareable link to the file. \
`-l int, --loop int` | Loops the script x amount of times.
