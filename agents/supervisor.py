"""
Supervisor - Orchestrates the flow between agents
"""

from langgraph.graph import StateGraph, END, START
from typing import Literal
from .state import AgentState
from models.model_router import get_llm


def supervisor_node(state: AgentState) -> dict:
    """Supervisor decides the next agent and returns state update"""
    llm = get_llm("balanced")  # Use fast model for routing
    
    prompt = f"""You are a supervisor managing a personal finance AI workflow.

Current Status:
- Transactions extracted: {len(state.get('transactions', [])) > 0}
- Spending analysis completed: {state.get('spending_analysis') is not None}
- Budget plan created: {state.get('budget_plan') is not None}

Decide the next step. Reply with **ONLY** one of these words:
ingestion, analysis, budget, investment, forecast, report, or END"""

    try:
        response = llm.invoke(prompt)
        next_step = response.content.strip().lower()
        
        if next_step not in ["ingestion", "analysis", "budget", "investment", "forecast", "report"]:
            next_step = "report"  # safe default
    except Exception:
        next_step = "analysis"  # fallback on error

    return {"next": next_step}


def build_finance_graph():
    workflow = StateGraph(AgentState)

    # Lazy loading wrappers to prevent import errors
    def ingestion_wrapper(state):
        from .ingestion_agent import ingestion_node
        return ingestion_node(state)

    def analysis_wrapper(state):
        from .analysis_agent import analysis_node
        return analysis_node(state)

    def budget_wrapper(state):
        from .budget_agent import budget_node
        return budget_node(state)

    def investment_wrapper(state):
        from .investment_agent import investment_node
        return investment_node(state)

    def forecast_wrapper(state):
        from .forecast_agent import forecast_node
        return forecast_node(state)

    def report_wrapper(state):
        from .report_agent import report_node
        return report_node(state)

    # Add Nodes
    workflow.add_node("ingestion", ingestion_wrapper)
    workflow.add_node("analysis", analysis_wrapper)
    workflow.add_node("budget", budget_wrapper)
    workflow.add_node("investment", investment_wrapper)
    workflow.add_node("forecast", forecast_wrapper)
    workflow.add_node("report", report_wrapper)
    workflow.add_node("supervisor", supervisor_node)

    # Define Flow
    workflow.add_edge(START, "ingestion")
    
    # Dynamic routing
    workflow.add_conditional_edges(
        "supervisor",
        lambda s: s["next"],
        {
            "ingestion": "ingestion",
            "analysis": "analysis",
            "budget": "budget",
            "investment": "investment",
            "forecast": "forecast",
            "report": "report",
            END: END,
        }
    )

    # Fallback: After each agent, go back to supervisor
    for node in ["ingestion", "analysis", "budget", "investment", "forecast", "report"]:
        workflow.add_edge(node, "supervisor")

    return workflow.compile()