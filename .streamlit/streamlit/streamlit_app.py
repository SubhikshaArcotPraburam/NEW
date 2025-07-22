import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- GOOGLE SHEETS CONNECTION ---
@st.cache_resource
def get_gsheet():
    credentials_dict = dict(st.secrets["gspread"])  # Load credentials from secrets.toml
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    credentials = Credentials.from_service_account_info(
        credentials_dict,
        scopes=scopes
    )
    gc = gspread.authorize(credentials)
    return gc.open_by_key(credentials_dict["gsheet_key"])


# --- UI SETUP ---

st.title("Vendor Management Portal")
st.markdown("Enter the details of the new vendor below.")

# --- Read Data from Google Sheets ---
sheet = get_gsheet()
worksheet = sheet.worksheet("Vendors")

# Read existing vendor data
records = worksheet.get_all_records()
existing_data = pd.DataFrame(records)

# --- Business Logic Options ---
BUSINESS_TYPES = [
    "Manufacturer", "Distributor", "Wholesaler", "Retailer", "Service Provider"
]
PRODUCTS = ["Electronics", "Apparel", "Groceries", "Software", "Other"]

# --- Vendor Input Form ---
with st.form(key="vendor_form"):
    company_name = st.text_input(label="Company Name*")
    business_type = st.selectbox("Business Type*", options=BUSINESS_TYPES, index=None)
    products = st.multiselect("Products Offered", options=PRODUCTS)
    years_in_business = st.slider("Years in Business", 0, 50, 5)
    onboarding_date = st.date_input(label="Onboarding Date")
    additional_info = st.text_area(label="Additional Notes")

    st.markdown("**required*")

    submit_button = st.form_submit_button(label="Submit Vendor Details")

    if submit_button:
        # --- Validation ---
        if not company_name or not business_type:
            st.warning("Ensure all mandatory fields are filled.")
            st.stop()
        elif "CompanyName" in existing_data.columns and existing_data["CompanyName"].str.contains(company_name).any():
            st.warning("A vendor with this company name already exists.")
            st.stop()
        else:
            # --- Create New Entry ---
            new_entry = {
                "CompanyName": company_name,
                "BusinessType": business_type,
                "Products": ", ".join(products),
                "YearsInBusiness": years_in_business,
                "OnboardingDate": onboarding_date.strftime("%Y-%m-%d"),
                "AdditionalInfo": additional_info,
            }

            # Append to Google Sheet
            worksheet.append_row(list(new_entry.values()), value_input_option="USER_ENTERED")
            st.success("Vendor details successfully submitted!")
