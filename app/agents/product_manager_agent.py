from app.agents.base_agent import BaseAgent
from typing import Dict, Any

class ProductManagerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Product Manager",
            role="Lead Product Manager",
            goal="Create comprehensive product strategies and ensure successful project execution",
            backstory="""You are an experienced Product Manager with a track record of successful product launches.
            You excel at understanding market needs, defining product requirements, and coordinating cross-functional teams.
            Your expertise lies in balancing business objectives with technical feasibility while ensuring user satisfaction.""",
            agent_type="product_manager"
        )

    async def analyze_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the project from a product management perspective."""
        analysis = {
            'market_analysis': await self._analyze_market(project_data),
            'product_strategy': await self._create_product_strategy(project_data),
            'success_metrics': await self._define_success_metrics(project_data),
            'risk_assessment': await self._assess_risks(project_data)
        }
        return analysis

    async def _analyze_market(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market opportunities and competition."""
        system_prompt = """You are an expert market analyst with deep experience in product strategy and market research.
        Your task is to analyze the market opportunity for a new product. Consider:
        1. Target market size and growth potential
        2. Key competitors and their strengths/weaknesses
        3. Market trends and opportunities
        4. Potential barriers to entry
        5. Unique value proposition opportunities
        
        Provide a detailed, data-driven analysis that can inform product strategy."""

        prompt = f"""Analyze the market opportunity for the following product:
        
        Title: {project_data['title']}
        Description: {project_data['description']}
        Requirements: {project_data['requirements']}
        Constraints: {project_data['constraints']}
        
        Provide a comprehensive market analysis including:
        1. Market size and growth potential
        2. Competitive landscape
        3. Market trends
        4. Target audience segments
        5. Key differentiators
        6. Market entry strategy recommendations"""

        analysis = await self.get_llm_response(prompt, system_prompt)
        return {
            'market_size': analysis,
            'target_audience': analysis,
            'competition': analysis,
            'market_trends': analysis
        }

    async def _create_product_strategy(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a comprehensive product strategy."""
        system_prompt = """You are a strategic product leader with expertise in product strategy and roadmap development.
        Your task is to create a comprehensive product strategy that aligns with business goals and market opportunities.
        Consider:
        1. Product vision and goals
        2. Key features and priorities
        3. Go-to-market strategy
        4. Resource requirements
        5. Timeline and milestones
        
        Provide a detailed, actionable strategy that can guide product development."""

        prompt = f"""Create a comprehensive product strategy for:
        
        Title: {project_data['title']}
        Description: {project_data['description']}
        Requirements: {project_data['requirements']}
        Constraints: {project_data['constraints']}
        Timeline: {project_data['timeline']}
        Budget: {project_data['budget']}
        
        Include:
        1. Product vision and goals
        2. Key features and priorities
        3. Go-to-market strategy
        4. Resource requirements
        5. Timeline and milestones
        6. Success criteria"""

        strategy = await self.get_llm_response(prompt, system_prompt)
        return {
            'vision': strategy,
            'goals': strategy,
            'key_features': strategy,
            'timeline': strategy
        }

    async def _define_success_metrics(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Define key success metrics for the project."""
        system_prompt = """You are an expert in product metrics and KPIs with experience in defining and measuring product success.
        Your task is to define clear, measurable success metrics that align with business objectives.
        Consider:
        1. Business metrics (revenue, growth, etc.)
        2. User metrics (engagement, satisfaction, etc.)
        3. Technical metrics (performance, reliability, etc.)
        4. Market metrics (adoption, market share, etc.)
        
        Provide specific, measurable metrics with target values."""

        prompt = f"""Define success metrics for:
        
        Title: {project_data['title']}
        Description: {project_data['description']}
        Requirements: {project_data['requirements']}
        
        Include:
        1. Key Performance Indicators (KPIs)
        2. Target values for each metric
        3. Measurement methodology
        4. Success criteria
        5. Monitoring and reporting recommendations"""

        metrics = await self.get_llm_response(prompt, system_prompt)
        return {
            'kpis': metrics,
            'targets': metrics,
            'measurement_methods': metrics
        }

    async def _assess_risks(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess potential risks and mitigation strategies."""
        system_prompt = """You are a risk management expert with experience in product development and market analysis.
        Your task is to identify potential risks and develop mitigation strategies.
        Consider:
        1. Market risks
        2. Technical risks
        3. Operational risks
        4. Financial risks
        5. Regulatory risks
        
        Provide a detailed risk assessment with specific mitigation strategies."""

        prompt = f"""Assess risks for:
        
        Title: {project_data['title']}
        Description: {project_data['description']}
        Requirements: {project_data['requirements']}
        Constraints: {project_data['constraints']}
        Timeline: {project_data['timeline']}
        Budget: {project_data['budget']}
        
        Include:
        1. Risk identification
        2. Impact assessment
        3. Probability assessment
        4. Mitigation strategies
        5. Contingency plans
        6. Risk monitoring recommendations"""

        risks = await self.get_llm_response(prompt, system_prompt)
        return {
            'risks': risks,
            'impact': risks,
            'mitigation_strategies': risks
        }

    def format_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format the analysis results for storage."""
        formatted = f"""
        Product Manager Analysis:
        
        Market Analysis:
        {analysis['market_analysis']}
        
        Product Strategy:
        {analysis['product_strategy']}
        
        Success Metrics:
        {analysis['success_metrics']}
        
        Risk Assessment:
        {analysis['risk_assessment']}
        """
        return formatted 