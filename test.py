# debug.py
import sys
sys.path.insert(0, r"C:\SL-Fin")

from agents.state import AgentState
from langchain_core.messages import HumanMessage

# Test each node individually
initial_state = {
    "messages": [],
    "user_goals": [],
    "user_profile": {"risk_tolerance": "Medium"},
    "raw_documents": [{"file_path": "data/sample_statements/commercial_bank_sample.csv", "file_type": "csv"}],
    "transactions": [],
    "next": "ingestion"
}

print("Testing ingestion_node...")
from agents.ingestion_agent import ingestion_node
result = ingestion_node(initial_state)
print(f"Type: {type(result)}, Value preview: {str(result)[:200]}")
print()

print("Testing analysis_node...")
from agents.analysis_agent import analysis_node
result2 = analysis_node({**initial_state, **result})
print(f"Type: {type(result2)}, Value preview: {str(result2)[:200]}")
print()

print("Testing supervisor_node...")
from agents.supervisor import supervisor_node
result3 = supervisor_node({**initial_state, **result, **result2})
print(f"Type: {type(result3)}, Value preview: {str(result3)[:200]}")

# Add to debug.py
print("Testing budget_node...")
from agents.budget_agent import budget_node
merged = {**initial_state, **result, **result2, **result3}
result4 = budget_node(merged)
print(f"Type: {type(result4)}, Value: {str(result4)[:200]}")

print("Testing report_node...")
from agents.report_agent import report_node
result5 = report_node({**merged, **result4})
print(f"Type: {type(result5)}, Value: {str(result5)[:200]}")