#!/usr/bin/env python3
"""
Simplified Database Seeding Script
Inserts test data matching the actual database schema
"""

import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv("backend/.env")

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL') or f"postgresql://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DATABASE')}"

print(f"🔗 Connecting to database...")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def clear_existing_data(db):
    """Clear existing test data"""
    print("🧹 Clearing existing data...")
    
    # Delete in order to respect foreign key constraints
    db.execute(text("DELETE FROM messages"))
    db.execute(text("DELETE FROM matches"))
    db.execute(text("DELETE FROM user_swipes"))
    db.execute(text("DELETE FROM user_features"))
    db.execute(text("DELETE FROM user_links"))
    db.execute(text("DELETE FROM users"))
    
    db.commit()
    print("✅ Existing data cleared")

def create_test_users(db):
    """Create 5 realistic test users"""
    print("👥 Creating test users...")
    
    users_data = [
        {
            "name": "Alice Chen",
            "bio": "UI/UX Designer passionate about fintech startups. 5+ years experience designing mobile apps. Looking for co-founders to build the next big thing in financial technology.",
            "verification_status": "verified",
            "feature_tags": ["UI/UX Design", "Mobile Apps", "Fintech", "Product Design", "Figma Expert"],
            "portfolio_links": ["https://behance.net/alicechen", "https://alicechen.design", "https://linkedin.com/in/alice-chen-design"]
        },
        {
            "name": "Bob Martinez",
            "bio": "Full-stack developer and blockchain enthusiast. Built 3 successful crypto projects. Expert in React, Node.js, and Solidity. Seeking investment opportunities and technical partnerships.",
            "verification_status": "verified",
            "feature_tags": ["Blockchain", "Full-stack Development", "React", "Node.js", "Cryptocurrency", "Smart Contracts"],
            "portfolio_links": ["https://github.com/bobmartinez", "https://bobmartinez.dev", "https://linkedin.com/in/bob-martinez-dev"]
        },
        {
            "name": "Carol Johnson",
            "bio": "Growth marketing specialist with 8 years experience scaling tech startups from 0 to $10M ARR. Expert in digital marketing, user acquisition, and product-market fit. Ready to be your CMO.",
            "verification_status": "pending",
            "feature_tags": ["Growth Marketing", "Digital Marketing", "User Acquisition", "Analytics", "B2B Marketing", "Startup Scaling"],
            "portfolio_links": ["https://linkedin.com/in/carol-johnson-growth", "https://caroljohnson.marketing"]
        },
        {
            "name": "David Kim",
            "bio": "Serial entrepreneur and angel investor. Founded 2 exits (acquired for $50M total). Now investing in early-stage AI and SaaS startups. Looking for exceptional founders to back.",
            "verification_status": "verified",
            "feature_tags": ["Angel Investor", "Serial Entrepreneur", "AI Startups", "SaaS", "Venture Capital", "Business Strategy"],
            "portfolio_links": ["https://davidkim.vc", "https://crunchbase.com/person/david-kim", "https://linkedin.com/in/david-kim-investor"]
        },
        {
            "name": "Emma Rodriguez",
            "bio": "Data scientist and AI researcher with PhD from Stanford. 6 years at Google AI. Building next-gen machine learning solutions. Seeking co-founder opportunities in AI/ML space.",
            "verification_status": "verified",
            "feature_tags": ["Data Science", "Machine Learning", "AI Research", "Python", "TensorFlow", "Computer Vision"],
            "portfolio_links": ["https://github.com/emmarodriguez", "https://scholar.google.com/emmarodriguez", "https://emmarodriguez.ai"]
        }
    ]
    
    created_user_ids = []
    
    for i, user_data in enumerate(users_data, 1):
        # Insert user
        result = db.execute(text("""
            INSERT INTO users (name, bio, verification_status, is_active)
            VALUES (:name, :bio, :verification_status, :is_active)
            RETURNING user_id
        """), {
            "name": user_data["name"],
            "bio": user_data["bio"],
            "verification_status": user_data["verification_status"],
            "is_active": True
        })
        
        user_id = result.fetchone()[0]
        created_user_ids.append(user_id)
        
        # Add feature tags
        for tag in user_data["feature_tags"]:
            db.execute(text("""
                INSERT INTO user_features (user_id, tags)
                VALUES (:user_id, :tags)
            """), {
                "user_id": user_id,
                "tags": tag
            })
        
        # Add portfolio links
        for link in user_data["portfolio_links"]:
            db.execute(text("""
                INSERT INTO user_links (user_id, links)
                VALUES (:user_id, :links)
            """), {
                "user_id": user_id,
                "links": link
            })
        
        print(f"   ✅ Created user {i}: {user_data['name']} (ID: {user_id})")
    
    db.commit()
    print(f"✅ Successfully created {len(created_user_ids)} users")
    return created_user_ids

