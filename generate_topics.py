"""
Generate new Greek topics using AI when topics.txt runs low.

This script:
1. Checks if topics.txt has enough topics (< 50 remaining)
2. Generates 100 new unique Greek topics using Pollinations API
3. Appends them to topics.txt
"""

import requests
from urllib.parse import quote
from pathlib import Path
import time
import re
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def generate_new_topics(count=100):
    """Generate new Greek topics using FREE HuggingFace API."""
    
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        raise ValueError("HF_TOKEN environment variable required")
    
    system = "Είσαι ιστορικός που ειδικεύεται στην ιστορία των γυναικών στους αρχαίους πολιτισμούς."
    prompt = f"Δημιούργησε {count} μοναδικά θέματα στα ελληνικά για γυναίκες σε αρχαίους πολιτισμούς. Κάθε θέμα σύντομο (5-10 λέξεις). Παράγει ΜΟΝΟ τα θέματα, ένα ανά γραμμή."
    
    url = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {"inputs": f"{system}\n\n{prompt}", "parameters": {"max_new_tokens": 500, "temperature": 0.8}}
    
    print(f"[topics] Generating {count} new Greek topics...")
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=180)
            r.raise_for_status()
            
            # Parse topics
            response_json = r.json()
            text = response_json['choices'][0]['message']['content'].strip()
            
            topics = []
            for line in text.split('\n'):
                # Remove numbering and clean
                cleaned = line.strip()
                # Remove common prefixes
                for prefix in ['- ', '* ', '• ', '→ ', '✓ ']:
                    if cleaned.startswith(prefix):
                        cleaned = cleaned[len(prefix):]
                # Remove numbering like "1. " or "1) "
                cleaned = re.sub(r'^\d+[\.:\)]\s*', '', cleaned)
                
                if cleaned and len(cleaned) > 5:
                    topics.append(cleaned)
            
            if len(topics) >= count // 2:  # Accept if we got at least half
                print(f"[topics] Successfully generated {len(topics)} topics!")
                return topics[:count]
            else:
                print(f"[topics] Only got {len(topics)} topics, retrying...")
                raise ValueError(f"Insufficient topics generated: {len(topics)}")
                
        except Exception as e:
            wait_time = (attempt + 1) * 5
            if attempt < max_retries - 1:
                print(f"[topics] Error: {e}")
                print(f"[topics] Retry {attempt + 1}/{max_retries} (waiting {wait_time}s)...")
                time.sleep(wait_time)
            else:
                print(f"[topics] Failed after {max_retries} attempts: {e}")
                raise
    
    return []

def check_and_update_topics():
    """Check topics.txt and add more if needed."""

    topics_file = Path('topics.txt')

    # Read existing topics
    if topics_file.exists():
        with open(topics_file, 'r', encoding='utf-8') as f:
            existing_topics = [line.strip() for line in f if line.strip()]
    else:
        existing_topics = []

    print(f"[topics] Current topics: {len(existing_topics)}")

    # Check if we need more topics
    if len(existing_topics) < 50:
        print(f"[topics] Low on topics! Generating 100 more...")
        
        new_topics = generate_new_topics(100)
        
        # Append to file
        with open(topics_file, 'a', encoding='utf-8') as f:
            for topic in new_topics:
                f.write(f"{topic}\n")
        
        print(f"[topics] Added {len(new_topics)} new topics!")
        print(f"[topics] Total topics now: {len(existing_topics) + len(new_topics)}")
    else:
        print(f"[topics] Enough topics available ({len(existing_topics)})")

if __name__ == '__main__':
    check_and_update_topics()
