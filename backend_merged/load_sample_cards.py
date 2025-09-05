"""
Load Sample Agent Cards
Script to load sample agent cards from agent_card.json into the database
"""

import json
import sys
from sqlalchemy.orm import Session
from dependencies.db import get_db
from services.agent_cards_service import AgentCardsService

def load_sample_cards():
    """Load sample agent cards from JSON file"""
    try:
        # Read the JSON file
        with open("agent_card.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        cards_data = data.get("results", [])
        
        if not cards_data:
            print("❌ No card data found in agent_card.json")
            return False
        
        print(f"📂 Found {len(cards_data)} cards in agent_card.json")
        
        # Get database session
        db = next(get_db())
        
        # Create service instance
        service = AgentCardsService(db)
        
        # Create cards
        created_ids = service.create_agent_cards_from_json(
            cards_data=cards_data,
            generation_prompt="Sample cards from agent_card.json",
            ai_agent_id="sample_loader_001"
        )
        
        if created_ids:
            print(f"✅ Successfully created {len(created_ids)} agent cards")
            print(f"   Card IDs: {created_ids}")
            return True
        else:
            print("❌ Failed to create agent cards")
            return False
            
    except FileNotFoundError:
        print("❌ agent_card.json file not found")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON format: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error loading sample cards: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Loading Sample Agent Cards")
    print("=" * 40)
    
    success = load_sample_cards()
    
    if success:
        print("\n🎉 Sample cards loaded successfully!")
        print("You can now test the agent cards system with these sample cards.")
    else:
        print("\n💥 Failed to load sample cards.")
        sys.exit(1)
