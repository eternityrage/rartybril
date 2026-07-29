"""
Generate new Greek topics using AI when topics.txt runs low.
"""
import requests, time, os, sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

def generate_new_topics(count=100):
    api_key = os.getenv("POLLINATIONS_API_KEY")
    if not api_key:
        raise ValueError("POLLINATIONS_API_KEY required")

    url = "https://gen.pollinations.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    system = "You are a historian specializing in ancient women's history. Create unique Greek-language topics about women in ancient civilizations worldwide (Greece, Rome, Egypt, Persia, India, China, Maya, etc.). Each topic short (5-10 words). Output ONLY the topics, one per line."
    prompt = f"Create {count} unique Greek-language topics about women in ancient civilizations:"
    payload = {"model": "openai", "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}], "temperature": 0.8}

    print(f"[topics] Generating {count} new Greek topics...")
    max_retries = 3
    for attempt in range(max_retries):
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=120)
            r.raise_for_status()
            content = r.json()["choices"][0]["message"]["content"].strip()
            topics = [line.strip() for line in content.split("\n") if line.strip() and not line[0].isdigit() and not line.startswith("-")]
            with open("topics.txt", "a", encoding="utf-8") as f:
                for t in topics:
                    f.write(f"{t}\n")
            print(f"[topics] Added {len(topics)} new topics")
            return topics
        except Exception as e:
            print(f"[topics] Attempt {attempt+1} failed: {e}")
            time.sleep((attempt+1)*5)
    return []
