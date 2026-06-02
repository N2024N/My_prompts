"""
Check Supabase table structure to see what's actually created.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print(f"SUPABASE_URL: {SUPABASE_URL}")
print(f"SUPABASE_KEY: {SUPABASE_KEY[:20]}...")

# Headers
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# 1. Check if we can connect to REST endpoint
try:
    print("\n=== Checking REST endpoint ===")
    response = requests.get(f"{SUPABASE_URL}/rest/v1/", headers=headers)
    print(f"REST endpoint status: {response.status_code}")
    if response.status_code == 200:
        print("SUCCESS: REST endpoint accessible")
except Exception as e:
    print(f"ERROR: Cannot access REST endpoint: {e}")

# 2. Check if activation_codes table exists
try:
    print("\n=== Checking activation_codes table ===")
    table_url = f"{SUPABASE_URL}/rest/v1/activation_codes"
    response = requests.get(table_url, headers=headers, params={"limit": "1"})
    print(f"Table check status: {response.status_code}")
    
    if response.status_code == 200:
        print("SUCCESS: Table exists and is accessible")
        # Try to get column info
        print("\n=== Getting table columns ===")
        # Use PostgREST to get table info
        info_url = f"{SUPABASE_URL}/rest/v1/rpc/get_table_info"
        # Actually, let's just try to query with no columns
        response = requests.get(table_url, headers=headers, params={"select": "*", "limit": "0"})
        if response.status_code == 200:
            print("Table query successful")
            # The response headers might have info
            print(f"Response headers: {dict(response.headers)}")
        else:
            print(f"Table query failed: {response.status_code} - {response.text[:200]}")
    else:
        print(f"ERROR: Table check failed: {response.status_code} - {response.text[:200]}")
        
except Exception as e:
    print(f"ERROR: Table check exception: {type(e).__name__}: {e}")

# 3. Try a simple insert to see error details
try:
    print("\n=== Testing simple insert ===")
    table_url = f"{SUPABASE_URL}/rest/v1/activation_codes"
    test_data = {
        "activation_code": "TEST-12345",
        "status": "unused",
        "plan": "standard"
    }
    response = requests.post(table_url, headers=headers, json=test_data)
    print(f"Insert test status: {response.status_code}")
    if response.status_code == 201:
        print("SUCCESS: Insert test passed")
        # Clean up - delete the test record
        record_id = response.json()[0].get("id")
        if record_id:
            delete_url = f"{table_url}?id=eq.{record_id}"
            delete_response = requests.delete(delete_url, headers=headers)
            print(f"Cleanup delete status: {delete_response.status_code}")
    else:
        print(f"Insert test failed: {response.text[:200]}")
        
except Exception as e:
    print(f"ERROR: Insert test exception: {type(e).__name__}: {e}")

print("\n=== Check complete ===")