#!/usr/bin/env python3
"""
Simple Notion database access test
"""
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

# ID candidates from user's URL
URL_PATH_ID = "36d3431ec8e680169aa5f78ff6c7e1e6"  # From p/{id}
URL_VIEW_ID = "36d3431ec8e68076a1e7000c59505208"   # From v={id}
CURRENT_ID = "36d3431ec8e68076a1e7000c59505208"

try:
    # Initialize Notion client
    notion = Client(auth=NOTION_API_KEY)
    print("Notion client created successfully")
    
    print("\nTesting database access with different IDs...")
    print("=" * 50)
    
    # Test 1: Current ID in code
    print(f"\nTest 1: Current ID in code")
    print(f"ID: {CURRENT_ID}")
    try:
        response = notion.databases.query(database_id=CURRENT_ID, page_size=1)
        print(f"SUCCESS - Database accessible")
        # Try to get title
        title = "Unknown"
        if hasattr(response, 'get'):
            title_list = response.get('title', [])
            if title_list and isinstance(title_list, list) and len(title_list) > 0:
                if isinstance(title_list[0], dict):
                    title = title_list[0].get('plain_text', 'Unknown')
        print(f"Database title: {title}")
    except Exception as e:
        print(f"FAILED: {type(e).__name__}: {str(e)[:100]}")
    
    # Test 2: URL path ID
    print(f"\nTest 2: URL path ID (from p/ in URL)")
    print(f"ID: {URL_PATH_ID}")
    try:
        response = notion.databases.query(database_id=URL_PATH_ID, page_size=1)
        print(f"SUCCESS - Database accessible")
        title = "Unknown"
        if hasattr(response, 'get'):
            title_list = response.get('title', [])
            if title_list and isinstance(title_list, list) and len(title_list) > 0:
                if isinstance(title_list[0], dict):
                    title = title_list[0].get('plain_text', 'Unknown')
        print(f"Database title: {title}")
    except Exception as e:
        print(f"FAILED: {type(e).__name__}: {str(e)[:100]}")
    
    # Test 3: URL view ID
    print(f"\nTest 3: URL view ID (from v= in URL)")
    print(f"ID: {URL_VIEW_ID}")
    try:
        response = notion.databases.query(database_id=URL_VIEW_ID, page_size=1)
        print(f"SUCCESS - Database accessible")
        title = "Unknown"
        if hasattr(response, 'get'):
            title_list = response.get('title', [])
            if title_list and isinstance(title_list, list) and len(title_list) > 0:
                if isinstance(title_list[0], dict):
                    title = title_list[0].get('plain_text', 'Unknown')
        print(f"Database title: {title}")
    except Exception as e:
        print(f"FAILED: {type(e).__name__}: {str(e)[:100]}")
    
    # Test 4: Try with hyphens in current ID
    print(f"\nTest 4: Current ID with hyphens")
    hyphen_id = f"{CURRENT_ID[:8]}-{CURRENT_ID[8:12]}-{CURRENT_ID[12:16]}-{CURRENT_ID[16:20]}-{CURRENT_ID[20:]}"
    print(f"ID: {hyphen_id}")
    try:
        response = notion.databases.query(database_id=hyphen_id, page_size=1)
        print(f"SUCCESS - Database accessible")
        title = "Unknown"
        if hasattr(response, 'get'):
            title_list = response.get('title', [])
            if title_list and isinstance(title_list, list) and len(title_list) > 0:
                if isinstance(title_list[0], dict):
                    title = title_list[0].get('plain_text', 'Unknown')
        print(f"Database title: {title}")
    except Exception as e:
        print(f"FAILED: {type(e).__name__}: {str(e)[:100]}")
    
    print("\n" + "=" * 50)
    print("Test completed")
    
except Exception as e:
    print(f"Notion client initialization failed: {type(e).__name__}: {e}")