def create_user_swipes(db, user_ids):
    """Create realistic swipe interactions between users"""
    print("👆 Creating user swipes...")
    
    swipes_data = [
        # Alice (1) swipes
        {"swiper_id": user_ids[0], "target_id": user_ids[1], "direction": "like"},   # Alice likes Bob
        {"swiper_id": user_ids[0], "target_id": user_ids[3], "direction": "like"},   # Alice likes David
        {"swiper_id": user_ids[0], "target_id": user_ids[4], "direction": "dislike"}, # Alice dislikes Emma
        
        # Bob (2) swipes
        {"swiper_id": user_ids[1], "target_id": user_ids[0], "direction": "like"},   # Bob likes Alice (MATCH!)
        {"swiper_id": user_ids[1], "target_id": user_ids[2], "direction": "like"},   # Bob likes Carol
        {"swiper_id": user_ids[1], "target_id": user_ids[4], "direction": "like"},   # Bob likes Emma
        
        # Carol (3) swipes
        {"swiper_id": user_ids[2], "target_id": user_ids[1], "direction": "like"},   # Carol likes Bob (MATCH!)
        {"swiper_id": user_ids[2], "target_id": user_ids[3], "direction": "like"},   # Carol likes David
        {"swiper_id": user_ids[2], "target_id": user_ids[0], "direction": "dislike"}, # Carol dislikes Alice
        
        # David (4) swipes
        {"swiper_id": user_ids[3], "target_id": user_ids[0], "direction": "like"},   # David likes Alice (MATCH!)
        {"swiper_id": user_ids[3], "target_id": user_ids[2], "direction": "like"},   # David likes Carol (MATCH!)
        {"swiper_id": user_ids[3], "target_id": user_ids[4], "direction": "like"},   # David likes Emma
        
        # Emma (5) swipes
        {"swiper_id": user_ids[4], "target_id": user_ids[1], "direction": "like"},   # Emma likes Bob (MATCH!)
        {"swiper_id": user_ids[4], "target_id": user_ids[3], "direction": "like"},   # Emma likes David (MATCH!)
        {"swiper_id": user_ids[4], "target_id": user_ids[0], "direction": "dislike"}, # Emma dislikes Alice
    ]
    
    for swipe_data in swipes_data:
        db.execute(text("""
            INSERT INTO user_swipes (swiper_id, target_id, direction, timestamp)
            VALUES (:swiper_id, :target_id, :direction, :timestamp)
        """), {
            "swiper_id": swipe_data["swiper_id"],
            "target_id": swipe_data["target_id"],
            "direction": swipe_data["direction"],
            "timestamp": datetime.utcnow() - timedelta(hours=24)
        })
    
    db.commit()
    print(f"✅ Created {len(swipes_data)} user swipes")

