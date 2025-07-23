#On one terminal run uvicorn bots.profile_bot:app --host 0.0.0.0 --port 8000
#On another terminal run curl -X POST http://127.0.0.1:8000/profile/summarize -H "Content-Type: application/json" -d "{\"user_id\": 1, \"paragraph\": \"I'm an investor who loves coding and is good at video editing. I also enjoy startups and tech projects.\"}"
#Run: python test_deepseek_match.py. Confirm list of tags
from bots.match_bot import extract_desired_tags_from_paragraph
paragraph = "I'm looking for AI projects with investors good at coding."
tags = extract_desired_tags_from_paragraph(paragraph)
print("Tags:", tags)