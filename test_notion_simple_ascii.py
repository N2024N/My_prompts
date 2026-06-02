import os
from notion_client import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Notion API key
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
if not NOTION_API_KEY:
    print("ERROR: NOTION_API_KEY not found in .env file")
    exit(1)

print(f"NOTION_API_KEY found: {NOTION_API_KEY[:10]}...")

# Test database IDs
DATABASE_IDS = [
    "36d3431ec8e68076a1e7000c59505208",  # prompts
    "36e3431ec8e6804d9f6a000c493f4cc4",  # prompt_versions
    "36e3431ec8e680de85b2000c8a2d278a",  # evaluations
    "36e3431ec8e680b4b39e000c06943ed0",  # prompt_templates
]

try:
    # Initialize Notion client
    notion = Client(auth=NOTION_API_KEY)
    print("SUCCESS: Notion client created successfully")
    
    # Test connection to each database
    for i, db_id in enumerate(DATABASE_IDS):
        try:
            response = notion.databases.query(database_id=db_id, page_size=1)
            db_title = "Unknown"
            if hasattr(response, 'get'):
                db_title = response.get('title', [{'plain_text': 'Unknown'}])[0].get('plain_text', 'Unknown')
            print(f"SUCCESS: Database {i+1} accessible (ID: {db_id[:8]}..., Title: {db_title})")
        except Exception as db_error:
            print(f"ERROR: Database {i+1} access failed (ID: {db_id[:8]}...): {type(db_error).__name__}: {str(db_error)[:100]}")
            
except Exception as e:
    print(f"ERROR: Notion client initialization failed: {type(e).__name__}: {e}")