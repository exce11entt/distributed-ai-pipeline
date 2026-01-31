import sys
import os
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.graph import EnterpriseAgent

def main():
    print("--- Initializing Enterprise Agent ---")
    agent = EnterpriseAgent()
    
    user_query = "What is the bank policy on international transfers?"
    print(f"User: {user_query}")
    
    result = agent.run(user_query)
    
    print("\n--- Agent Trace ---")
    for msg in result["messages"]:
        role = "AI" if hasattr(msg, "content") else "System"
        print(f"{role}: {getattr(msg, 'content', 'No content')[:100]}...")
        
    print("\n--- Final Status ---")
    print(f"Complete: {result['is_complete']}")
    print(f"Final Step: {result['current_step']}")

if __name__ == "__main__":
    main()
