import os
from dotenv import load_dotenv
from google import genai # Note: The SDK often uses 'from google import genai' or 'import google_genai'

# This line reads the .env file and makes the variables available to os.getenv
load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

models = client.models.list()

for m in models:
    print(m.name)