"""
Visualization Tool - Generates interactive and static charts for financial reports
using Plotly. Works excellently with Streamlit.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime
import os


def generate_summary_charts(
    categorized_transactions: List,
    budget_plan: Dict = None,
    forecast: Dict = None
) -> Dict[str, str]:
    """
    Generate all key charts and return paths or figure objects.
    """
    charts = {}
    
    # 1. Spending by Category (Pie Chart)
    charts["spending_pie"] = create_spending_pie_chart(categorized_transactions)
    
    # 2. Spending by Category (Bar Chart)
    charts["spending_bar"] = create_spending_bar_chart(categorized_transactions)
    
    # 3. Budget vs Actual
    if budget_plan and budget_plan.get("comparison"):
        charts["budget_vs_actual"] = create_budget_comparison_chart(budget_plan)
    
    # 4. Portfolio Allocation
    if budget_plan and budget_plan.get("portfolio_summary"):
        charts["portfolio_allocation"] = create_portfolio_pie_chart(budget_plan)
    
    # 5. Cash Flow Forecast
    if forecast and forecast.get("cashflow_forecast"):
        charts["cashflow_forecast"] = create_cashflow_forecast_chart(forecast)

    return charts


def create_spending_pie_chart(transactions: List) -> str:
    """Pie chart - Spending by Category"""
    from collections import defaultdict
    category_totals = defaultdict(float)
    
    for t in transactions:
        if t.amount < 0:  # Only expenses
            cat = t.category or "Others"
            category_totals[cat] += abs(t.amount)
    
    if not category_totals:
        return None
    
    df = pd.DataFrame({
        "Category": list(category_totals.keys()),
        "Amount": list(category_totals.values())
    })
    
    fig = px.pie(
        df, 
        names="Category", 
        values="Amount",
        title="Spending Breakdown by Category",
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Plasma
    )
    
    fig.update_traces(textinfo='percent+label', textfont_size=13)
    return save_chart(fig, "spending_pie")


def create_spending_bar_chart(transactions: List) -> str:
    """Bar chart - Top spending categories"""
    from collections import defaultdict
    category_totals = defaultdict(float)
    
    for t in transactions:
        if t.amount < 0:
            cat = t.category or "Others"
            category_totals[cat] += abs(t.amount)
    
    df = pd.DataFrame({
        "Category": list(category_totals.keys()),
        "Amount (LKR)": list(category_totals.values())
    }).sort_values("Amount (LKR)", ascending=False).head(8)
    
    fig = px.bar(
        df,
        x="Category",
        y="Amount (LKR)",
        title="Top Spending Categories",
        text_auto=True,
        color="Amount (LKR)",
        color_continuous_scale="Blues"
    )
    
    fig.update_layout(xaxis_title="", yaxis_title="Amount (LKR)")
    return save_chart(fig, "spending_bar")


def create_budget_comparison_chart(budget_plan: Dict) -> str:
    """Budget vs Actual comparison chart"""
    comparison = budget_plan.get("comparison", {}).get("details", {})
    
    categories = []
    actuals = []
    budgets = []
    
    for cat, data in comparison.items():
        categories.append(cat)
        actuals.append(data.get("actual", 0))
        budgets.append(data.get("budget", 0))
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Actual Spending", x=categories, y=actuals, marker_color='#FF6B6B'))
    fig.add_trace(go.Bar(name="Budget", x=categories, y=budgets, marker_color='#4ECDC4'))
    
    fig.update_layout(
        title="Budget vs Actual Spending",
        barmode='group',
        xaxis_title="",
        yaxis_title="Amount (LKR)",
        legend_title="Legend"
    )
    
    return save_chart(fig, "budget_comparison")


def create_portfolio_pie_chart(portfolio_data: Dict) -> str:
    """Portfolio Asset Allocation Pie Chart"""
    allocation = portfolio_data.get("portfolio_summary", {}).get("asset_allocation", {})
    
    if not allocation:
        return None
    
    fig = px.pie(
        names=list(allocation.keys()),
        values=list(allocation.values()),
        title="Investment Portfolio Allocation",
        hole=0.3
    )
    
    return save_chart(fig, "portfolio_allocation")


def create_cashflow_forecast_chart(forecast: Dict) -> str:
    """Cash Flow Projection Chart"""
    cf = forecast.get("cashflow_forecast", {})
    
    months = ["Now", "3M", "6M", "12M", "24M", "36M"]
    savings = [
        0,
        cf.get("projected_savings_6m", 0) * 0.25,
        cf.get("projected_savings_6m", 0),
        cf.get("projected_savings_12m", 0),
        cf.get("projected_savings_12m", 0) * 1.8,
        cf.get("projected_savings_36m", 0)
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months,
        y=savings,
        mode='lines+markers',
        name='Projected Savings',
        line=dict(color='#22C55E', width=4),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="Cash Flow & Savings Projection",
        xaxis_title="Time Horizon",
        yaxis_title="Projected Savings (LKR)",
        template="plotly_white"
    )
    
    return save_chart(fig, "cashflow_forecast")


def save_chart(fig, name: str) -> str:
    """Save chart as HTML + PNG and return path"""
    os.makedirs("charts", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    html_path = f"charts/{name}_{timestamp}.html"
    png_path = f"charts/{name}_{timestamp}.png"
    
    # Save interactive HTML
    fig.write_html(html_path)
    
    # Save static image
    try:
        fig.write_image(png_path, width=800, height=500)
        return png_path  # Prefer static image for reports
    except:
        return html_path  # Fallback


# Utility function for Streamlit
def display_chart_in_streamlit(chart_path: str):
    """Helper to display saved charts in Streamlit"""
    import streamlit as st
    if chart_path.endswith(".png"):
        st.image(chart_path)
    else:
        with open(chart_path, "r", encoding="utf-8") as f:
            st.components.v1.html(f.read(), height=500)