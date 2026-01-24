"""
Utility script to fetch available models from OpenRouter API.
This can help identify correct model names.
"""
import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()


def fetch_openrouter_models():
    """Fetch list of available models from OpenRouter."""
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("OPENROUTER_API_KEY not found in .env file")
        return
    
    url = "https://openrouter.ai/api/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/niki-sudo/ChatList",
        "X-Title": "ChatList"
    }
    
    try:
        with httpx.Client() as client:
            response = client.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            print("Available OpenRouter Models:")
            print("=" * 80)
            
            models = data.get('data', [])
            for model in models:
                model_id = model.get('id', 'N/A')
                name = model.get('name', 'N/A')
                pricing = model.get('pricing', {})
                context_length = model.get('context_length', 'N/A')
                
                print(f"\nID: {model_id}")
                print(f"Name: {name}")
                print(f"Context: {context_length}")
                if pricing:
                    prompt_price = pricing.get('prompt', 'N/A')
                    completion_price = pricing.get('completion', 'N/A')
                    print(f"Pricing: Prompt={prompt_price}, Completion={completion_price}")
                print("-" * 80)
            
            # Save to file for reference
            with open('openrouter_models.json', 'w') as f:
                json.dump(data, f, indent=2)
            print(f"\n\nFull model list saved to openrouter_models.json")
            
    except Exception as e:
        print(f"Error fetching models: {e}")


if __name__ == '__main__':
    fetch_openrouter_models()

