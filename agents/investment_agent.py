"""
Investment Agent - Optimized for speed and stability
"""

from typing import Dict, List
from langchain_core.messages import HumanMessage

from agents.state import AgentState
from prompts.investment_prompts import INVESTMENT_SYSTEM_PROMPT
from models.model_router import get_llm
from tools.calculator import calculate_portfolio_metrics


def investment_node(state: AgentState) -> dict:
    """Main investment analysis node"""
    transactions = state.get("categorized_transactions", [])
    user_profile = state.get("user_profile", {})
    user_goals = state.get("user_goals", [])

    # Extract investment transactions
    investments = extract_investments(transactions)
    
    if not investments:
        return {
            "investment_analysis": {"status": "no_data", "message": "No investment transactions detected"},
            "messages": state.get("messages", []) + [HumanMessage(content="No investment data found.")],
            "next": "supervisor"
        }

    # Calculate metrics
    metrics = calculate_portfolio_metrics(investments)

    # Generate analysis and recommendations
    analysis = generate_portfolio_analysis(investments, metrics, user_profile, user_goals)
    recommendations = generate_recommendations(analysis, user_profile)

    return {
        "investment_analysis": {
            "portfolio_summary": metrics,
            "detailed_analysis": analysis,
            "recommendations": recommendations,
            "risk_score": metrics.get("risk_score", 50)
        },
        "messages": state.get("messages", []) + [HumanMessage(content="✅ Investment analysis completed.")],
        "next": "supervisor"
    }


def extract_investments(transactions: List) -> List[Dict]:
    """Extract potential investment transactions"""
    keywords = ["investment", "unit trust", "fixed deposit", "treasury", "stock", "dividend", "bond"]
    return [
        {
            "date": t.date,
            "description": t.description,
            "amount": abs(t.amount),
            "type": "investment"
        }
        for t in transactions 
        if any(kw in t.description.lower() for kw in keywords)
    ]


def generate_portfolio_analysis(investments: List[Dict], metrics: Dict, user_profile: Dict, user_goals: List[str]) -> Dict:
    llm = get_llm("balanced")
    
    prompt = f"""{INVESTMENT_SYSTEM_PROMPT}

Portfolio Value: {metrics.get('total_value', 0)} LKR
Risk Score: {metrics.get('risk_score', 50)}

User Profile: Risk Tolerance = {user_profile.get('risk_tolerance', 'Medium')}
Goals: {user_goals or 'None'}

Give a short, practical analysis."""
    
    try:
        response = llm.invoke(prompt)
        return {"analysis_text": response.content}
    except:
        return {"analysis_text": "Portfolio analysis completed."}


def generate_recommendations(analysis: Dict, user_profile: Dict) -> List[Dict]:
    """Simple recommendations"""
    risk = user_profile.get("risk_tolerance", "Medium").lower()
    
    if risk == "low":
        return [
            {"action": "Hold", "asset": "Fixed Deposits", "reason": "Safety first", "priority": "High"},
            {"action": "Rebalance", "asset": "Portfolio", "reason": "Reduce risk", "priority": "Medium"}
        ]
    elif risk == "high":
        return [
            {"action": "Consider", "asset": "Equity / Unit Trusts", "reason": "Higher long-term returns", "priority": "High"}
        ]
    else:
        return [
            {"action": "Rebalance", "asset": "Portfolio", "reason": "Maintain balanced allocation", "priority": "High"}
        ]