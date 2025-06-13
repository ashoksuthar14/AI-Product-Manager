from app.agents.base_agent import BaseAgent
from typing import Dict, Any

class QAAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="QA Engineer",
            role="Senior QA Engineer",
            goal="Develop comprehensive testing strategies and quality assurance plans",
            backstory="""You are a senior QA engineer with extensive experience in software testing and quality assurance.
            You excel at identifying potential issues, creating test strategies, and ensuring product quality.
            Your expertise includes test automation, performance testing, security testing, and user acceptance testing.""",
            agent_type="qa"
        )

    async def analyze_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the project from a QA perspective."""
        analysis = {
            'test_strategy': await self._create_test_strategy(project_data),
            'quality_metrics': await self._define_quality_metrics(project_data),
            'test_plan': await self._create_test_plan(project_data),
            'risk_assessment': await self._assess_quality_risks(project_data)
        }
        return analysis

    async def _create_test_strategy(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive test strategy."""
        system_prompt = """You are an expert in software testing and quality assurance.
        Your task is to create a comprehensive test strategy that ensures product quality.
        Consider:
        1. Testing levels and types
        2. Test automation approach
        3. Performance testing requirements
        4. Security testing needs
        5. User acceptance criteria
        
        Provide a detailed test strategy that covers all quality aspects."""

        prompt = f"""Create test strategy for:
        
        Title: {project_data['title']}
        Description: {project_data['description']}
        Requirements: {project_data['requirements']}
        Constraints: {project_data['constraints']}
        
        Include:
        1. Testing approach and methodology
        2. Test levels (unit, integration, system, acceptance)
        3. Test types (functional, performance, security, etc.)
        4. Test automation strategy
        5. Test environment requirements
        6. Test data management
        7. Quality gates and criteria"""

        strategy = await self.get_llm_response(prompt, system_prompt)
        return {
            'approach': strategy,
            'levels': strategy,
            'types': strategy,
            'automation': strategy
        }

    async def _define_quality_metrics(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Define quality metrics and KPIs."""
        system_prompt = """You are an expert in software quality metrics and measurement.
        Your task is to define clear, measurable quality metrics that ensure product excellence.
        Consider:
        1. Code quality metrics
        2. Test coverage metrics
        3. Performance metrics
        4. User satisfaction metrics
        5. Defect metrics
        
        Provide specific, measurable quality metrics with target values."""

        prompt = f"""Define quality metrics for:
        
        Title: {project_data['title']}
        Description: {project_data['description']}
        Requirements: {project_data['requirements']}
        
        Include:
        1. Code quality metrics
        2. Test coverage requirements
        3. Performance benchmarks
        4. User satisfaction metrics
        5. Defect tracking metrics
        6. Quality gates and thresholds
        7. Measurement methodology"""

        metrics = await self.get_llm_response(prompt, system_prompt)
        return {
            'code_quality': metrics,
            'test_coverage': metrics,
            'performance': metrics,
            'user_satisfaction': metrics
        }

    async def _create_test_plan(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed test plan."""
        system_prompt = """You are an expert in test planning and execution.
        Your task is to create a detailed test plan that ensures comprehensive testing coverage.
        Consider:
        1. Test scope and objectives
        2. Test schedule and resources
        3. Test environment setup
        4. Test case development
        5. Test execution approach
        
        Provide a comprehensive test plan with clear timelines and responsibilities."""

        prompt = f"""Create test plan for:
        
        Title: {project_data['title']}
        Description: {project_data['description']}
        Requirements: {project_data['requirements']}
        Timeline: {project_data['timeline']}
        
        Include:
        1. Test objectives and scope
        2. Test schedule and milestones
        3. Resource requirements
        4. Test environment setup
        5. Test case development approach
        6. Test execution strategy
        7. Defect management process
        8. Test reporting and metrics"""

        plan = await self.get_llm_response(prompt, system_prompt)
        return {
            'objectives': plan,
            'schedule': plan,
            'resources': plan,
            'execution': plan
        }

    async def _assess_quality_risks(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess quality-related risks."""
        system_prompt = """You are an expert in quality risk assessment and mitigation.
        Your task is to identify potential quality risks and develop mitigation strategies.
        Consider:
        1. Technical risks
        2. Process risks
        3. Resource risks
        4. Schedule risks
        5. User acceptance risks
        
        Provide a detailed risk assessment with specific mitigation strategies."""

        prompt = f"""Assess quality risks for:
        
        Title: {project_data['title']}
        Description: {project_data['description']}
        Requirements: {project_data['requirements']}
        Constraints: {project_data['constraints']}
        Timeline: {project_data['timeline']}
        
        Include:
        1. Quality risk identification
        2. Impact assessment
        3. Probability assessment
        4. Mitigation strategies
        5. Contingency plans
        6. Risk monitoring approach
        7. Early warning indicators"""

        risks = await self.get_llm_response(prompt, system_prompt)
        return {
            'risks': risks,
            'impact': risks,
            'mitigation': risks,
            'monitoring': risks
        }

    def format_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format the analysis results for storage."""
        formatted = f"""
        QA Engineer Analysis:
        
        Test Strategy:
        {analysis['test_strategy']}
        
        Quality Metrics:
        {analysis['quality_metrics']}
        
        Test Plan:
        {analysis['test_plan']}
        
        Quality Risk Assessment:
        {analysis['risk_assessment']}
        """
        return formatted 