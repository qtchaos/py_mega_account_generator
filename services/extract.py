import os
import json
from utilities.etc import p_print, Colours

CREDENTIALS_FOLDER = "./credentials"
OUTPUT_FILE = "credentials.txt"

def extract_credentials(account_format: str = "{email}#{password}"):
    with open(OUTPUT_FILE, "w") as output_file:
        for file in os.listdir(CREDENTIALS_FOLDER):
            file_path = os.path.join(CREDENTIALS_FOLDER, file)
            
            if os.path.isfile(file_path) and file.endswith(".json"):
                with open(file_path, "r") as json_file:
                    try:
                        data = json.load(json_file)
                    except json.JSONDecodeError:
                        p_print(f"Failed to parse JSON file: {file}, skipping...", Colours.WARNING)
                        continue

                email = data.get("email", "")
                password = data.get("password", "")
                emailPassword = data.get("emailPassword", "")

                # Replace placeholders in the account_format string with actual values
                output = account_format.replace("{email}", email).replace("{password}", password).replace("{emailPassword}", emailPassword)

                output_file.write(f"{output}\n")

    p_print("Data extraction and writing complete!", Colours.OKGREEN)
    p_print(f"Output saved to: {os.path.abspath(OUTPUT_FILE)}", Colours.OKGREEN)
