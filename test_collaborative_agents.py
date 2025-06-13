import asyncio
from app.agents.agent_coordinator import AgentCoordinator

async def test_collaborative_agents():
    print("🤖 Testing Collaborative Agent System...")
    print("This will show agents working together and having conversations!")
    print("=" * 80)
    
    # Initialize the agent coordinator
    coordinator = AgentCoordinator()
    
    # Test project data
    test_project = {
        'title': 'AI-Powered E-commerce Recommendation Engine',
        'description': 'An intelligent e-commerce platform that uses machine learning to provide personalized product recommendations, dynamic pricing, and inventory optimization.',
        'requirements': 'Must support real-time recommendations, A/B testing, scalable architecture, and integration with existing e-commerce platforms',
        'constraints': 'Budget: $150,000, Timeline: 6 months, Team: 8 developers',
        'timeline': '6 months',
        'budget': '$150,000'
    }
    
    try:
        print("🚀 Starting Collaborative Analysis...")
        print("You'll see agents discussing, sharing insights, and building on each other's work!\n")
        
        # Run collaborative analysis
        analysis = await coordinator.collaborative_analysis(test_project)
        
        print("\n" + "="*80)
        print("📊 FINAL ANALYSIS SUMMARY")
        print("="*80)
        
        # Show conversation summary
        conversation_summary = coordinator.get_conversation_summary()
        print(conversation_summary)
        
        print("\n✅ Collaborative Agent Test Successful!")
        print("The agents successfully worked together to analyze the project!")
        
    except Exception as e:
        print(f"\n❌ Error during collaborative agent test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_collaborative_agents()) 