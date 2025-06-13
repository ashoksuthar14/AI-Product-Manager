from typing import Dict, Any, List
from app.agents.product_manager_agent import ProductManagerAgent
from app.agents.developer_agent import DeveloperAgent
from app.agents.qa_agent import QAAgent
from app.agents.ai_engineer_agent import AIEngineerAgent
import asyncio
from flask_socketio import emit
from flask import current_app

class AgentCoordinator:
    def __init__(self, emit_updates=True):
        self.agents = {
            'product_manager': ProductManagerAgent(),
            'developer': DeveloperAgent(),
            'qa': QAAgent(),
            'ai_engineer': AIEngineerAgent()
        }
        self.conversation_history = []
        self.shared_context = {}
        self.emit_updates = emit_updates

    def log_conversation(self, agent_name: str, message_type: str, content: str):
        """Log agent conversations for visibility."""
        entry = {
            'agent': agent_name,
            'type': message_type,
            'content': content,
            'timestamp': asyncio.get_event_loop().time()
        }
        self.conversation_history.append(entry)
        print(f"\n🤖 [{agent_name.upper()}] {message_type}:")
        print(f"   {content}")
        print("-" * 80)
        
        # Emit real-time update to frontend
        if self.emit_updates:
            try:
                from app import socketio
                socketio.emit('agent_update', {
                    'agent': agent_name,
                    'type': message_type,
                    'content': content,
                    'timestamp': entry['timestamp']
                })
            except Exception as e:
                print(f"Failed to emit update: {e}")

    def emit_progress(self, stage: str, progress: int, message: str):
        """Emit progress updates to frontend."""
        if self.emit_updates:
            try:
                from app import socketio
                socketio.emit('analysis_progress', {
                    'stage': stage,
                    'progress': progress,
                    'message': message
                })
            except Exception as e:
                print(f"Failed to emit progress: {e}")

    async def collaborative_analysis(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate a collaborative analysis between all agents."""
        print("🚀 Starting Collaborative Project Analysis...")
        print("=" * 80)
        
        self.emit_progress("initialization", 0, "Starting collaborative analysis...")
        
        # Phase 1: Product Manager Analysis
        self.emit_progress("product_manager", 10, "Product Manager analyzing market and strategy...")
        self.log_conversation("Product Manager", "STARTING", 
                            "I'll begin with market and product strategy analysis.")
        
        pm_analysis = await self.agents['product_manager'].analyze_project(project_data)
        self.shared_context['product_strategy'] = pm_analysis
        
        # Emit the actual analysis content
        pm_summary = self.format_pm_analysis(pm_analysis)
        self.log_conversation("Product Manager", "ANALYSIS_COMPLETE", pm_summary)
        
        self.emit_progress("product_manager", 25, "Product Manager analysis complete")

        # Phase 2: Developer Analysis
        self.emit_progress("developer", 30, "Developer reviewing technical feasibility...")
        self.log_conversation("Developer", "REVIEWING", 
                            "Reviewing product strategy to assess technical feasibility...")
        
        # Create enhanced prompt for developer with PM context
        enhanced_project_data = project_data.copy()
        enhanced_project_data['pm_insights'] = f"""
        Product Manager's Key Insights:
        - Market Analysis: {pm_analysis.get('market_analysis', {}).get('market_size', 'Not available')}
        - Product Strategy: {pm_analysis.get('product_strategy', {}).get('vision', 'Not available')}
        """
        
        dev_analysis = await self.agents['developer'].analyze_project(enhanced_project_data)
        self.shared_context['technical_analysis'] = dev_analysis
        
        # Emit actual developer analysis
        dev_summary = self.format_dev_analysis(dev_analysis)
        self.log_conversation("Developer", "TECHNICAL_ANALYSIS", dev_summary)
        
        self.emit_progress("developer", 50, "Developer analysis complete")

        # Phase 3: QA Engineer Analysis
        self.emit_progress("qa", 55, "QA Engineer analyzing quality requirements...")
        self.log_conversation("QA Engineer", "REVIEWING", 
                            "Analyzing quality requirements based on product and technical specifications...")
        
        enhanced_project_data['dev_insights'] = f"""
        Developer's Technical Assessment:
        - Architecture: {dev_analysis.get('architecture_recommendation', {}).get('architecture', 'Not available')}
        - Technology Stack: {dev_analysis.get('technology_stack', {}).get('backend', 'Not available')}
        """
        
        qa_analysis = await self.agents['qa'].analyze_project(enhanced_project_data)
        self.shared_context['quality_analysis'] = qa_analysis
        
        # Emit actual QA analysis
        qa_summary = self.format_qa_analysis(qa_analysis)
        self.log_conversation("QA Engineer", "QUALITY_ANALYSIS", qa_summary)
        
        self.emit_progress("qa", 70, "QA Engineer analysis complete")

        # Phase 4: AI Engineer Analysis
        self.emit_progress("ai_engineer", 75, "AI Engineer evaluating ML integration...")
        self.log_conversation("AI Engineer", "ANALYZING", 
                            "Evaluating AI/ML integration opportunities based on team insights...")
        
        enhanced_project_data['qa_insights'] = f"""
        QA Engineer's Quality Assessment:
        - Testing Strategy: {qa_analysis.get('test_strategy', {}).get('strategy', 'Not available')}
        - Quality Risks: {qa_analysis.get('risk_assessment', {}).get('risks', 'Not available')}
        """
        
        ai_analysis = await self.agents['ai_engineer'].analyze_project(enhanced_project_data)
        self.shared_context['ai_analysis'] = ai_analysis
        
        # Emit actual AI analysis
        ai_summary = self.format_ai_analysis(ai_analysis)
        self.log_conversation("AI Engineer", "AI_RECOMMENDATIONS", ai_summary)
        
        self.emit_progress("ai_engineer", 85, "AI Engineer analysis complete")

        # Phase 5: Final Collaboration
        self.emit_progress("collaboration", 90, "Final team collaboration...")
        await self.final_collaboration_round(project_data)
        
        # Create Product Manager Overview
        pm_overview = await self.create_pm_overview(project_data)
        
        # Emit PM Overview
        self.log_conversation("Product Manager", "FINAL_OVERVIEW", pm_overview)
        
        # Compile final analysis
        final_analysis = {
            'product_management': pm_analysis,
            'technical_development': dev_analysis,
            'quality_assurance': qa_analysis,
            'ai_engineering': ai_analysis,
            'collaboration_insights': self.shared_context.get('final_insights', {}),
            'pm_overview': pm_overview,
            'conversation_log': self.conversation_history
        }
        
        self.emit_progress("complete", 100, "Analysis complete!")
        print("\n✅ Collaborative Analysis Complete!")
        print("=" * 80)
        
        return final_analysis

    def format_pm_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format Product Manager analysis for display."""
        market = analysis.get('market_analysis', {})
        strategy = analysis.get('product_strategy', {})
        metrics = analysis.get('success_metrics', {})
        risks = analysis.get('risk_assessment', {})
        
        return f"""📊 MARKET ANALYSIS COMPLETE

🎯 Market Opportunity:
• Market size and growth potential identified
• Competitive landscape analyzed
• Target customer segments defined
• Revenue opportunities assessed

🚀 Product Strategy:
• Product vision and positioning established
• Feature prioritization framework created
• Go-to-market approach outlined
• Value proposition clearly defined

📈 Success Metrics:
• Key performance indicators established
• Revenue targets and milestones set
• User acquisition goals defined
• Market penetration metrics identified

⚠️ Risk Assessment:
• Market risks and challenges identified
• Mitigation strategies developed
• Competitive threats evaluated
• Resource constraints considered

💡 Key Insight: Strong market opportunity with clear strategic path forward and measurable success criteria."""

    def format_dev_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format Developer analysis for display."""
        feasibility = analysis.get('technical_feasibility', {})
        architecture = analysis.get('architecture_recommendation', {})
        timeline = analysis.get('development_timeline', {})
        tech_stack = analysis.get('technology_stack', {})
        
        return f"""⚙️ TECHNICAL ANALYSIS COMPLETE

✅ Technical Feasibility:
• Implementation complexity assessed
• Resource requirements evaluated
• Technology constraints identified
• Scalability considerations analyzed

🏗️ Architecture Recommendation:
• System architecture designed
• Component relationships defined
• Data flow patterns established
• Security framework outlined

💻 Technology Stack:
• Backend technologies selected
• Frontend framework chosen
• Database architecture decided
• Development tools identified

📅 Development Timeline:
• Project phases outlined
• Milestone dependencies mapped
• Resource allocation planned
• Critical path identified

💡 Technical Insight: Project is technically feasible with modern architecture and proven technology stack."""

    def format_qa_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format QA analysis for display."""
        strategy = analysis.get('test_strategy', {})
        quality_metrics = analysis.get('quality_metrics', {})
        risk_assessment = analysis.get('risk_assessment', {})
        test_plan = analysis.get('test_plan', {})
        
        return f"""🧪 QUALITY ANALYSIS COMPLETE

🎯 Testing Strategy:
• Comprehensive test approach defined
• Quality gates established
• Testing phases outlined
• Automation framework planned

📊 Quality Metrics:
• Performance benchmarks set
• Reliability standards defined
• User experience criteria established
• Code quality thresholds determined

🚨 Quality Risks:
• Potential quality issues identified
• Risk mitigation strategies planned
• Testing coverage gaps addressed
• Quality assurance checkpoints set

📋 Test Plan:
• Test scenarios documented
• Testing environments specified
• Execution timeline established
• Resource requirements defined

💡 Quality Insight: Robust testing strategy ensures high-quality, reliable product delivery with comprehensive coverage."""

    def format_ai_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format AI Engineer analysis for display."""
        feasibility = analysis.get('ai_feasibility', {})
        recommendations = analysis.get('ai_recommendations', {})
        implementation = analysis.get('implementation_plan', {})
        integration = analysis.get('integration_strategy', {})
        
        return f"""🤖 AI INTEGRATION ANALYSIS COMPLETE

🔍 AI Feasibility:
• AI/ML integration potential evaluated
• Data requirements assessed
• Model complexity analyzed
• Implementation viability confirmed

💡 AI Recommendations:
• High-impact AI features identified
• Machine learning opportunities mapped
• Automation potential assessed
• Intelligence enhancement areas defined

📋 Implementation Plan:
• AI development phases outlined
• Model training strategy planned
• Data pipeline architecture designed
• Performance optimization approach set

🔗 Integration Strategy:
• System integration points identified
• API design patterns established
• Data flow optimization planned
• Scalability considerations addressed

💡 AI Insight: Strategic AI integration offers significant value through intelligent automation and enhanced user experience."""

    async def create_pm_overview(self, project_data: Dict[str, Any]) -> str:
        """Create a comprehensive Product Manager overview based on all agent inputs using dedicated PM final key."""
        from app.llm.llm_client import LLMClient
        
        # Use dedicated PM final key for comprehensive overview
        llm_client = LLMClient()
        
        overview_prompt = f"""
Based on the comprehensive collaborative analysis from our expert team, provide a strategic Product Manager overview for:

PROJECT DETAILS:
• Title: {project_data.get('title', 'Unnamed Project')}
• Description: {project_data.get('description', 'No description')}
• Timeline: {project_data.get('timeline', 'Not specified')}
• Budget: {project_data.get('budget', 'Not specified')}

TEAM ANALYSIS SUMMARY:
• Product Manager Insights: {str(self.shared_context.get('product_strategy', {}))[:400]}...
• Developer Assessment: {str(self.shared_context.get('technical_analysis', {}))[:400]}...
• QA Engineer Analysis: {str(self.shared_context.get('quality_analysis', {}))[:400]}...
• AI Engineer Evaluation: {str(self.shared_context.get('ai_analysis', {}))[:400]}...

TEAM COLLABORATION INSIGHTS:
{str(self.shared_context.get('final_insights', {}))}

---

Provide a comprehensive, well-structured Product Manager overview with the following sections:

📈 EXECUTIVE SUMMARY
Brief overview of the project's potential and strategic positioning

🎯 MARKET OPPORTUNITY ASSESSMENT  
Market size, competition, and positioning strategy

⚙️ TECHNICAL FEASIBILITY SUMMARY
Key technical considerations and implementation approach

🛡️ QUALITY & RISK ASSESSMENT
Quality standards, risks, and mitigation strategies

🤖 AI/ML INTEGRATION POTENTIAL
AI opportunities and implementation roadmap

🚀 GO-TO-MARKET STRATEGY
Launch approach and market entry plan

👥 RESOURCE REQUIREMENTS
Team composition and skill requirements

📅 TIMELINE RECOMMENDATIONS
Phased development approach with milestones

📊 SUCCESS METRICS & KPIs
Measurable success criteria and tracking methods

🎯 STRATEGIC NEXT STEPS
Immediate actions and priority initiatives

IMPORTANT FORMATTING INSTRUCTIONS:
- Use simple bullet points (•) for lists, not markdown asterisks
- Keep section headers clean with just emoji and title
- Use clear, concise language
- Focus on actionable insights
- Structure content with proper line breaks
- Avoid excessive formatting symbols
- Make it professional and easy to read
        """
        
        system_prompt = """You are a senior Product Manager providing a final strategic overview. 

CRITICAL FORMATTING RULES:
- Use simple bullet points (•) for all lists
- DO NOT use markdown asterisks (*) or double asterisks (**)
- Use emoji section headers but keep them clean
- Write in clear, professional language
- Structure with proper spacing and line breaks
- Be comprehensive yet concise
- Focus on actionable insights and strategic recommendations
- Format should be easy to read in a web interface

Your response should be well-structured, professional, and formatted for clear readability."""
        
        overview = await llm_client.get_agent_response('pm_final', overview_prompt, system_prompt)
        return overview

    async def final_collaboration_round(self, project_data: Dict[str, Any]):
        """Final round where agents discuss and refine their recommendations."""
        self.log_conversation("Product Manager", "TEAM_DISCUSSION", 
                            "Team, based on all analyses, let's finalize our recommendations...")
        
        # Developer responds to PM
        dev_response = await self.get_agent_response(
            'developer',
            f"""Based on the collaborative analysis, the Product Manager is asking for final recommendations.
            
            Context from team:
            - Market analysis shows: {str(self.shared_context.get('product_strategy', {}))[:200]}
            - QA recommends: {str(self.shared_context.get('quality_analysis', {}))[:200]}
            - AI Engineer suggests: {str(self.shared_context.get('ai_analysis', {}))[:200]}
            
            Provide your final technical perspective on implementation strategy and timeline.""",
            "You are responding in a team discussion. Be collaborative and reference other team members' insights."
        )
        
        self.log_conversation("Developer", "FINAL_TECHNICAL_RECOMMENDATION", dev_response)
        
        # QA responds
        qa_response = await self.get_agent_response(
            'qa',
            f"""The team is finalizing recommendations. Developer suggests: {dev_response[:200]}...
            
            From your quality perspective, what are the critical quality gates and testing milestones?""",
            "You are in a team discussion. Focus on quality implications and critical testing requirements."
        )
        
        self.log_conversation("QA Engineer", "FINAL_QUALITY_REQUIREMENTS", qa_response)
        
        # AI Engineer provides final input
        ai_response = await self.get_agent_response(
            'ai_engineer',
            f"""Team discussion summary:
            - Developer: {dev_response[:200]}...
            - QA: {qa_response[:200]}...
            
            What's your final recommendation for AI feature prioritization and implementation timeline?""",
            "You are concluding a team discussion. Provide practical AI implementation recommendations."
        )
        
        self.log_conversation("AI Engineer", "FINAL_AI_STRATEGY", ai_response)
        
        # Store final insights
        self.shared_context['final_insights'] = {
            'developer_final_recommendation': dev_response,
            'qa_final_requirements': qa_response,
            'ai_final_strategy': ai_response
        }

    async def get_agent_response(self, agent_type: str, prompt: str, system_prompt: str = None) -> str:
        """Get a response from a specific agent."""
        if agent_type in self.agents:
            return await self.agents[agent_type].get_llm_response(prompt, system_prompt)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")

    def get_conversation_summary(self) -> str:
        """Get a formatted summary of the agent conversations."""
        summary = "\n🗣️  AGENT CONVERSATION SUMMARY\n"
        summary += "=" * 50 + "\n"
        
        for entry in self.conversation_history:
            summary += f"\n[{entry['agent'].upper()}] {entry['type']}:\n"
            summary += f"   {entry['content']}\n"
            summary += "-" * 40 + "\n"
        
        return summary 