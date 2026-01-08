# GoogleSheet.py
import datetime
import gspread
from google.oauth2.service_account import Credentials
import logging

# -----------------------------
# Google Sheets Setup
# -----------------------------
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

CREDS = None
CLIENT = None
SPREADSHEET = None
SHEET = None

try:
    CREDS = Credentials.from_service_account_file(
        "ServiceAccount.json",
        scopes=SCOPE
    )
    CLIENT = gspread.authorize(CREDS)
    SPREADSHEET = CLIENT.open("ChatBotData")
    SHEET = SPREADSHEET.worksheet("Campaign5")
except Exception as e:
    logging.exception("Failed to initialize Google Sheets client. Google features will be disabled.")
    SHEET = None

# -----------------------------
# Sheet Headers
# -----------------------------
HEADERS = [
    "Name", "DOB", "Age", "Insurance", "Timing",
    "Income", "Phone", "Plan", "Email", "Signup",
    "Timestamp", "Email_Sent", "WhatsApp_Link"
]

# -----------------------------
# Value Mappings
# -----------------------------
INSURANCE_MAP = {
    "1": "No coverage at all",
    "2": "Basic employee",
    "3": "Some personal",
    "4": "Comprehensive"
}

TIMING_MAP = {
    "1": "3 months",
    "2": "6 months",
    "3": "9 months",
    "4": "12 months"
}

INCOME_MAP = {
    "1": "Less than RM20,000",
    "2": "RM20,001 - RM40,000",
    "3": "RM40,001 - RM60,000",
    "4": "More than RM60,000"
}

# -----------------------------
# Ensure header exists (row 1)
# -----------------------------
def ensure_header():
    if SHEET is None:
        return
    try:
        existing_headers = SHEET.row_values(1)
        if existing_headers != HEADERS:
            if existing_headers:
                # Overwrite first row instead of deleting
                SHEET.update("A1:M1", [HEADERS])
            else:
                SHEET.insert_row(HEADERS, 1)
    except Exception as e:
        logging.exception("Failed to ensure header.")

# -----------------------------
# Convert numeric choice to text
# -----------------------------
def map_value(value, mapping):
    return mapping.get(str(value), value)

# -----------------------------
# Save chatbot session
# -----------------------------
def save_to_sheet(session):
    """
    Save the chatbot session to Google Sheet.
    Returns the row index where data is inserted (for email update).
    """
    if SHEET is None:
        logging.warning("Google Sheets not initialized; skipping save_to_sheet.")
        return None

    ensure_header()

    # Map numeric choices to text
    insurance = map_value(session.get('insurance', ''), INSURANCE_MAP)
    timing = map_value(session.get('timing', ''), TIMING_MAP)
    income = map_value(session.get('income', ''), INCOME_MAP)

    phone = session.get('phone', '')
    whatsapp_link = f"https://wa.me/{phone}" if phone else ""

    row = [
        session.get('name', ''),
        session.get('dob', ''),
        session.get('age', ''),
        insurance,
        timing,
        income,
        phone,
        session.get('plan', ''),
        session.get('email', ''),
        session.get('signup', ''),
        datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "",  # Email_Sent column
        whatsapp_link  # WhatsApp link column
    ]

    try:
        # Find next empty row reliably
        existing_rows = SHEET.get_all_values()
        next_row_index = len(existing_rows) + 1  # row after last filled row
        SHEET.insert_row(row, next_row_index)
        return next_row_index
    except Exception as e:
        logging.exception("Failed to insert row into Google Sheet.")
        return None

# -----------------------------
# Update Email_Sent column
# -----------------------------
def update_email_sent(row_index):
    """
    Update the Email_Sent column (L) with current timestamp
    after successfully sending email. Ensure WhatsApp link exists.
    """
    if SHEET is None or row_index is None:
        return
    try:
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        SHEET.update_cell(row_index, 12, timestamp)  # Column L = Email_Sent

        # Ensure WhatsApp link is present
        phone = SHEET.cell(row_index, 7).value  # Column G = Phone
        if phone:
            whatsapp_link = f"https://wa.me/{phone}"
            SHEET.update_cell(row_index, 13, whatsapp_link)  # Column M = WhatsApp_Link
    except Exception as e:
        logging.exception(f"Failed to update Email_Sent or WhatsApp link at row {row_index}")
