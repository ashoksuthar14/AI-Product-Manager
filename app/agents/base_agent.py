from typing import List, Dict, Any
from app.llm.llm_client import LLMClient

class BaseAgent:
    def __init__(self, name: str, role: str, goal: str, backstory: str, agent_type: str):
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.agent_type = agent_type
        self.llm_client = LLMClient()

    async def analyze_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the project and return recommendations."""
        raise NotImplementedError("Subclasses must implement analyze_project method")

    def format_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format the analysis results for storage."""
        raise NotImplementedError("Subclasses must implement format_analysis method")

    async def get_llm_response(self, prompt: str, system_prompt: str = None) -> str:
        """Get response from the appropriate LLM for this agent."""
        return await self.llm_client.get_agent_response(
            self.agent_type,
            prompt,
            system_prompt
        ) 