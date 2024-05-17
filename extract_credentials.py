import os
import json

CREDENTIALS_FOLDER = "./credentials"
OUTPUT_FILE = "credentials.txt"

with open(OUTPUT_FILE, "w") as output_file:
    for file in os.listdir(CREDENTIALS_FOLDER):
        if os.path.isfile(os.path.join(CREDENTIALS_FOLDER, file)) and file.endswith(
            ".json"
        ):
            with open(os.path.join(CREDENTIALS_FOLDER, file), "r") as json_file:
                data = json.load(json_file)
            email = data.get("email", "")
            password = data.get("password", "")
            output_file.write(f"{email}#{password}\n")

print("Data extraction and writing complete!")
print(f"Output saved to: {os.path.abspath(OUTPUT_FILE)}")
