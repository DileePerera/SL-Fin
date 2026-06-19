import sys
import os
from pathlib import Path

# GPU Optimization
os.environ["OLLAMA_FLASH_ATTENTION"] = "1"
os.environ["OLLAMA_NUM_PARALLEL"] = "1"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
# Fix import path
current_dir = Path(__file__).parent.absolute()
project_root = current_dir.parent.absolute()
sys.path.insert(0, str(project_root))

import streamlit as st
import pandas as pd
from datetime import datetime

# Import project modules
from agents.supervisor import build_finance_graph
from agents.state import AgentState
from tools.visualizer import display_chart_in_streamlit

st.set_page_config(
    page_title="Local Finance Agent",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🧠 Local Finance Agent")
st.caption("Your Private AI-Powered Personal CFO | 100% Local & Private")

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("📤 Data Input")
    
    # === Sample Data Button ===
    st.subheader("🧪 Try Sample Data")
    if st.button("Load Commercial Bank Sample", use_container_width=True, type="secondary"):
        with st.spinner("Loading sample data..."):
            sample_file = "data/sample_statements/commercial_bank_sample.csv"
            if os.path.exists(sample_file):
                st.session_state['sample_loaded'] = True
                st.session_state['sample_path'] = sample_file
                st.success("✅ Sample data loaded!")
            else:
                st.error("❌ Sample file not found. Please create `data/sample_statements/commercial_bank_sample.csv`")

    st.divider()

    st.header("📤 Upload Your Statements")
    uploaded_files = st.file_uploader(
        "CSV, PDF, or Excel files",
        type=['csv', 'pdf', 'xlsx', 'xls'],
        accept_multiple_files=True
    )
    
    st.divider()
    
    st.header("🎯 Your Goals")
    user_goals = st.text_area(
        "Enter your financial goals (one per line)",
        placeholder="Buy a house in Malabe in 3 years\nBuild 2 million LKR emergency fund\nRetire at 55",
        height=100
    )
    
    risk_tolerance = st.selectbox(
        "Risk Tolerance", ["Low", "Medium", "High"], index=1
    )

    analyze_button = st.button("🚀 Analyze My Finances", type="primary", use_container_width=True)

# ====================== ANALYSIS ======================
if analyze_button or st.session_state.get('sample_loaded'):
    with st.spinner("🤖 Running multi-agent analysis using local models..."):
        
        file_paths = []
        
        # Sample data
        if st.session_state.get('sample_loaded'):
            file_paths.append({
                "file_path": st.session_state.get('sample_path'),
                "file_type": "csv"
            })
        
        # Uploaded files
        elif uploaded_files:
            os.makedirs("data/user_data", exist_ok=True)
            for file in uploaded_files:
                save_path = f"data/user_data/{file.name}"
                with open(save_path, "wb") as f:
                    f.write(file.getbuffer())
                file_paths.append({
                    "file_path": save_path,
                    "file_type": file.name.split('.')[-1].lower()
                })

        if not file_paths:
            st.error("Please load sample data or upload files.")
        else:
            initial_state: AgentState = {
                "messages": [],
                "user_goals": [g.strip() for g in user_goals.split('\n') if g.strip()],
                "user_profile": {"risk_tolerance": risk_tolerance},
                "raw_documents": file_paths,
                "transactions": [],
                "next": "ingestion"
            }
            
            try:
                graph = build_finance_graph()
                result = graph.invoke(initial_state)
                
                st.session_state['analysis_result'] = result
                st.success("✅ Analysis completed successfully!")
                st.balloons()
            except Exception as e:
                st.error(f"Error during analysis: {e}")

# ====================== RESULTS ======================
if 'analysis_result' in st.session_state:
    result = st.session_state['analysis_result']
    report = result.get("report", {})
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", "📉 Spending", "💰 Budget", "📈 Forecast", "📋 Full Report"
    ])
    
    with tab1:
        st.subheader("Financial Health Overview")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Savings Rate", f"{report.get('financial_health', {}).get('savings_rate', 0)}%")
        with col2:
            st.metric("Transactions", report.get('spending_analysis', {}).get('total_transactions', 0))
        with col3:
            st.metric("Est. Monthly Income", f"Rs. {report.get('budget_analysis', {}).get('total_monthly_income', 0):,}")
        with col4:
            st.metric("Health Score", f"{report.get('financial_health', {}).get('overall_score', 0)}/100")
        
        st.subheader("Executive Summary")
        st.write(report.get("executive_summary", "No summary available."))

    with tab2:
        st.subheader("Spending Analysis")
        spending = result.get("spending_analysis", {})
        if spending.get("chart_path"):
            display_chart_in_streamlit(spending.get("chart_path"))

    with tab3:
        st.subheader("Budget Analysis")
        if "charts" in report and "budget_vs_actual" in report["charts"]:
            display_chart_in_streamlit(report["charts"]["budget_vs_actual"])

    with tab4:
        st.subheader("Forecast")
        if "charts" in report and "cashflow_forecast" in report["charts"]:
            display_chart_in_streamlit(report["charts"]["cashflow_forecast"])

    with tab5:
        st.subheader("Full Detailed Report")
        st.json(report, expanded=False)

else:
    st.info("👈 Start by loading the sample data or uploading your bank statements.")

# Footer
st.divider()
st.markdown(
    "<p style='text-align: center; color: #64748B;'>"
    "Local Finance Agent • Open Source • Built for Sri Lanka"
    "</p>",
    unsafe_allow_html=True
)