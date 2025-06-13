from app.agents.base_agent import BaseAgent
from typing import Dict, Any

class AIEngineerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="AI Engineer",
            role="Senior AI/ML Engineer",
            goal="Provide AI/ML implementation guidance and model recommendations",
            backstory="""You are a senior AI/ML engineer with extensive experience in implementing
            artificial intelligence and machine learning solutions. You excel at evaluating AI requirements,
            selecting appropriate models, and designing scalable AI systems. Your expertise includes
            deep learning, natural language processing, computer vision, and reinforcement learning.""",
            agent_type="ai_engineer"
        )

    async def analyze_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the project from an AI/ML perspective."""
        analysis = {
            'ai_requirements': await self._analyze_ai_requirements(project_data),
            'model_recommendations': await self._recommend_models(project_data),
            'implementation_strategy': await self._create_implementation_strategy(project_data),
            'infrastructure_requirements': await self._assess_infrastructure_needs(project_data)
        }
        return analysis

    async def _analyze_ai_requirements(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze AI/ML requirements."""
        system_prompt = """You are an expert in AI/ML requirements analysis and system design.
        Your task is to analyze the AI/ML requirements and determine the best approach.
        Consider:
        1. Problem type and complexity
        2. Data requirements and availability
        3. Performance requirements
        4. Integration needs
        5. Scalability requirements
        
        Provide a detailed analysis of AI/ML requirements and feasibility."""

        prompt = f"""Analyze AI/ML requirements for:
        
        Title: {project_data['title']}
        Description: {project_data['description']}
        Requirements: {project_data['requirements']}
        Constraints: {project_data['constraints']}
        
        Include:
        1. Problem classification
        2. Data requirements
        3. Model requirements
        4. Performance criteria
        5. Integration requirements
        6. Scalability needs
        7. Ethical considerations"""

        requirements = await self.get_llm_response(prompt, system_prompt)
        return {
            'problem_analysis': requirements,
            'data_requirements': requirements,
            'model_requirements': requirements,
            'performance_requirements': requirements
        }

    async def _recommend_models(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend appropriate AI/ML models."""
        system_prompt = """You are an expert in AI/ML model selection and evaluation.
        Your task is to recommend appropriate models for the project requirements.
        Consider:
        1. Problem type and complexity
        2. Data characteristics
        3. Performance requirements
        4. Resource constraints
        5. Deployment environment
        
        Provide detailed model recommendations with justification."""

        prompt = f"""Recommend AI/ML models for:
        
        Title: {project_data['title']}
        Description: {project_data['description']}
        Requirements: {project_data['requirements']}
        Constraints: {project_data['constraints']}
        
        Include:
        1. Model types and architectures
        2. Pre-trained models (if applicable)
        3. Custom model requirements
        4. Model evaluation criteria
        5. Performance benchmarks
        6. Resource requirements
        7. Justification for each recommendation"""

        models = await self.get_llm_response(prompt, system_prompt)
        return {
            'model_types': models,
            'architectures': models,
            'evaluation': models,
            'benchmarks': models
        }

    async def _create_implementation_strategy(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create AI/ML implementation strategy."""
        system_prompt = """You are an expert in AI/ML implementation and deployment.
        Your task is to create a comprehensive implementation strategy.
        Consider:
        1. Development approach
        2. Data pipeline design
        3. Model training strategy
        4. Evaluation methodology
        5. Deployment approach
        
        Provide a detailed implementation strategy with clear steps and timelines."""

        prompt = f"""Create AI/ML implementation strategy for:
        
        Title: {project_data['title']}
        Description: {project_data['description']}
        Requirements: {project_data['requirements']}
        Timeline: {project_data['timeline']}
        
        Include:
        1. Development phases
        2. Data pipeline design
        3. Model training approach
        4. Evaluation methodology
        5. Deployment strategy
        6. Monitoring and maintenance
        7. Resource requirements"""

        strategy = await self.get_llm_response(prompt, system_prompt)
        return {
            'phases': strategy,
            'data_pipeline': strategy,
            'training': strategy,
            'deployment': strategy
        }

    async def _assess_infrastructure_needs(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess AI/ML infrastructure requirements."""
        system_prompt = """You are an expert in AI/ML infrastructure and deployment.
        Your task is to assess infrastructure requirements for AI/ML implementation.
        Consider:
        1. Computing resources
        2. Storage requirements
        3. Network needs
        4. Deployment environment
        5. Scaling requirements
        
        Provide a detailed infrastructure assessment with specific recommendations."""

        prompt = f"""Assess infrastructure needs for:
        
        Title: {project_data['title']}
        Description: {project_data['description']}
        Requirements: {project_data['requirements']}
        Constraints: {project_data['constraints']}
        
        Include:
        1. Computing requirements
        2. Storage needs
        3. Network requirements
        4. Deployment environment
        5. Scaling strategy
        6. Cost considerations
        7. Security requirements"""

        infrastructure = await self.get_llm_response(prompt, system_prompt)
        return {
            'computing': infrastructure,
            'storage': infrastructure,
            'network': infrastructure,
            'deployment': infrastructure
        }

    def format_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format the analysis results for storage."""
        formatted = f"""
        AI Engineer Analysis:
        
        AI/ML Requirements:
        {analysis['ai_requirements']}
        
        Model Recommendations:
        {analysis['model_recommendations']}
        
        Implementation Strategy:
        {analysis['implementation_strategy']}
        
        Infrastructure Requirements:
        {analysis['infrastructure_requirements']}
        """
        return formatted 