def create_matches(db, user_ids):
    """Create matches based on mutual likes"""
    print("💕 Creating matches...")
    
    # Based on the swipes above, these are the mutual matches:
    matches_data = [
        {"user1_id": user_ids[0], "user2_id": user_ids[1]},  # Alice ↔ Bob
        {"user1_id": user_ids[1], "user2_id": user_ids[2]},  # Bob ↔ Carol
        {"user1_id": user_ids[0], "user2_id": user_ids[3]},  # Alice ↔ David
        {"user1_id": user_ids[2], "user2_id": user_ids[3]},  # Carol ↔ David
        {"user1_id": user_ids[1], "user2_id": user_ids[4]},  # Bob ↔ Emma
        {"user1_id": user_ids[3], "user2_id": user_ids[4]},  # David ↔ Emma
    ]
    
    created_match_ids = []
    
    for match_data in matches_data:
        result = db.execute(text("""
            INSERT INTO matches (user1_id, user2_id, timestamp, is_active)
            VALUES (:user1_id, :user2_id, :timestamp, :is_active)
            RETURNING match_id
        """), {
            "user1_id": match_data["user1_id"],
            "user2_id": match_data["user2_id"],
            "timestamp": datetime.utcnow() - timedelta(hours=20),
            "is_active": True
        })
        
        match_id = result.fetchone()[0]
        created_match_ids.append(match_id)
    
    db.commit()
    print(f"✅ Created {len(created_match_ids)} matches")
    return created_match_ids

def create_sample_messages(db, match_ids, user_ids):
    """Create sample chat messages between matched users"""
    print("💬 Creating sample messages...")
    
    messages_data = [
        # Alice ↔ Bob conversation (match_id 0)
        {
            "match_id": match_ids[0],
            "sender_id": user_ids[0],  # Alice
            "message_text": "Hi Bob! I saw your blockchain projects on GitHub. Really impressive work on the DeFi protocol!",
            "sent_at": datetime.utcnow() - timedelta(hours=18),
            "is_read": True
        },
        {
            "match_id": match_ids[0],
            "sender_id": user_ids[1],  # Bob
            "message_text": "Thanks Alice! I love your UI/UX work. Your fintech designs are exactly what the crypto space needs.",
            "sent_at": datetime.utcnow() - timedelta(hours=17, minutes=30),
            "is_read": True
        },
        {
            "match_id": match_ids[0],
            "sender_id": user_ids[0],  # Alice
            "message_text": "I've been thinking about building a user-friendly DeFi app. Would you be interested in collaborating?",
            "sent_at": datetime.utcnow() - timedelta(hours=16),
            "is_read": False
        },
        
        # Bob ↔ Carol conversation (match_id 1)
        {
            "match_id": match_ids[1],
            "sender_id": user_ids[2],  # Carol
            "message_text": "Hey Bob! Your blockchain projects caught my attention. I specialize in growth marketing for tech startups.",
            "sent_at": datetime.utcnow() - timedelta(hours=12),
            "is_read": True
        },
        {
            "match_id": match_ids[1],
            "sender_id": user_ids[1],  # Bob
            "message_text": "Perfect timing Carol! I'm looking for someone to help scale my next crypto project. Your track record is impressive.",
            "sent_at": datetime.utcnow() - timedelta(hours=11, minutes=15),
            "is_read": False
        },
        
        # Alice ↔ David conversation (match_id 2)
        {
            "match_id": match_ids[2],
            "sender_id": user_ids[3],  # David
            "message_text": "Alice, your fintech design portfolio is outstanding. I'm always looking to invest in design-driven startups.",
            "sent_at": datetime.utcnow() - timedelta(hours=8),
            "is_read": True
        },
        {
            "match_id": match_ids[2],
            "sender_id": user_ids[0],  # Alice
            "message_text": "Thank you David! I'm actually working on a new fintech concept. Would love to discuss potential investment opportunities.",
            "sent_at": datetime.utcnow() - timedelta(hours=6),
            "is_read": False
        },
        
        # David ↔ Emma conversation (match_id 5)
        {
            "match_id": match_ids[5],
            "sender_id": user_ids[4],  # Emma
            "message_text": "Hi David! I'm developing some cutting-edge AI solutions and looking for the right investor partner.",
            "sent_at": datetime.utcnow() - timedelta(hours=4),
            "is_read": True
        },
        {
            "match_id": match_ids[5],
            "sender_id": user_ids[3],  # David
            "message_text": "Emma, your AI research background is exactly what I look for. Let's schedule a call to discuss your vision.",
            "sent_at": datetime.utcnow() - timedelta(hours=2),
            "is_read": False
        },
    ]
    
    for msg_data in messages_data:
        db.execute(text("""
            INSERT INTO messages (match_id, sender_id, text, timestamp, is_read)
            VALUES (:match_id, :sender_id, :text, :timestamp, :is_read)
        """), {
            "match_id": msg_data["match_id"],
            "sender_id": msg_data["sender_id"],
            "text": msg_data["message_text"],
            "timestamp": msg_data["sent_at"],
            "is_read": msg_data["is_read"]
        })
    
    db.commit()
    print(f"✅ Created {len(messages_data)} sample messages")

