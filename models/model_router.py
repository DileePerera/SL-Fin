"""
Model Router - Optimized for RTX 3050 4GB Laptop GPU
"""

from typing import Optional
from langchain_ollama import ChatOllama
import os


class ModelRouter:
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        # Optimized for 4GB VRAM
        self.models = {
            "fast": {
                "name": os.getenv("FAST_MODEL", "llama3.1:8b"),
                "temperature": 0.1,
                "num_ctx": 8192,
                "description": "Fastest - for simple & quick tasks"
            },
            "balanced": {
                "name": os.getenv("DEFAULT_MODEL", "llama3.1:8b"),
                "temperature": 0.1,
                "num_ctx": 8192,
                "description": "Best balance for most tasks"
            },
            "strong": {
                "name": os.getenv("STRONG_MODEL", "llama3.1:8b"),   # Do NOT use 32B here
                "temperature": 0.05,
                "num_ctx": 8192,
                "description": "Strong reasoning (still 8b on 4GB)"
            },
            "creative": {
                "name": os.getenv("CREATIVE_MODEL", "llama3.1:8b"),
                "temperature": 0.6,
                "num_ctx": 8192,
                "description": "For writing summaries & reports"
            }
        }

    def get_llm(self, task_type: str = "balanced", temperature: Optional[float] = None) -> ChatOllama:
        if task_type not in self.models:
            task_type = "balanced"

        config = self.models[task_type]
        
        return ChatOllama(
            model=config["name"],
            temperature=temperature if temperature is not None else config["temperature"],
            base_url=self.base_url,
            num_ctx=config["num_ctx"],
            # GPU Performance Settings
            top_p=0.9,
            top_k=40,
            # Important for GPU usage
            # ollama will automatically use GPU if available
        )

    def get_model_name(self, task_type: str = "balanced") -> str:
        return self.models.get(task_type, self.models["balanced"])["name"]

    def route_task(self, task_description: str) -> str:
        """Route tasks intelligently"""
        text = task_description.lower()
        
        if any(word in text for word in ["calculate", "forecast", "monte", "budget", "sum", "average", "percentage"]):
            return "strong"
        elif any(word in text for word in ["write", "summary", "report", "recommend", "insight", "executive"]):
            return "creative"
        elif any(word in text for word in ["categorize", "parse", "extract", "list"]):
            return "fast"
        else:
            return "balanced"


# Global instance
router = ModelRouter()

# Convenience functions
def get_llm(task_type: str = "balanced", temperature: Optional[float] = None):
    return router.get_llm(task_type, temperature)

def get_fast_llm():
    return router.get_llm("fast")

def get_strong_llm():
    return router.get_llm("strong")

def get_creative_llm():
    return router.get_llm("creative")