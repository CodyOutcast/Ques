# Backend Developer Instructions

## 1. Setup

1. **Clone the repository**  
   ```sh
   git clone <repo-url>
   cd backend
   ```

2. **Install dependencies**  
   ```sh
   pip install -r requirements.txt
   ```

3. **Configure environment variables**  
   - Copy `.env.example` to `.env` (if provided) or create `.env` with the following keys:
     - `DATABASE_URL` or `PG_USER`, `PG_PASSWORD`, `PG_HOST`, `PG_PORT`, `PG_DATABASE`
     - `DEEPSEEK_API_KEY`
     - `VECTORDB_ENDPOINT`, `VECTORDB_USERNAME`, `VECTORDB_KEY`, `VECTORDB_COLLECTION`, `VECTORDB_DIMENSION`
     - `SECRET_KEY` (for JWT)

4. **Run database migrations**  
   ```sh
   alembic upgrade head
   ```

5. **(Optional) Seed the database with test data**  
   ```sh
   python seed_database_simple.py
   ```
   - Creates 5 realistic test users with profiles, matches, swipes, and messages
   - Populates all database tables with sample dating app data

## 2. Running the Backend

Start the FastAPI server:
```sh
uvicorn main:app --reload
```
- The API will be available at `http://127.0.0.1:8000/`

## 3. API Endpoints

### Core Dating App Features

- **User Registration:**  
  `POST /users/register`  
  - Input: `{ "name": str, "bio": str, "verification_status": str }`
  - Output: `{ "user_id": int, "message": str }`

- **User Profile Management:**  
  `GET /users/profile/{user_id}` - Get user profile  
  `PUT /users/profile/{user_id}` - Update user profile  
  `DELETE /users/profile/{user_id}` - Delete user profile  

- **User Listing:**  
  `GET /users/list` - Get all users with pagination

- **Chat System:**  
  `GET /chat/matches/{user_id}` - Get user's matches  
  `POST /chat/send` - Send message to match  
  `GET /chat/messages/{match_id}` - Get chat history  
  `GET /chat/unread-count/{user_id}` - Get unread message count

### AI-Powered Features

- **Profile Summarization:**  
  `POST /profile/summarize`  
  - Input: `{ "user_id": int, "paragraph": str }`
  - Output: `{ "tags": [...] }`

- **Project Matching:**  
  `POST /match/summarize`  
  - Input: `{ "query_paragraph": str }`
  - Output: `{ "matches": [...] }`

## 4. Folder Structure

- `main.py` — FastAPI entry point, loads routers.
- `bots/` — AI logic for profile and match endpoints.
- `models/` — SQLAlchemy ORM models for DB tables:
  - `users.py` — User, UserFeature, UserLink, UserSwipe models
  - `matches.py` — Match model for user connections
  - `messages.py` — Message model for chat functionality
- `routers/` — FastAPI routers for endpoints:
  - `users.py` — User registration and profile management (Page 3)
  - `chat.py` — Chat and messaging functionality (Page 4)
  - `profile.py` — AI profile summarization
  - `match.py` — AI project matching
- `utils/` — Utility functions for DB and VectorDB.
- `dependencies/` — Dependency injection and authentication.
- `migrations/` — Alembic migration scripts.
- `test_*.py` — Scripts to test DB, VectorDB, and AI tag extraction.
- `seed_database_simple.py` — Database seeding script with realistic test data.

## 5. Useful Scripts

- **Test Database Schema:**  
  ```sh
  python check_db.py
  ```
- **Test API Endpoints:**  
  ```sh
  python test_pages_3_4.py
  ```
- **Test DB and VectorDB:**  
  ```sh
  python test_dbs.py
  ```
- **Test DeepSeek Tag Extraction:**  
  ```sh
  python test_deepseek_extract.py
  ```
- **Test DeepSeek Match Extraction:**  
  ```sh
  python test_deepseek_match.py
  ```
- **Run Simple Test Server:**  
  ```sh
  python test_server.py
  ```

## 6. Database Schema

The dating app uses 6 main tables:
- **`users`** — User profiles with name, bio, verification status
- **`user_features`** — User skill tags and features
- **`user_links`** — User portfolio/social links
- **`user_swipes`** — Swipe interactions (like/dislike)
- **`matches`** — Mutual matches between users
- **`messages`** — Chat messages between matched users

## 7. Notes

- **Never commit `.env` with secrets to the repository.**
- **Database is pre-populated** with 5 test users (IDs 7-11) and realistic data
- If you change models, run:
  ```sh
  alembic revision --autogenerate -m "Describe change"
  alembic upgrade head
  ```
- For any issues, check logs or ask in the team chat.

## 8. Testing the Application

1. **Start the server:**
   ```sh
   uvicorn main:app --reload
   ```

2. **Visit API documentation:**
   - Swagger UI: `http://127.0.0.1:8000/docs`
   - ReDoc: `http://127.0.0.1:8000/redoc`

3. **Test with existing data:**
   - Use user IDs 7-11 for testing API endpoints
   - Check matches and messages between these users

---