def print_summary(db):
    """Print a summary of created data"""
    print("\n📊 DATABASE SEEDING SUMMARY")
    print("=" * 50)
    
    # Users summary
    users_result = db.execute(text("""
        SELECT u.user_id, u.name, u.verification_status,
               STRING_AGG(uf.tags, ', ') as features
        FROM users u
        LEFT JOIN user_features uf ON u.user_id = uf.user_id
        GROUP BY u.user_id, u.name, u.verification_status
        ORDER BY u.user_id
    """))
    
    print("\n👥 USERS CREATED:")
    for row in users_result:
        features = row[3][:50] + "..." if row[3] and len(row[3]) > 50 else row[3]
        print(f"   {row[0]}. {row[1]}")
        print(f"      Status: {row[2]}")
        print(f"      Tags: {features}")
    
    # Matches summary
    matches_result = db.execute(text("""
        SELECT m.match_id, u1.name as user1_name, u2.name as user2_name
        FROM matches m
        JOIN users u1 ON m.user1_id = u1.user_id
        JOIN users u2 ON m.user2_id = u2.user_id
        ORDER BY m.match_id
    """))
    
    print(f"\n💕 MATCHES CREATED:")
    for row in matches_result:
        print(f"   {row[0]}. {row[1]} ↔ {row[2]}")
    
    # Messages summary
    message_count = db.execute(text("SELECT COUNT(*) FROM messages")).fetchone()[0]
    unread_count = db.execute(text("SELECT COUNT(*) FROM messages WHERE is_read = false")).fetchone()[0]
    print(f"\n💬 MESSAGES: {message_count} total ({unread_count} unread)")
    
    # Swipes summary
    swipe_count = db.execute(text("SELECT COUNT(*) FROM user_swipes")).fetchone()[0]
    likes_count = db.execute(text("SELECT COUNT(*) FROM user_swipes WHERE direction = 'like'")).fetchone()[0]
    print(f"\n👆 SWIPES: {swipe_count} total ({likes_count} likes, {swipe_count - likes_count} dislikes)")

def main():
    print("🚀 Project Tinder Database Seeding")
    print("=" * 40)
    
    try:
        # Create database session
        db = SessionLocal()
        
        # Ask user if they want to clear existing data
        clear_data = input("\n🤔 Clear existing data? (y/N): ").lower().strip()
        if clear_data == 'y':
            clear_existing_data(db)
        
        # Create test data
        user_ids = create_test_users(db)
        create_user_swipes(db, user_ids)
        match_ids = create_matches(db, user_ids)
        create_sample_messages(db, match_ids, user_ids)
        
        # Print summary
        print_summary(db)
        
        print("\n🎉 Database seeding completed successfully!")
        print("\n📖 Next steps:")
        print("1. Connect your backend to this database")
        print("2. Test the API endpoints with this data")
        print("3. Use these user IDs in your frontend/mobile app")
        
        print(f"\n🆔 Created User IDs: {user_ids}")
        print(f"🔗 Created Match IDs: {match_ids}")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
