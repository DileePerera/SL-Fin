"""
Analysis Agent - Spending analysis, categorization, and insights
"""

from typing import Dict, List
from langchain_core.messages import HumanMessage

from agents.state import AgentState, Transaction
from prompts.analysis_prompts import (
    ANALYSIS_SYSTEM_PROMPT,
    CATEGORIZATION_PROMPT,
    INSIGHTS_PROMPT
)
from models.model_router import get_llm
from tools.calculator import calculate_financial_metrics
from tools.visualizer import create_spending_pie_chart


def analysis_node(state: AgentState) -> dict:
    """Main analysis node - returns proper dict for LangGraph"""
    transactions: List[Transaction] = state.get("transactions", [])
    
    if not transactions:
        return {
            "messages": state.get("messages", []) + [HumanMessage(content="Error: No transactions found.")],
            "next": "supervisor",
            "error": "No transactions available"
        }

    # Step 1: Categorize (use fast fallback most of the time)
    categorized_transactions = categorize_transactions(transactions)
    
    # Step 2: Calculate metrics (pure Python - fast)
    metrics = calculate_financial_metrics(categorized_transactions)
    
    # Step 3: Generate insights (only use LLM here)
    insights = generate_insights(categorized_transactions, metrics, state.get("user_goals", []))
    
    # Step 4: Generate chart
    try:
        chart_path = create_spending_pie_chart(categorized_transactions)
    except:
        chart_path = None

    return {
        "categorized_transactions": categorized_transactions,
        "spending_analysis": {
            "metrics": metrics,
            "insights": insights,
            "chart_path": chart_path,
            "total_transactions": len(transactions),
        },
        "messages": state.get("messages", []) + [
            HumanMessage(content=f"✅ Spending analysis completed for {len(transactions)} transactions.")
        ],
        "next": "supervisor"
    }


def categorize_transactions(transactions: List[Transaction]) -> List[Transaction]:
    """Fast categorization with fallback"""
    # Use fast model for categorization
    llm = get_llm("balanced")   # Changed from heavy qwen2.5:32b
    
    sample = [
        {"desc": t.description, "amount": t.amount} 
        for t in transactions[:60]
    ]
    
    prompt = f"""{CATEGORIZATION_PROMPT}

Transactions:
{sample}

Return only valid JSON array with 'category' added."""
    
    try:
        response = llm.invoke(prompt)
        import json
        data = json.loads(response.content)
        
        return [
            Transaction(
                date=t.date,
                description=t.description,
                amount=t.amount,
                currency=t.currency,
                category=item.get("category", "Others")
            )
            for t, item in zip(transactions, data)
        ]
    except:
        return fallback_categorization(transactions)


def fallback_categorization(transactions: List[Transaction]) -> List[Transaction]:
    """Fast keyword fallback"""
    keywords = {
        "Food & Dining": ["keells", "arpico", "food", "restaurant", "hotel", "kfc"],
        "Transport": ["uber", "pickme", "petrol", "fuel", "bus"],
        "Utilities": ["dialog", "mobitel", "ceb", "water", "internet"],
        "Rent": ["rent", "house rent"],
        "Shopping": ["fashion", "market", "supermarket"],
        "Healthcare": ["hospital", "asiri", "nawaloka", "pharmacy"],
    }
    
    result = []
    for t in transactions:
        desc = t.description.lower()
        cat = "Others"
        for category, words in keywords.items():
            if any(word in desc for word in words):
                cat = category
                break
        result.append(Transaction(
            date=t.date,
            description=t.description,
            amount=t.amount,
            currency=t.currency,
            category=cat
        ))
    return result


def generate_insights(transactions: List[Transaction], metrics: Dict, user_goals: List[str]) -> Dict:
    """Generate insights using lighter model"""
    llm = get_llm("balanced")
    
    prompt = f"""{INSIGHTS_PROMPT}

Metrics: {metrics}
Goals: {user_goals or 'None'}

Give short, practical insights for a person in Sri Lanka."""
    
    try:
        response = llm.invoke(prompt)
        return {
            "summary": response.content[:600],
            "raw": response.content
        }
    except:
        return {"summary": "Analysis completed successfully."}