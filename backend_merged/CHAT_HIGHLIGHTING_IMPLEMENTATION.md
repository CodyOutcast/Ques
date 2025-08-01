# Chat Message Highlighting Implementation

## Overview
This implementation adds keyword highlighting functionality to chat messages, allowing users to highlight specific words or phrases when viewing chat conversations.

## Backend Implementation (✅ Completed)

### 1. Schema Updates (`schemas/chats.py`)
- Added `highlighted_content: Optional[str]` field to `MessageResponse`
- This field contains the message content with search terms highlighted using `**keyword**` format

### 2. Service Layer (`services/chat_service.py`)
- Modified `get_chat_with_messages()` to accept optional `search_query` parameter
- Enhanced `_highlight_text()` method for text highlighting with context
- Highlights are formatted as `**keyword**` for frontend processing

### 3. API Endpoint (`routers/chats.py`)
- Updated `GET /api/chats/{chat_id}` endpoint to accept `search_query` parameter
- When `search_query` is provided, messages containing the search term will have `highlighted_content` populated

## Frontend Implementation (Required)

### 1. API Usage
```javascript
// Get chat with highlighting
const response = await fetch(`/api/chats/${chatId}?search_query=${searchTerm}`, {
    headers: { 'Authorization': `Bearer ${token}` }
});

const chatData = await response.json();
```

### 2. Rendering Highlighted Messages
```javascript
// Process highlighted content
chatData.messages.forEach(message => {
    if (message.highlighted_content) {
        // Convert **text** to HTML highlighting
        const highlighted = message.highlighted_content
            .replace(/\*\*(.*?)\*\*/g, '<mark>$1</mark>');
        
        displayMessage(highlighted);
    } else {
        displayMessage(message.content);
    }
});
```

### 3. React Component Example
```jsx
const MessageComponent = ({ message, searchQuery }) => {
    const content = message.highlighted_content || message.content;
    
    if (message.highlighted_content) {
        // Convert **text** to React elements
        const parts = content.split(/(\*\*.*?\*\*)/);
        
        return (
            <div>
                {parts.map((part, index) => {
                    if (part.startsWith('**') && part.endsWith('**')) {
                        const text = part.slice(2, -2);
                        return <span key={index} className="highlight">{text}</span>;
                    }
                    return <span key={index}>{part}</span>;
                })}
            </div>
        );
    }
    
    return <div>{content}</div>;
};
```

### 4. CSS Styling
```css
.highlight {
    background-color: yellow;
    padding: 2px 4px;
    border-radius: 3px;
    font-weight: bold;
}

/* Or using mark tag */
mark {
    background-color: #ffeb3b;
    padding: 2px 4px;
    border-radius: 3px;
}
```

## Division of Responsibilities

### Backend (✅ Done)
- ✅ Accept search query parameter
- ✅ Perform text matching (case-insensitive)
- ✅ Generate highlighted content with `**keyword**` format
- ✅ Return both original and highlighted content
- ✅ Handle text excerpting for long messages

### Frontend (To Do)
- 🔲 Implement search input UI
- 🔲 Send search query to backend
- 🔲 Parse `**keyword**` format from backend
- 🔲 Convert to HTML/React highlighting
- 🔲 Style highlighted text appropriately
- 🔲 Handle search state management

## API Endpoints

### Get Chat Messages (Enhanced)
```http
GET /api/chats/{chat_id}?search_query={keyword}&limit=50&offset=0
```

**Response Format:**
```json
{
    "chat_id": 1,
    "messages": [
        {
            "message_id": 123,
            "content": "Hello world! How are you?",
            "highlighted_content": "**Hello** world! How are you?",
            "created_at": "2025-07-30T10:00:00Z",
            ...
        }
    ],
    ...
}
```

## How It Works

1. **User searches**: Frontend sends search query to chat endpoint
2. **Backend processing**: 
   - Retrieves chat messages normally
   - For each message containing the search term:
     - Creates highlighted version with `**keyword**` format
     - Provides context around the match
3. **Frontend rendering**:
   - Checks if `highlighted_content` exists
   - Converts `**keyword**` to appropriate styling
   - Displays highlighted version or falls back to original

## Features

- ✅ Case-insensitive search
- ✅ Context preservation (shows text around matches)
- ✅ Excerpt generation for long messages
- ✅ Multiple keyword highlighting
- ✅ Backward compatibility (works without search query)

## Testing

Use `test_chat_highlighting.py` to test the implementation:
1. Update credentials and chat ID
2. Run the script to see highlighting in action
3. Verify both API response and highlighting format

## Next Steps

1. **Frontend Integration**: Implement the frontend components shown above
2. **Enhanced Search**: Consider adding regex support or phrase matching
3. **Performance**: Add database indexing for message content if needed
4. **UI/UX**: Design intuitive search interface with real-time highlighting

The backend implementation is complete and ready for frontend integration!
