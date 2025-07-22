import json

with open("credentials.json") as f:  # Your downloaded service account key
    creds = json.load(f)

# Escape the private key properly
creds["private_key"] = creds["private_key"].replace("\n", "\\n")

with open(".streamlit/secrets.toml", "w") as f:
    f.write("[gspread]\n")
    for k, v in creds.items():
        f.write(f'{k} = "{v}"\n')
    f.write('gsheet_key = "120CdAS6mUd8BMex1ftYZ6pRLsucxFiLlgCQp8PYVRG4"\n')  # <- Replace this

