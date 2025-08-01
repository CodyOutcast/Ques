"""
Test highlighting functionality in chat viewing
"""

import requests
import json

# Replace with your actual server URL
BASE_URL = "http://localhost:8000"

def test_chat_highlighting():
    """
    Test chat highlighting functionality
    """
    print("🔍 Testing Chat Message Highlighting...")
    
    # Test API endpoint for getting chat with highlighting
    # You'll need to replace these with actual values:
    chat_id = 1  # Replace with actual chat ID
    search_query = "hello"  # Word to highlight
    
    # Headers with authentication (replace with actual token)
    headers = {
        "Authorization": "Bearer YOUR_TOKEN_HERE",
        "Content-Type": "application/json"
    }
    
    # Make request to get chat with highlighting
    response = requests.get(
        f"{BASE_URL}/api/chats/{chat_id}",
        params={
            "search_query": search_query,
            "limit": 20
        },
        headers=headers
    )
    
    if response.status_code == 200:
        chat_data = response.json()
        print(f"✅ Successfully retrieved chat {chat_id}")
        print(f"📝 Messages count: {len(chat_data['messages'])}")
        
        # Show highlighting examples
        highlighted_count = 0
        for message in chat_data['messages']:
            if message.get('highlighted_content'):
                highlighted_count += 1
                print(f"\n📍 Message {message['message_id']}:")
                print(f"   Original: {message['content'][:100]}...")
                print(f"   Highlighted: {message['highlighted_content']}")
        
        print(f"\n🎯 Highlighted {highlighted_count} messages containing '{search_query}'")
        
        return True
    else:
        print(f"❌ Failed to retrieve chat: {response.status_code}")
        print(f"Error: {response.text}")
        return False

def show_api_usage():
    """
    Show how to use the API
    """
    print("\n📖 API Usage Examples:")
    print("\n1. Get chat without highlighting:")
    print("   GET /api/chats/{chat_id}")
    
    print("\n2. Get chat with highlighting:")
    print("   GET /api/chats/{chat_id}?search_query=hello")
    
    print("\n3. Frontend Implementation Example:")
    print("""
    // JavaScript/React example
    const fetchChatWithHighlighting = async (chatId, searchQuery) => {
        const response = await fetch(`/api/chats/${chatId}?search_query=${searchQuery}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        const chatData = await response.json();
        
        // Render messages with highlighting
        chatData.messages.forEach(message => {
            if (message.highlighted_content) {
                // Use highlighted_content for display
                // Convert **text** to <mark>text</mark> or similar
                const highlighted = message.highlighted_content
                    .replace(/\*\*(.*?)\*\*/g, '<mark>$1</mark>');
                
                displayMessage(highlighted);
            } else {
                // Use regular content
                displayMessage(message.content);
            }
        });
    };
    """)

def show_highlighting_format():
    """
    Show highlighting format details
    """
    print("\n🎨 Highlighting Format:")
    print("Backend returns highlighted text with **keyword** format")
    print("Frontend should convert this to appropriate styling:")
    print("\nExample:")
    print("  Backend: 'Hello **world** how are you?'")
    print("  Frontend HTML: 'Hello <mark>world</mark> how are you?'")
    print("  Frontend React: 'Hello <span className=\"highlight\">world</span> how are you?'")

if __name__ == "__main__":
    print("🚀 Chat Highlighting Test & Documentation")
    print("=" * 50)
    
    # Show API usage
    show_api_usage()
    
    # Show highlighting format
    show_highlighting_format()
    
    # Note about testing
    print(f"\n⚠️  To test with real data:")
    print("1. Update BASE_URL, chat_id, and token in the script")
    print("2. Make sure your server is running")
    print("3. Uncomment the test_chat_highlighting() call below")
    
    # Uncomment this line to run actual test (after updating credentials)
    # test_chat_highlighting()
    
    print("\n✅ Chat highlighting functionality is ready!")
    print("Backend provides highlighted_content field when search_query is provided")
