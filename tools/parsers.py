import pandas as pd
from typing import List, Dict
from langchain_community.document_loaders import PyPDFLoader, CSVLoader
import re
from typing import List
from agents.state import Transaction

def parse_bank_statement(file_path: str) -> List[Dict]:
    """Parse PDF or CSV bank statement"""
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        # Use LLM to structure later in agent
        return [{"content": doc.page_content} for doc in docs]
    else:
        raise ValueError("Unsupported file type")
    
    return df.to_dict('records')

def extract_transactions_from_text(text: str) -> List[Transaction]:
    """Rule-based extraction as fallback"""
    transactions = []
    # Simple regex pattern for common bank statement formats
    pattern = r'(\d{2}[/\.-]\d{2}[/\.-]\d{2,4})\s+(.+?)\s+([-\d,]+\.?\d*)'
    
    for match in re.finditer(pattern, text):
        date, desc, amount_str = match.groups()
        try:
            amount = float(amount_str.replace(',', ''))
            transactions.append(Transaction(
                date=date,
                description=desc.strip(),
                amount=amount,
                currency="LKR"
            ))
        except:
            continue
    return transactions