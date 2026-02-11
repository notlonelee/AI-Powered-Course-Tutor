import gspread
from datetime import datetime
import os
import json

SHEET_ID = "1GmaqxFDaP-916TRnPKbUJS7oJU494edKkqc8cmAcDkk" 

def get_google_sheets_client():
    """Get authenticated Google Sheets client"""
    try:
        creds_json = os.getenv("google_sheets_json")
        if not creds_json:
            raise ValueError("google_sheets_json not found in secrets")
        
        creds_dict = json.loads(creds_json)
        gc = gspread.service_account_from_dict(creds_dict)
        return gc
    except Exception as e:
        print(f"Error authenticating with Google Sheets: {e}")
        return None

def log_interaction(question, response_with_context, response_without_context, classification, confidence=0, production=False):
    """Log interaction to Google Sheets"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        gc = get_google_sheets_client()
        if gc is None:
            print("Could not connect to Google Sheets")
            return
        
        sh = gc.open_by_key(SHEET_ID)
        worksheet = sh.sheet1
        
        new_row = [
            timestamp,
            question,
            classification,
            f"{confidence*100:.0f}",
            response_with_context[:], 
            response_without_context[]
        ]
        
        worksheet.append_row(new_row)
        print("✓ Logged to Google Sheets")
    except Exception as e:
        print(f"Error logging to Google Sheets: {e}")
