import os
import json
import urllib.request
import urllib.parse
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def get_system_prompt():
    skill_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".agents", "skills", "SKILL.md")
    try:
        with open(skill_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Warning: Could not read SKILL.md: {e}")
        return "You are an AI Resume Consultant."

def search_company_info(company_name: str) -> str:
    """
    Search Wikipedia for background information and culture of a company.
    Use this tool when the user asks about a specific company to tailor the resume better.
    
    Args:
        company_name: The name of the company to search for.
    """
    query = urllib.parse.quote(company_name)
    url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exsentences=3&exlimit=1&titles={query}&explaintext=1&format=json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            pages = data.get("query", {}).get("pages", {})
            for page_id, page_info in pages.items():
                if page_id == "-1":
                    return f"Could not find Wikipedia information for {company_name}."
                return page_info.get("extract", "No summary available.")
    except Exception as e:
        return f"Error fetching company info: {str(e)}"
    return "Unknown error occurred."

def generate_chat_response(messages_history):
    """
    messages_history is a list of dicts: [{'role': 'user'|'assistant'|'system', 'content': '...'}]
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")
    
    client = genai.Client(api_key=api_key)
    
    contents = []
    for msg in messages_history:
        # Gemini roles: user, model
        if msg['role'] == "system":
            # Pass system messages as user context for simplicity
            role = "user"
            content = f"[System Context]: {msg['content']}"
        else:
            role = "user" if msg['role'] == "user" else "model"
            content = msg['content']
            
        contents.append(
            types.Content(role=role, parts=[types.Part.from_text(text=content)])
        )

    system_instruction = get_system_prompt()

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,
            tools=[search_company_info]
        )
    )
    
    return response.text
