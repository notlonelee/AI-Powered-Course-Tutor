import pandas as pd
from datetime import datetime
import os

LOG_FILE = "output_log.xlsx"
PRODUCTION_LOG_FILE = "production_log.xlsx"

def log_interaction(question, response_with_context, response_without_context, classification, confidence=0, production=False):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_file = PRODUCTION_LOG_FILE if production else LOG_FILE

    new_row = {
        "Timestamp": timestamp,
        "Question": question,
        "Classification": classification,
        "Confidence": confidence*100,
        "Response_With_Context": response_with_context,
        "Response_Without_Context": response_without_context
    }
    
    if os.path.exists(log_file):
        df = pd.read_excel(log_file)
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    else:
        df = pd.DataFrame([new_row])
    
    # Save to Excel
    df.to_excel(log_file, index=False)
