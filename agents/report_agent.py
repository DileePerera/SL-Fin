"""
Report Agent - Final report generation (Optimized)
"""

from typing import Dict, List
from langchain_core.messages import HumanMessage
from datetime import datetime

from agents.state import AgentState
from prompts.report_prompts import EXECUTIVE_SUMMARY_PROMPT
from models.model_router import get_llm


def report_node(state: AgentState) -> dict:
    """Final report node"""
    spending = state.get("spending_analysis", {})
    budget = state.get("budget_plan", {})
    investment = state.get("investment_analysis", {})
    forecast = state.get("forecast_results", {})
    user_goals = state.get("user_goals", [])

    # Generate executive summary
    summary = generate_executive_summary(spending, budget, investment, forecast, user_goals)

    overall_score = calculate_overall_score(spending, budget, investment)

    final_report = {
        "report_title": f"Personal Finance Report - {datetime.now().strftime('%B %Y')}",
        "generated_date": datetime.now().isoformat(),
        "executive_summary": summary,
        "financial_health": {
            "overall_score": overall_score,
            "savings_rate": spending.get("metrics", {}).get("savings_rate", 0)
        },
        "spending_analysis": spending,
        "budget_analysis": budget,
        "investment_analysis": investment,
        "future_forecast": forecast,
        "top_recommendations": extract_top_recommendations(budget, investment),
        "disclaimer": "This report was generated locally using AI models."
    }

    return {
        "report": final_report,
        "messages": state.get("messages", []) + [HumanMessage(content="✅ Final report generated successfully.")],
        "next": "END"
    }


def generate_executive_summary(spending, budget, investment, forecast, user_goals):
    llm = get_llm("balanced")
    
    prompt = f"""{EXECUTIVE_SUMMARY_PROMPT}

Key Numbers:
- Savings Rate: {spending.get('metrics', {}).get('savings_rate', 0)}%
- Monthly Income (est): Rs. {budget.get('total_monthly_income', 0):,}
- Risk Score: {investment.get('risk_score', 'N/A')}

User Goals: {user_goals or 'None'}

Write a short, honest, and encouraging executive summary."""
    
    try:
        response = llm.invoke(prompt)
        return response.content
    except:
        return "Your financial analysis is complete. Review the details in each section."


def calculate_overall_score(spending: Dict, budget: Dict, investment: Dict) -> int:
    score = 65
    savings_rate = spending.get("metrics", {}).get("savings_rate", 0)
    if savings_rate > 20:
        score += 20
    elif savings_rate > 10:
        score += 10
    return min(95, score)


def extract_top_recommendations(budget: Dict, investment: Dict) -> List[Dict]:
    recs = []
    if budget.get("recommendations"):
        recs.extend(budget["recommendations"][:2])
    if investment.get("recommendations"):
        recs.extend(investment["recommendations"][:2])
    return recs[:5]