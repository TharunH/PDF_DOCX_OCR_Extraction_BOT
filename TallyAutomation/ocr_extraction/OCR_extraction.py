import re
import json

def safe_extract(pattern, text, group=1, default=''):
    match = re.search(pattern, text)
    return match.group(group) if match else default

def extract_from_text(text):
    lines = text.splitlines()
    lines = [line.strip() for line in lines if line.strip()]

    # --- STEP 3: Regex / Pattern Matching ---
    account_info = {
        "account_no": safe_extract(r'Account No\.?\s*:\s*([\d\-]+)', text),
        "iban": safe_extract(r'IBAN\s*([A-Z0-9]+)', text),
        "account_name": safe_extract(r'Account Name\s*:\s*(.*)', text),
        "start_date": safe_extract(r'Start Date\s*:\s*([\d\-A-Za-z]+)', text),
        "end_date": safe_extract(r'End Date\s*:\s*([\d\-A-Za-z]+)', text),
        "opening_balance": safe_extract(r'Opening Balance\s*:\s*(\S+)', text),
        "closing_balance": safe_extract(r'Closing\(Available\) Balance\s*:\s*(\S+)', text),
    }

    metadata = {
        "report_date": safe_extract(r'Report Date\s*:\s*([\d\-A-Za-z]+)', text),
        "entity": safe_extract(r'(PROCASH)', text),
    }

    # --- STEP 4: Table Reconstruction ---
    transaction_rows = []
    in_table = False

    for i, line in enumerate(lines):
        if re.search(r'^Sr\.?No', line):
            in_table = True
            continue

        if in_table:
            # Split by | or multiple spaces
            parts = re.split(r'\s{2,}|\|', line)
            if len(parts) >= 5:
                row = {
                    "date": parts[1].strip() if len(parts) > 1 else '',
                    "value_date": parts[2].strip() if len(parts) > 2 else '',
                    "bank_ref": parts[3].strip() if len(parts) > 3 else '',
                    "customer_ref": parts[4].strip() if len(parts) > 4 else '',
                    "description": " ".join(parts[5:-2]).strip() if len(parts) > 6 else '',
                    "debit": parts[-2].strip(),
                    "credit": parts[-1].strip() if len(parts) > 6 else '',
                }
                transaction_rows.append(row)
            else:
                # Multi-line continuation (stitch to last row)
                if transaction_rows:
                    transaction_rows[-1]["description"] += " " + line.strip()

    # --- STEP 5–7: Final Structured Output ---
    result = {
        "metadata": metadata,
        "account_info": account_info,
        "transactions": transaction_rows
    }

    return result
