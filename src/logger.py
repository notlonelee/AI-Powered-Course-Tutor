import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
from datetime import datetime

class SheetLogger:
    def __init__(self, spreadsheet_id: str, worksheet_name: str = "Logs"):
        self.spreadsheet_id = spreadsheet_id
        self.worksheet_name = worksheet_name
        self.worksheet = None
        self._authenticate()
    
    def _authenticate(self):
        try:
            # Get credentials from Streamlit secrets
            creds_dict = st.secrets["gcp_service_account"]
            
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            client = gspread.authorize(credentials)
            
            spreadsheet = client.open_by_key(self.spreadsheet_id)
            
            try:
                self.worksheet = spreadsheet.worksheet(self.worksheet_name)
            except gspread.exceptions.WorksheetNotFound:
                self.worksheet = spreadsheet.add_worksheet(self.worksheet_name, rows=100, cols=10)
                self.worksheet.append_row(["Timestamp", "User", "Question", "Answer", "Model", "Status"])
        
        except Exception as e:
            st.error(f"Google Sheets authentication failed: {e}")
            self.worksheet = None
    
    def log_interaction(self, user: str, question: str, answer: str, model: str, status: str = "success"):
        if not self.worksheet:
            return False
        
        try:
            row = [
                datetime.now().isoformat(),
                user,
                question[:500],
                answer[:500],
                model,
                status
            ]
            self.worksheet.append_row(row, value_input_option="RAW")
            return True
        except Exception as e:
            st.warning(f"Failed to log to Google Sheets: {e}")
            return False

