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