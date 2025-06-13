import asyncio
from app.llm.llm_client import LLMClient
from app.agents.product_manager_agent import ProductManagerAgent

async def test_llm_integration():
    print("Testing LLM Integration...")
    
    # Test Product Manager Agent
    print("\nTesting Product Manager Agent...")
    product_manager = ProductManagerAgent()
    
    test_project = {
        'title': 'AI-Powered Task Management System',
        'description': 'A modern task management system that uses AI to help users organize and prioritize their work.',
        'requirements': 'Must support task creation, prioritization, and AI-powered suggestions',
        'constraints': 'Budget: $50,000, Timeline: 3 months',
        'timeline': '3 months',
        'budget': '$50,000'
    }
    
    try:
        print("Analyzing project...")
        analysis = await product_manager.analyze_project(test_project)
        print("\nAnalysis Results:")
        print(product_manager.format_analysis(analysis))
        print("\nLLM Integration Test Successful!")
    except Exception as e:
        print(f"\nError during LLM integration test: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_llm_integration()) 