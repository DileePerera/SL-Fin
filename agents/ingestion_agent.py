"""
Ingestion Agent - Responsible for parsing bank statements and extracting transactions.
Supports: CSV, PDF, Excel
"""

import pandas as pd
from typing import List, Dict
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.messages import HumanMessage

from agents.state import AgentState, Transaction
from prompts.ingestion_prompts import INGESTION_SYSTEM_PROMPT
from models.model_router import get_llm
from tools.parsers import extract_transactions_from_text


def ingestion_node(state: AgentState) -> AgentState:
    """Main ingestion node"""
    messages = state.get("messages", [])
    raw_documents = state.get("raw_documents", [])
    
    all_transactions: List[Transaction] = []
    errors = []

    for doc in raw_documents:
        file_path = doc.get("file_path")
        file_type = doc.get("file_type", "").lower()
        
        try:
            if file_type == "csv":
                transactions = parse_csv(file_path)
            elif file_type == "pdf":
                transactions = parse_pdf(file_path)
            elif file_type in ["xlsx", "xls"]:
                transactions = parse_excel(file_path)
            else:
                transactions = parse_text_file(file_path)
                
            all_transactions.extend(transactions)
            
        except Exception as e:
            errors.append(f"Failed to parse {file_path}: {str(e)}")

    # LLM fallback if no transactions found
    if not all_transactions and raw_documents:
        llm_transactions = llm_structured_extraction(raw_documents)
        all_transactions.extend(llm_transactions)

    all_transactions = deduplicate_transactions(all_transactions)

    return {
        "transactions": all_transactions,
        "raw_documents": raw_documents,
        "messages": messages + [HumanMessage(content=f"Processed {len(all_transactions)} transactions.")],
        "next": "supervisor",
        "error": errors if errors else None
    }


def parse_csv(file_path: str) -> List[Transaction]:
    df = pd.read_csv(file_path)
    date_col = find_column(df, ["date", "transaction_date", "posting_date"])
    desc_col = find_column(df, ["description", "details", "narration"])
    amount_col = find_column(df, ["amount", "debit", "credit", "transaction_amount"])
    
    transactions = []
    for _, row in df.iterrows():
        try:
            amount = float(row[amount_col]) if pd.notna(row[amount_col]) else 0.0
            transactions.append(Transaction(
                date=str(row[date_col]),
                description=str(row[desc_col]),
                amount=amount,
                currency="LKR",
                category=None
            ))
        except:
            continue
    return transactions


def parse_pdf(file_path: str) -> List[Transaction]:
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    full_text = "\n".join([page.page_content for page in pages])
    
    transactions = extract_transactions_from_text(full_text)
    
    if len(transactions) < 5:
        return llm_structured_extraction([{"content": full_text}])
    return transactions


def parse_excel(file_path: str) -> List[Transaction]:
    return parse_csv(file_path)


def parse_text_file(file_path: str) -> List[Transaction]:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    return extract_transactions_from_text(text)


def llm_structured_extraction(documents: List[Dict]) -> List[Transaction]:
    llm = get_llm("strong")
    
    combined_text = "\n\n".join([doc.get("content", "") for doc in documents])
    
    prompt = f"""{INGESTION_SYSTEM_PROMPT}

Extract all transactions as valid JSON array.

Text:
{combined_text[:12000]}
"""
    
    response = llm.invoke(prompt)
    try:
        import json
        data = json.loads(response.content)
        return [Transaction(**item) for item in data if isinstance(item, dict)]
    except:
        return []


def find_column(df: pd.DataFrame, possible_names: List[str]) -> str:
    for name in possible_names:
        for col in df.columns:
            if name.lower() in str(col).lower():
                return col
    return df.columns[0]


def deduplicate_transactions(transactions: List[Transaction]) -> List[Transaction]:
    seen = set()
    unique = []
    for t in transactions:
        key = (t.date, t.description[:50], round(t.amount, 2))
        if key not in seen:
            seen.add(key)
            unique.append(t)
    return unique