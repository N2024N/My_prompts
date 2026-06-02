#!/usr/bin/env python3
"""
Test script for Notion API integration.
"""
import os
import sys
from dotenv import load_dotenv
from notion_client import Client

# Load environment variables
load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
if not NOTION_API_KEY:
    print("ERROR: NOTION_API_KEY not found in environment variables")
    sys.exit(1)

# Database IDs
DATABASE_IDS = {
    "prompts": "36d3431ec8e68076a1e7000c59505208",
    "prompt_versions": "36e3431ec8e6804d9f6a000c493f4cc4",
    "evaluations": "36e3431ec8e680de85b2000c8a2d278a",
    "prompt_templates": "36e3431ec8e680b4b39e000c06943ed0"
}

try:
    # Initialize client
    notion = Client(auth=NOTION_API_KEY)
    
    # Test connection by retrieving database info
    database_id = DATABASE_IDS["prompts"]
    print(f"Testing connection to Notion database: {database_id}")
    
    # Get database info
    db_info = notion.databases.retrieve(database_id=database_id)
    print(f"✅ Database found: {db_info.get('title', [{}])[0].get('plain_text', 'Untitled')}")
    
    # Query a few pages
    response = notion.databases.query(database_id=database_id, page_size=5)
    pages = response.get("results", [])
    
    print(f"✅ Found {len(pages)} pages in database")
    
    for i, page in enumerate(pages):
        props = page.get("properties", {})
        title = "Untitled"
        for prop_name, prop_value in props.items():
            if prop_value.get("type") == "title" and prop_value.get("title"):
                title = prop_value["title"][0].get("plain_text", "Untitled")
                break
        
        print(f"  {i+1}. {title} ({page.get('id')})")
    
    print("\n✅ Notion API integration test PASSED")
    
except Exception as e:
    print(f"❌ Notion API integration test FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)