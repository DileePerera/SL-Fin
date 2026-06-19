"""
Forecast Agent - Optimized (lighter Monte Carlo)
"""

from typing import Dict, List
import numpy as np
from langchain_core.messages import HumanMessage

from agents.state import AgentState, Transaction
from prompts.forecast_prompts import FORECAST_SYSTEM_PROMPT
from models.model_router import get_llm


def forecast_node(state: AgentState) -> dict:
    transactions = state.get("categorized_transactions", [])
    if not transactions:
        return {"next": "supervisor", "error": "No data"}

    monthly_income = estimate_monthly_income(transactions)
    monthly_expenses = estimate_monthly_expenses(transactions)

    cashflow = {
        "monthly_income": monthly_income,
        "monthly_expenses": monthly_expenses,
        "monthly_savings": monthly_income - monthly_expenses,
        "projected_savings_12m": (monthly_income - monthly_expenses) * 12
    }

    monte_carlo = run_simple_monte_carlo(monthly_income, monthly_expenses)

    return {
        "forecast_results": {
            "cashflow_forecast": cashflow,
            "monte_carlo": monte_carlo,
            "summary": {
                "projected_savings_12m": cashflow["projected_savings_12m"],
                "median_net_worth_5y": monte_carlo["median_net_worth_5y"]
            }
        },
        "messages": state.get("messages", []) + [HumanMessage(content="✅ Forecast completed.")],
        "next": "supervisor"
    }


def run_simple_monte_carlo(monthly_income: float, monthly_expenses: float, simulations=500):
    savings = []
    for _ in range(simulations):
        sim_savings = (monthly_income - monthly_expenses) * np.random.normal(1.0, 0.15)
        savings.append(sim_savings * 60)  # 5 years
    
    return {
        "median_net_worth_5y": round(np.median(savings), 2),
        "p10": round(np.percentile(savings, 10), 2),
        "p90": round(np.percentile(savings, 90), 2)
    }


def estimate_monthly_income(transactions):
    income = sum(t.amount for t in transactions if t.amount > 0)
    return max(150000, round(income * 1.2, -3))


def estimate_monthly_expenses(transactions):
    expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
    return max(100000, round(expenses * 1.1, -3))