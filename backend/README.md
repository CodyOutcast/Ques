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
   python seed.py
   ```

## 2. Running the Backend

Start the FastAPI server:
```sh
uvicorn main:app --reload
```
- The API will be available at `http://127.0.0.1:8000/`

## 3. API Endpoints

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
- `models/` — SQLAlchemy ORM models for DB tables.
- `routers/` — FastAPI routers for endpoints.
- `utils/` — Utility functions for DB and VectorDB.
- `dependencies/` — Dependency injection and authentication.
- `migrations/` — Alembic migration scripts.
- `test_*.py` — Scripts to test DB, VectorDB, and AI tag extraction.

## 5. Useful Scripts

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

## 6. Notes

- **Never commit `.env` with secrets to the repository.**
- If you change models, run:
  ```sh
  alembic revision --autogenerate -m "Describe change"
  alembic upgrade head
  ```
- For any issues, check logs or ask in the team chat.

---