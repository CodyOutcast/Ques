"""
Simple Interactive Test for Project Idea Generation Agent
Enter queries manually and evaluate output quality
"""

import os
import json
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Mock database functions for standalone testing
def mock_check_quota(user_id: int) -> bool:
    """Mock quota check - always returns True for testing"""
    return True

def mock_deduct_quota(user_id: int, cost: int = 1):
    """Mock quota deduction - does nothing for testing"""
    pass

# Replace the database imports with mocks
sys.modules['db_utils'] = type(sys)('mock_db_utils')
sys.modules['db_utils'].check_quota = mock_check_quota
sys.modules['db_utils'].deduct_quota = mock_deduct_quota

# Import the agent after mocking
from services.project_idea_agent import generate_project_ideas

def format_output(result):
    """Format the output in a readable way for manual evaluation"""
    print("\n" + "="*80)
    print("🎯 PROJECT IDEA GENERATION RESULTS")
    print("="*80)
    
    print(f"📝 Original Query: {result['original_query']}")
    print(f"🔍 Search ID: {result['search_id']}")
    print(f"⏱️  Processing Time: {result['processing_time_seconds']} seconds")
    print(f"📚 Sources Found: {result['total_sources_found']}")
    print(f"💡 Ideas Extracted: {result['total_ideas_extracted']}")
    print(f"📅 Created: {result['created_at']}")
    
    print(f"\n🔍 Generated Search Prompts ({len(result['generated_prompts'])}):")
    for i, prompt in enumerate(result['generated_prompts'], 1):
        print(f"   {i}. [{prompt['engine']}] {prompt['prompt']} ({prompt['results_count']} results)")
    
    print(f"\n🎯 PROJECT IDEAS ({len(result['project_ideas'])}):")
    print("-" * 80)
    
    for i, idea in enumerate(result['project_ideas'], 1):
        print(f"\n💡 IDEA {i}: {idea['project_idea_title']}")
        print(f"   🎯 Scope: {idea['project_scope']}")
        print(f"   📊 Difficulty: {idea['difficulty_level']}")
        print(f"   ⏰ Timeline: {idea['estimated_timeline']}")
        print(f"   📈 Relevance Score: {idea['relevance_score']}")
        
        print(f"   📝 Description:")
        print(f"      {idea['description']}")
        
        print(f"   ⭐ Key Features:")
        for feature in idea['key_features']:
            print(f"      • {feature}")
        
        print(f"   🛠️  Required Skills:")
        print(f"      {', '.join(idea['required_skills'])}")
        
        if idea['similar_examples']:
            print(f"   🔗 Similar Examples:")
            for example in idea['similar_examples']:
                print(f"      • {example}")
        
        print("-" * 40)

def check_environment():
    """Check if environment is properly configured"""
    print("🔧 Checking Environment...")
    
    required_keys = {
        'SEARCHAPI_KEY': os.environ.get('SEARCHAPI_KEY'),
        'DEEPSEEK_API_KEY_AGENT': os.environ.get('DEEPSEEK_API_KEY_AGENT')
    }
    
    missing_keys = []
    for key, value in required_keys.items():
        if not value:
            missing_keys.append(key)
            print(f"❌ {key}: Not set")
        else:
            print(f"✅ {key}: Configured")
    
    if missing_keys:
        print(f"\n⚠️  Missing API keys: {', '.join(missing_keys)}")
        print("Please add them to your .env file:")
        for key in missing_keys:
            print(f"   {key}=your_key_here")
        return False
    
    print("✅ Environment ready!")
    return True

def interactive_test():
    """Run interactive testing session"""
    print("🎯 Project Idea Generator - Interactive Test")
    print("=" * 50)
    print("Enter your queries to generate project ideas.")
    print("Type 'quit' or 'exit' to stop.\n")
    
    if not check_environment():
        print("\n❌ Environment not ready. Please configure your API keys.")
        return
    
    while True:
        try:
            # Get user input
            query = input("\n📝 Enter your project query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not query:
                print("⚠️  Please enter a query.")
                continue
            
            print(f"\n🔄 Generating ideas for: '{query}'")
            print("⏳ This may take 30-60 seconds...")
            
            # Generate ideas
            result = generate_project_ideas(query, user_id=1)
            
            # Display formatted results
            format_output(result)
            
            # Ask for evaluation
            print("\n" + "="*80)
            print("📊 MANUAL EVALUATION")
            print("="*80)
            print("Please evaluate the quality of these results:")
            print("1. Are the ideas relevant to your query?")
            print("2. Are they creative and unique?")
            print("3. Are the details (timeline, skills, etc.) realistic?")
            print("4. Would you consider implementing any of these ideas?")
            print("5. How would you rate the overall quality (1-10)?")
            
            # Optional: Save results
            save = input("\n💾 Save these results to file? (y/n): ").strip().lower()
            if save in ['y', 'yes']:
                filename = f"test_results_{result['search_id']}.json"
                with open(filename, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"✅ Results saved to {filename}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error generating ideas: {str(e)}")
            print("Please check your API keys and internet connection.")

def quick_test():
    """Run a quick test with predefined queries"""
    print("🚀 Quick Test - Predefined Queries")
    print("=" * 40)
    
    if not check_environment():
        return
    
    test_queries = [
        "Build a Python web scraper for job listings",
        "Create a mobile app for habit tracking",
        "Write a technical blog about AI trends"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Test {i}/{len(test_queries)} ---")
        print(f"Query: {query}")
        
        try:
            result = generate_project_ideas(query, user_id=1)
            
            # Brief summary
            print(f"✅ Generated {len(result['project_ideas'])} ideas")
            print(f"⏱️  Processing time: {result['processing_time_seconds']}s")
            print(f"📚 Sources: {result['total_sources_found']}")
            
            # Show just the titles
            print("💡 Ideas generated:")
            for j, idea in enumerate(result['project_ideas'], 1):
                print(f"   {j}. {idea['project_idea_title']}")
                print(f"      Relevance: {idea['relevance_score']}")
            
        except Exception as e:
            print(f"❌ Failed: {str(e)}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple Project Idea Generator Test")
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="Run interactive mode (default)")
    parser.add_argument("--quick", "-q", action="store_true", 
                       help="Run quick test with predefined queries")
    
    args = parser.parse_args()
    
    if args.quick:
        quick_test()
    else:
        interactive_test()
