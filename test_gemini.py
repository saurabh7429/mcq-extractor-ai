from google import genai
import os
from dotenv import load_dotenv
import json

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

sample_text = """
1. What is CPU?
A. Central Processing Unit
B. Computer Personal Unit
C. Central Program Utility
D. Control Processing Unit
Answer: A
"""

prompt = f"""
Extract only valid MCQs from the text below.

Rules:
- Only include proper MCQs.
- Each MCQ must have exactly 4 options.
- Answer must match one of the options.
- Return strictly JSON format.
- Do not include explanations.

Format:
[
  {{
    "id": 1,
    "question": "Question text",
    "options": ["A", "B", "C", "D"],
    "answer": "Correct option text"
  }}
]

Text:
{sample_text}
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

print(response.text)
