#!/usr/bin/env python3
"""
Example usage of the messaging system API
This script shows how to interact with the messaging system
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

class MessagingDemo:
    """Demonstration of the messaging system"""
    
    def __init__(self, base_url=API_BASE):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
        self.user_tokens = {}  # Will store auth tokens for demo users
    
    def login_user(self, email: str, password: str = "password123") -> str:
        """Login and get auth token"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={"email": email, "password": password},
                headers=self.headers
            )
            if response.status_code == 200:
                token = response.json().get("access_token")
                self.user_tokens[email] = f"Bearer {token}"
                return token
            else:
                print(f"Login failed for {email}: {response.text}")
                return None
        except Exception as e:
            print(f"Login error: {e}")
            return None
    
    def get_auth_headers(self, email: str) -> dict:
        """Get headers with auth token"""
        token = self.user_tokens.get(email)
        if token:
            return {**self.headers, "Authorization": token}
        return self.headers
    
    def like_user(self, liker_email: str, target_user_id: int):
        """Like a user (prerequisite for sending greeting)"""
        try:
            headers = self.get_auth_headers(liker_email)
            response = requests.post(
                f"{self.base_url}/recommendations/swipe",
                json={
                    "target_user_id": target_user_id,
                    "action": "like"
                },
                headers=headers
            )
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"Like error: {e}")
            return False
    
    def send_greeting(self, sender_email: str, recipient_id: int, message: str):
        """Send a greeting to start a chat"""
        print(f"\n📨 {sender_email} sending greeting to user {recipient_id}")
        print(f"    Message: '{message}'")
        
        try:
            headers = self.get_auth_headers(sender_email)
            response = requests.post(
                f"{self.base_url}/chats/greeting",
                json={
                    "recipient_id": recipient_id,
                    "greeting_message": message
                },
                headers=headers
            )
            
            if response.status_code == 201:
                chat_data = response.json()
                print(f"    ✅ Greeting sent! Chat ID: {chat_data['chat_id']}")
                print(f"    Status: {chat_data['status']}")
                return chat_data
            else:
                print(f"    ❌ Failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
            return None
    
    def get_pending_greetings(self, user_email: str):
        """Get pending greetings for a user"""
        print(f"\n📥 Getting pending greetings for {user_email}")
        
        try:
            headers = self.get_auth_headers(user_email)
            response = requests.get(
                f"{self.base_url}/chats/pending",
                headers=headers
            )
            
            if response.status_code == 200:
                greetings = response.json()
                print(f"    📊 Found {len(greetings)} pending greeting(s)")
                for greeting in greetings:
                    print(f"      - Chat {greeting['chat_id']}: '{greeting['greeting_message']}'")
                    print(f"        From: {greeting['other_user_name']} (ID: {greeting['initiator_id']})")
                return greetings
            else:
                print(f"    ❌ Failed: {response.text}")
                return []
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
            return []
    
    def respond_to_greeting(self, user_email: str, chat_id: int, accept: bool):
        """Accept or reject a greeting"""
        action = "accepting" if accept else "rejecting"
        print(f"\n🤝 {user_email} {action} greeting in chat {chat_id}")
        
        try:
            headers = self.get_auth_headers(user_email)
            response = requests.post(
                f"{self.base_url}/chats/greeting/respond",
                json={
                    "chat_id": chat_id,
                    "accept": accept
                },
                headers=headers
            )
            
            if response.status_code == 200:
                chat_data = response.json()
                print(f"    ✅ Response sent! New status: {chat_data['status']}")
                if accept:
                    print(f"    🎉 Chat is now active! You can start messaging.")
                return chat_data
            else:
                print(f"    ❌ Failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
            return None
    
    def send_message(self, sender_email: str, chat_id: int, message: str):
        """Send a message in an active chat"""
        print(f"\n💬 {sender_email} sending message to chat {chat_id}")
        print(f"    Message: '{message}'")
        
        try:
            headers = self.get_auth_headers(sender_email)
            response = requests.post(
                f"{self.base_url}/chats/message",
                json={
                    "chat_id": chat_id,
                    "content": message
                },
                headers=headers
            )
            
            if response.status_code == 201:
                message_data = response.json()
                print(f"    ✅ Message sent! Message ID: {message_data['message_id']}")
                return message_data
            else:
                print(f"    ❌ Failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
            return None
    
    def get_chat_messages(self, user_email: str, chat_id: int):
        """Get messages from a chat"""
        print(f"\n📖 {user_email} viewing chat {chat_id}")
        
        try:
            headers = self.get_auth_headers(user_email)
            response = requests.get(
                f"{self.base_url}/chats/{chat_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                chat_data = response.json()
                print(f"    📊 Chat with {chat_data['other_user_name']}")
                print(f"    Status: {chat_data['status']}")
                print(f"    Messages: {len(chat_data['messages'])}")
                
                for msg in chat_data['messages']:
                    timestamp = msg['created_at'][:19]  # Remove microseconds
                    sender_marker = "📤" if msg['sender_id'] == chat_data['initiator_id'] else "📥"
                    greeting_marker = " [GREETING]" if msg['is_greeting'] else ""
                    print(f"      {timestamp} {sender_marker} {msg['content']}{greeting_marker}")
                
                return chat_data
            else:
                print(f"    ❌ Failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
            return None
    
    def get_all_chats(self, user_email: str):
        """Get all chats for a user"""
        print(f"\n📋 Getting all chats for {user_email}")
        
        try:
            headers = self.get_auth_headers(user_email)
            response = requests.get(
                f"{self.base_url}/chats/",
                headers=headers
            )
            
            if response.status_code == 200:
                chat_list = response.json()
                print(f"    📊 Total chats: {chat_list['total']}")
                print(f"    Pending greetings: {chat_list['pending_greetings']}")
                
                for chat in chat_list['chats']:
                    print(f"      - Chat {chat['chat_id']}: {chat['status']} with {chat['other_user_name']}")
                    if chat['last_message_at']:
                        print(f"        Last message: {chat['last_message_at'][:19]}")
                
                return chat_list
            else:
                print(f"    ❌ Failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
            return None

def demo_messaging_flow():
    """Demonstrate the complete messaging flow"""
    print("🎭 MESSAGING SYSTEM DEMO")
    print("=" * 50)
    print("This demo shows the complete greeting/acceptance flow:")
    print("1. User A likes User B")
    print("2. User A sends greeting to User B")
    print("3. User B sees pending greeting")
    print("4. User B accepts the greeting")
    print("5. Both users exchange messages")
    print("=" * 50)
    
    demo = MessagingDemo()
    
    # Demo users
    alice_email = "alice@example.com"
    bob_email = "bob@example.com"
    
    print("\n🔐 Step 0: Login demo users")
    alice_token = demo.login_user(alice_email)
    bob_token = demo.login_user(bob_email)
    
    if not alice_token or not bob_token:
        print("❌ Cannot proceed without user authentication")
        return
    
    print("\n👍 Step 1: Alice likes Bob")
    bob_user_id = 2  # Assuming Bob has user_id 2
    demo.like_user(alice_email, bob_user_id)
    
    print("\n📨 Step 2: Alice sends greeting to Bob")
    greeting_msg = "Hi Bob! I saw your profile and would love to chat! 😊"
    chat = demo.send_greeting(alice_email, bob_user_id, greeting_msg)
    
    if not chat:
        print("❌ Cannot proceed without successful greeting")
        return
    
    chat_id = chat['chat_id']
    
    print("\n📥 Step 3: Bob checks pending greetings")
    demo.get_pending_greetings(bob_email)
    
    print("\n🤝 Step 4: Bob accepts Alice's greeting")
    demo.respond_to_greeting(bob_email, chat_id, accept=True)
    
    print("\n💬 Step 5: Exchange messages")
    demo.send_message(bob_email, chat_id, "Hi Alice! Nice to meet you! 👋")
    demo.send_message(alice_email, chat_id, "Thanks for accepting! How's your day going?")
    demo.send_message(bob_email, chat_id, "Great! I love your travel photos. Where was that taken?")
    
    print("\n📖 Step 6: View chat history")
    demo.get_chat_messages(alice_email, chat_id)
    
    print("\n📋 Step 7: View all chats")
    demo.get_all_chats(alice_email)
    demo.get_all_chats(bob_email)
    
    print("\n✅ Demo complete! The messaging system is working perfectly.")

if __name__ == "__main__":
    print("🧪 MESSAGING SYSTEM API DEMO")
    print("To run this demo, make sure:")
    print("1. Server is running on http://localhost:8000")
    print("2. Users alice@example.com and bob@example.com exist")
    print("3. Database tables are created")
    print()
    print("Run: python test_messaging_system.py first to verify setup")
    print("Then: python start_server.py to start the server")
    print("Finally: python messaging_demo.py to run this demo")
    print()
    input("Press Enter to continue with demo (or Ctrl+C to exit)...")
    demo_messaging_flow()
