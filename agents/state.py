from typing import TypedDict, Annotated, List, Dict, Optional
import operator
from pydantic import BaseModel

class Transaction(BaseModel):
    date: str
    description: str
    amount: float
    category: Optional[str] = None
    currency: str = "LKR"

class AgentState(TypedDict, total=False):  # ← total=False makes all fields optional
    # Messages for conversation history
    messages: Annotated[list, operator.add]
    
    # User context
    user_goals: List[str]
    user_profile: Dict
    
    # Data flow
    raw_documents: List[Dict]
    transactions: List[Transaction]
    categorized_transactions: List[Transaction]
    
    # Agent outputs
    spending_analysis: Dict
    budget_plan: Dict
    investment_analysis: Dict
    forecast_results: Dict
    recommendations: List[Dict]
    
    # Control flow
    next: str
    error: str