from bots.match_bot import extract_desired_tags_from_paragraph
paragraph = "I'm looking for AI projects with investors good at coding."
tags = extract_desired_tags_from_paragraph(paragraph)
print("Tags:", tags)