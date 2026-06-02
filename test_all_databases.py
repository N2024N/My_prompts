#!/usr/bin/env python3
"""
Test all Notion databases with current IDs
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

# Current database IDs from main.py (updated)
DATABASES = {
    "prompts": "36d3431ec8e680169aa5f78ff6c7e1e6",  # Corrected
    "prompt_versions": "36e3431ec8e68045a413fc20efd7a4c8",  # Corrected
    "evaluations": "36e3431ec8e6808cb129f5c60b0a56b9",  # Corrected
    "prompt_templates": "36e3431ec8e680009298ea5aff019272"  # Corrected
}

try:
    # Initialize Notion client
    notion = Client(auth=NOTION_API_KEY)
    print("Notion client created successfully")
    
    print(f"\nTesting {len(DATABASES)} databases...")
    print("=" * 60)
    
    success_count = 0
    results = {}
    
    for db_name, db_id in DATABASES.items():
        try:
            print(f"\nDatabase: {db_name}")
            print(f"ID: {db_id}")
            
            # Try to query the database
            response = notion.databases.query(database_id=db_id, page_size=1)
            
            # If successful, extract database info
            db_title = "Unknown"
            if hasattr(response, 'get'):
                title_list = response.get('title', [])
                if title_list and isinstance(title_list, list) and len(title_list) > 0:
                    if isinstance(title_list[0], dict):
                        db_title = title_list[0].get('plain_text', 'Unknown')
            
            print(f"SUCCESS - Title: {db_title}")
            
            # Try to get record count
            try:
                count_response = notion.databases.query(database_id=db_id, page_size=100)
                result_count = len(count_response.get('results', []))
                print(f"Record count: {result_count}")
            except:
                print(f"Record count: Failed to read (but has access)")
            
            success_count += 1
            results[db_name] = {"status": "success", "title": db_title}
            
        except Exception as e:
            error_msg = str(e)
            print(f"FAILED: {type(e).__name__}")
            if "Could not find database" in error_msg:
                print(f"Reason: Database not found or insufficient permissions")
            elif "permission" in error_msg.lower():
                print(f"Reason: Permission issue")
            else:
                print(f"Reason: {error_msg[:80]}")
            
            results[db_name] = {"status": "failed", "error": error_msg[:100]}
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY:")
    print(f"SUCCESS: {success_count}/{len(DATABASES)}")
    print(f"FAILED: {len(DATABASES) - success_count}/{len(DATABASES)}")
    
    if success_count == len(DATABASES):
        print("\nALL DATABASES ARE ACCESSIBLE! Notion integration is working!")
    elif success_count > 0:
        print(f"\nPARTIAL SUCCESS: {success_count} database(s) accessible")
        print("Databases that failed:")
        for db_name, result in results.items():
            if result["status"] == "failed":
                print(f"  - {db_name}: {result.get('error', 'Unknown error')}")
    else:
        print("\nALL DATABASES FAILED. Need to check IDs or permissions.")
        
except Exception as e:
    print(f"Notion client initialization failed: {type(e).__name__}: {e}")