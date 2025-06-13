from app.agents.base_agent import BaseAgent
from typing import Dict, Any

class DeveloperAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Developer",
            role="Senior Software Developer",
            goal="Provide technical feasibility analysis and implementation recommendations",
            backstory="""You are an experienced software developer with expertise in system architecture, 
            technology selection, and implementation planning. You have worked on numerous projects across 
            different domains and are skilled in evaluating technical requirements, recommending appropriate 
            technologies, and creating realistic implementation timelines.""",
            agent_type="developer"
        )

    async def analyze_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the project from a technical development perspective."""
        analysis = {
            'technical_feasibility': await self._analyze_technical_feasibility(project_data),
            'architecture_recommendation': await self._recommend_architecture(project_data),
            'technology_stack': await self._suggest_technology_stack(project_data),
            'implementation_plan': await self._create_implementation_plan(project_data)
        }
        return analysis

    async def _analyze_technical_feasibility(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze technical feasibility of the project."""
        system_prompt = """You are a senior software developer with extensive experience in technical feasibility analysis.
        Your task is to evaluate the technical feasibility of a project. Consider:
        1. Technical complexity and challenges
        2. Resource requirements
        3. Technology constraints
        4. Integration challenges
        5. Scalability considerations
        6. Performance requirements
        
        Provide a detailed, realistic assessment of technical feasibility."""

        prompt = f"""Analyze the technical feasibility for:
        
        Title: {project_data['title']}
        Description: {project_data['description']}
        Requirements: {project_data['requirements']}
        Constraints: {project_data['constraints']}
        Timeline: {project_data['timeline']}
        Budget: {project_data['budget']}
        
        Additional Context: {project_data.get('pm_insights', 'No additional context')}
        
        Provide:
        1. Technical complexity assessment
        2. Key technical challenges
        3. Resource requirements
        4. Feasibility rating (1-10)
        5. Risk factors
        6. Recommendations for success"""

        feasibility = await self.get_llm_response(prompt, system_prompt)
        return {
            'complexity': feasibility,
            'challenges': feasibility,
            'feasibility_score': feasibility
        }

    async def _recommend_architecture(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend system architecture."""
        system_prompt = """You are a system architect with expertise in designing scalable, maintainable systems.
        Your task is to recommend an appropriate system architecture. Consider:
        1. System requirements and constraints
        2. Scalability needs
        3. Performance requirements
        4. Security considerations
        5. Maintainability
        6. Cost effectiveness
        
        Provide specific architectural recommendations with justifications."""

        prompt = f"""Recommend system architecture for:
        
        Title: {project_data['title']}
        Description: {project_data['description']}
        Requirements: {project_data['requirements']}
        Constraints: {project_data['constraints']}
        
        Include:
        1. Overall architecture pattern (microservices, monolith, etc.)
        2. System components and their interactions
        3. Data architecture
        4. Security architecture
        5. Deployment architecture
        6. Justification for choices"""

        architecture = await self.get_llm_response(prompt, system_prompt)
        return {
            'architecture': architecture,
            'components': architecture,
            'justification': architecture
        }

    async def _suggest_technology_stack(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest appropriate technology stack."""
        system_prompt = """You are a technology consultant with deep knowledge of various tech stacks.
        Your task is to recommend the most suitable technology stack. Consider:
        1. Project requirements
        2. Team expertise
        3. Scalability needs
        4. Performance requirements
        5. Development speed
        6. Long-term maintainability
        
        Provide specific technology recommendations with rationale."""

        prompt = f"""Suggest technology stack for:
        
        Title: {project_data['title']}
        Description: {project_data['description']}
        Requirements: {project_data['requirements']}
        Constraints: {project_data['constraints']}
        
        Recommend:
        1. Backend technologies (languages, frameworks)
        2. Frontend technologies
        3. Database solutions
        4. Infrastructure and deployment
        5. Development tools
        6. Third-party services
        7. Rationale for each choice"""

        tech_stack = await self.get_llm_response(prompt, system_prompt)
        return {
            'backend': tech_stack,
            'frontend': tech_stack,
            'database': tech_stack,
            'infrastructure': tech_stack
        }

    async def _create_implementation_plan(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed implementation plan."""
        system_prompt = """You are a project lead with expertise in implementation planning and project management.
        Your task is to create a detailed implementation plan. Consider:
        1. Project phases and milestones
        2. Task dependencies
        3. Resource allocation
        4. Risk mitigation
        5. Quality assurance
        6. Delivery timeline
        
        Provide a comprehensive, actionable implementation plan."""

        prompt = f"""Create implementation plan for:
        
        Title: {project_data['title']}
        Description: {project_data['description']}
        Requirements: {project_data['requirements']}
        Timeline: {project_data['timeline']}
        Budget: {project_data['budget']}
        
        Include:
        1. Development phases
        2. Key milestones
        3. Task breakdown
        4. Timeline estimates
        5. Resource requirements
        6. Risk mitigation strategies
        7. Quality gates"""

        plan = await self.get_llm_response(prompt, system_prompt)
        return {
            'phases': plan,
            'milestones': plan,
            'timeline': plan,
            'resources': plan
        }

    def format_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format the analysis results for storage."""
        formatted = f"""
        Developer Analysis:
        
        Technical Feasibility:
        {analysis['technical_feasibility']}
        
        Architecture Recommendation:
        {analysis['architecture_recommendation']}
        
        Technology Stack:
        {analysis['technology_stack']}
        
        Implementation Plan:
        {analysis['implementation_plan']}
        """
        return formatted 