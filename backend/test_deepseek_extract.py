#On one terminal run uvicorn bots.profile_bot:app --host 0.0.0.0 --port 8000
#On another terminal run curl -X POST http://127.0.0.1:8000/profile/summarize -H "Content-Type: application/json" -d "{\"user_id\": 1, \"paragraph\": \"I'm an investor who loves coding and is good at video editing. I also enjoy startups and tech projects.\"}"
'''
Run in VSCode Terminal: python test_deepseek.py.
Confirmation: Should print a list of 3-7 tags. If error (e.g., "Failed to extract tags"), check: API key valid? Network up? Prompt parsing (DeepSeek must output valid JSON). Fix: Lower temperature to 0.5 for stricter output.
'''
import os
from dotenv import load_dotenv
from bots.profile_bot import extract_tags_from_paragraph  # Adjust path if needed

load_dotenv()
paragraph = "I'm an investor who loves coding and is good at video editing. I also enjoy startups and tech projects."
try:
    tags = extract_tags_from_paragraph(paragraph)
    print("Extracted Tags:", tags)
except Exception as e:
    print("Error:", e)