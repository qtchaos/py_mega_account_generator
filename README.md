# py_mega_account_generator

Generate MEGA accounts with a single command, upload files, get shareable links and do all of that however many times you want with loops.

## Instructions

These instructions assume you have [Git](https://git-scm.com/) and [Python](https://www.python.org/) installed, if you do not have Git installed, then download the project from [here](https://github.com/qtchaos/py_mega_account_generator/archive/refs/heads/master.zip)

```
git clone https://github.com/qtchaos/py_mega_account_generator.git
cd py_mega_account_generator
pip install -r requirements.txt
python main.py
```

## Usage

> [!NOTE]
> The maximum upload size of a file is 20GB, since this is the limit on a free account.

You can use this program without any arguments at all, this will spit out a new account with the welcome pdf deleted, it will show the login credentials in the console and create a new file in the credentials folder.
If you want to upload a file though, you can use the following setup: `python main.py -f FILENAME -p`, this will upload the file to a new account and print out a publicly shareable link. Unfortunately, it seems that MEGA likes to purge accounts that haven't been logged into for a while, so if it has been a while since you started generating new accounts, you might want to run the keepalive service: `python main.py -ka -v`, this will login to every account and print out the storage used. And if you want to mass create accounts or upload files, then you can use the loop argument: `python main.py -p -f FILENAME -l TIMES_TO_LOOP`.

### Format
```
{"email": "*******@*******.com", "emailPassword": "*****", "password": "*********"}
```
The `emailPassword` represents the password used to create the [mail.tm](https://mail.tm) account.\
If you want to login to the MEGA account later on, you have to use the `email` and `password` fields.

## Arguments
> [!WARNING]  
> Do not use the arguments in the **Services** section together with the file upload arguments.

`-f filename, --file filename` | Uploads a file to the generated account.\
`-p, --public` | Generates a shareable link to the file. \
`-l int, --loop int` | Loops the script x amount of times.

### Services

`-ka, --keepalive` | Logs into the accounts to keep them alive.\
`-v, --verbose` | Shows storage left while using keepalive function.
