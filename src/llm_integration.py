import requests

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def query_llm(prompt, api_key=None, model="text-davinci-003"):
    api_key = api_key or os.getenv("OPENAI_API_KEY")

    if not api_key or api_key == "your_openai_api_key_here":
        return {
            "error": "API key not provided. Returning deep prompt.",
            "prompt": prompt,
        }

    url = os.getenv("OPENAI_API_URL")
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    data = {"model": model, "prompt": prompt, "max_tokens": 150}
    response = requests.post(url, headers=headers, json=data)
    return response.json()
