"""
Budget Agent - Optimized for speed
"""

from typing import Dict, List
from langchain_core.messages import HumanMessage

from agents.state import AgentState, Transaction
from prompts.budget_prompts import BUDGET_SYSTEM_PROMPT, BUDGET_CREATION_PROMPT
from models.model_router import get_llm
from tools.calculator import calculate_category_totals


def budget_node(state: AgentState) -> dict:
    transactions: List[Transaction] = state.get("categorized_transactions", [])
    
    if not transactions:
        return {"next": "supervisor", "error": "No transactions for budget"}

    category_spending = calculate_category_totals(transactions)
    
    budget_plan = generate_budget_plan(category_spending, state.get("user_goals", []))
    comparison = compare_actual_vs_budget(category_spending, budget_plan)

    return {
        "budget_plan": {
            "monthly_budget": budget_plan,
            "category_spending": category_spending,
            "comparison": comparison,
            "total_monthly_income": estimate_monthly_income(transactions),
            "total_monthly_expenses": sum(category_spending.values()),
            "savings_rate": calculate_savings_rate(transactions)
        },
        "messages": state.get("messages", []) + [HumanMessage(content="✅ Budget plan created.")],
        "next": "supervisor"
    }


def generate_budget_plan(category_spending: Dict, user_goals: List[str]) -> Dict:
    llm = get_llm("balanced")  # Faster model
    
    prompt = f"""{BUDGET_CREATION_PROMPT}

Current Spending: {category_spending}
Goals: {user_goals or 'None'}

Return a realistic monthly budget in LKR as JSON."""
    
    try:
        response = llm.invoke(prompt)
        import json
        data = json.loads(response.content)
        return data.get("categories", category_spending)
    except:
        return fallback_budget(category_spending)


def fallback_budget(spending: Dict) -> Dict:
    return {cat: round(amount * 0.9, -2) for cat, amount in spending.items()}


def compare_actual_vs_budget(actual: Dict, budget: Dict) -> Dict:
    comparison = {}
    for cat in set(list(actual.keys()) + list(budget.keys())):
        act = actual.get(cat, 0)
        bud = budget.get(cat, 0)
        diff = act - bud
        comparison[cat] = {
            "actual": round(act, 2),
            "budget": round(bud, 2),
            "difference": round(diff, 2),
            "status": "over" if diff > 0 else "under" if diff < -3000 else "on_track"
        }
    return comparison


def estimate_monthly_income(transactions: List[Transaction]) -> float:
    income = sum(t.amount for t in transactions if t.amount > 0)
    return round(income * 1.1, -3) if income > 0 else 180000


def calculate_savings_rate(transactions: List[Transaction]) -> float:
    income = sum(t.amount for t in transactions if t.amount > 0)
    expenses = abs(sum(t.amount for t in transactions if t.amount < 0))
    return round(((income - expenses) / income) * 100, 1) if income > 0 else 0.0