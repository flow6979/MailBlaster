import logging
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

def load_google_sheet(sheet_id, range_name):
    if not sheet_id or not range_name:
        logging.error("Sheet ID and Range Name must be provided.")
        return pd.DataFrame()

    try:
        # Getting credentials and create a client
        creds, _ = google.auth.default()
        service = build('sheets', 'v4', credentials=creds)

        logging.info(f"Fetching data from Google Sheet: {sheet_id}, Range: {range_name}")
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()

        values = result.get('values', [])
        if not values:
            logging.warning("No data found in the provided range.")
            return pd.DataFrame()

        df = pd.DataFrame(values[1:], columns=values[0])
        logging.info("Data successfully loaded into DataFrame.")
        return df

    except HttpError as err:
        logging.error(f"HTTP error occurred while loading Google Sheet: {err}")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

    return pd.DataFrame()
