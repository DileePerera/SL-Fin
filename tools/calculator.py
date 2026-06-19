"""
Safe Financial Calculator Tool - All numerical calculations should go through this module
to prevent hallucinations and ensure accuracy.
"""

from typing import Dict, List, Any, Optional
import numpy as np
from datetime import datetime
from agents.state import Transaction


def calculate_financial_metrics(transactions: List[Transaction]) -> Dict[str, Any]:
    """Calculate core financial health metrics"""
    if not transactions:
        return {}

    incomes = [t.amount for t in transactions if t.amount > 0]
    expenses = [abs(t.amount) for t in transactions if t.amount < 0]

    total_income = sum(incomes)
    total_expenses = sum(expenses)
    net_income = total_income - total_expenses

    # Savings Rate
    savings_rate = (net_income / total_income * 100) if total_income > 0 else 0

    # Average transaction values
    avg_income = np.mean(incomes) if incomes else 0
    avg_expense = np.mean(expenses) if expenses else 0

    # Category breakdown
    category_totals = calculate_category_totals(transactions)

    return {
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "net_income": round(net_income, 2),
        "savings_rate": round(savings_rate, 2),
        "avg_income_transaction": round(avg_income, 2),
        "avg_expense_transaction": round(avg_expense, 2),
        "transaction_count": len(transactions),
        "category_breakdown": category_totals,
        "top_expense_categories": dict(sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:5])
    }


def calculate_category_totals(transactions: List[Transaction]) -> Dict[str, float]:
    """Group transactions by category"""
    from collections import defaultdict
    category_totals = defaultdict(float)
    
    for t in transactions:
        category = t.category or "Others"
        category_totals[category] += abs(t.amount) if t.amount < 0 else t.amount
    
    return dict(sorted(category_totals.items(), key=lambda x: x[1], reverse=True))


def calculate_portfolio_metrics(portfolio: List[Dict]) -> Dict[str, Any]:
    """Calculate investment portfolio metrics"""
    if not portfolio:
        return {
            "total_value": 0,
            "risk_score": 50,
            "diversification_score": 0,
            "asset_allocation": {}
        }

    total_value = sum(item.get("amount", 0) for item in portfolio)
    
    # Simple risk scoring based on asset types
    risk_score = calculate_risk_score(portfolio)
    diversification_score = calculate_diversification_score(portfolio)

    # Asset allocation
    allocation = calculate_asset_allocation(portfolio)

    return {
        "total_value": round(total_value, 2),
        "risk_score": risk_score,
        "diversification_score": diversification_score,
        "asset_allocation": allocation,
        "num_assets": len(portfolio)
    }


def calculate_risk_score(portfolio: List[Dict]) -> int:
    """Simple risk scoring (0-100)"""
    risk_weights = {
        "equity": 85,
        "stock": 85,
        "crypto": 95,
        "unit trust": 60,
        "fixed deposit": 25,
        "treasury": 20,
        "bond": 35,
        "gold": 40
    }
    
    total_risk = 0
    total_weight = 0
    
    for item in portfolio:
        desc = item.get("description", "").lower()
        amount = item.get("amount", 0)
        
        item_risk = 50  # default
        for asset_type, weight in risk_weights.items():
            if asset_type in desc:
                item_risk = weight
                break
                
        total_risk += item_risk * amount
        total_weight += amount
    
    return int(total_risk / total_weight) if total_weight > 0 else 50


def calculate_diversification_score(portfolio: List[Dict]) -> int:
    """Score diversification (0-100)"""
    asset_types = set()
    for item in portfolio:
        desc = item.get("description", "").lower()
        if any(x in desc for x in ["stock", "equity"]):
            asset_types.add("equity")
        elif any(x in desc for x in ["fixed", "deposit", "treasury"]):
            asset_types.add("fixed")
        elif "crypto" in desc:
            asset_types.add("crypto")
        elif "gold" in desc:
            asset_types.add("gold")
        else:
            asset_types.add("other")
    
    score = min(100, len(asset_types) * 25)
    return score


def calculate_asset_allocation(portfolio: List[Dict]) -> Dict[str, float]:
    """Calculate percentage allocation"""
    total = sum(item.get("amount", 0) for item in portfolio)
    if total == 0:
        return {}
    
    allocation = defaultdict(float)
    for item in portfolio:
        desc = item.get("description", "").lower()
        amount = item.get("amount", 0)
        percentage = (amount / total) * 100
        
        if any(x in desc for x in ["stock", "equity"]):
            allocation["Equity"] += percentage
        elif any(x in desc for x in ["fixed", "deposit", "treasury", "bond"]):
            allocation["Fixed Income"] += percentage
        elif "crypto" in desc:
            allocation["Crypto"] += percentage
        elif "gold" in desc:
            allocation["Gold"] += percentage
        else:
            allocation["Others"] += percentage
    
    return {k: round(v, 2) for k, v in allocation.items()}


def safe_calculate(numbers: List[float], operation: str = "sum") -> float:
    """Safe mathematical operations"""
    if not numbers:
        return 0.0
    
    try:
        if operation == "sum":
            return float(sum(numbers))
        elif operation == "mean":
            return float(np.mean(numbers))
        elif operation == "median":
            return float(np.median(numbers))
        elif operation == "max":
            return float(max(numbers))
        elif operation == "min":
            return float(min(numbers))
        else:
            return float(sum(numbers))
    except:
        return 0.0


# Utility functions for common finance formulas

def calculate_compound_interest(principal: float, rate: float, years: int, compounds_per_year: int = 12) -> float:
    """Compound Interest Calculator"""
    return principal * (1 + rate/compounds_per_year)**(compounds_per_year * years)


def calculate_monthly_emi(principal: float, annual_rate: float, years: int) -> float:
    """Calculate EMI for loans"""
    monthly_rate = annual_rate / 12 / 100
    months = years * 12
    if monthly_rate == 0:
        return principal / months
    emi = principal * monthly_rate * (1 + monthly_rate)**months / ((1 + monthly_rate)**months - 1)
    return round(emi, 2)


def calculate_retirement_projection(
    monthly_savings: float,
    current_age: int,
    retirement_age: int,
    expected_return: float = 0.10,
    inflation: float = 0.09
) -> Dict:
    """Project retirement corpus"""
    years = retirement_age - current_age
    real_return = expected_return - inflation
    
    future_value = monthly_savings * 12 * (((1 + real_return)**years - 1) / real_return) if real_return != 0 else monthly_savings * 12 * years
    
    return {
        "years_to_retirement": years,
        "projected_corpus": round(future_value, 2),
        "monthly_savings": monthly_savings
    }