import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# --- Google Sheets Auth ---
@st.cache_resource
def get_gsheet():
    credentials_dict = dict(st.secrets["gspread"])
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    credentials = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
    gc = gspread.authorize(credentials)
    return gc.open_by_key(credentials_dict["gsheet_key"])

# --- UI ---
st.title("🚋 Mini Survey: Train Mood Check")

with st.form("survey_form"):
    name = st.text_input("What's your name?")
    mood = st.radio("How are you feeling today?", ["Happy", "Okay", "Sad"])
    submitted = st.form_submit_button("Submit")

if submitted:
    if name.strip() == "":
        st.warning("Please enter your name before submitting.")
    else:
        sheet = get_gsheet().worksheet("Responses")
        sheet.append_row([name, mood], value_input_option="USER_ENTERED")
        st.success("✅ Your response has been saved. Thank you!")
