"""
Check the actual columns in the activation_codes table.
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

# Try to query with minimal columns
table_url = f"{SUPABASE_URL}/rest/v1/activation_codes"

print("\n=== Test 1: Query with just id ===")
params = {"select": "id", "limit": "1"}
try:
    response = requests.get(table_url, headers=headers, params=params)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text[:200]}")
except Exception as e:
    print(f"Exception: {e}")

print("\n=== Test 2: Query with activation_code column ===")
params = {"select": "activation_code", "limit": "1"}
try:
    response = requests.get(table_url, headers=headers, params=params)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text[:200]}")
except Exception as e:
    print(f"Exception: {e}")

print("\n=== Test 3: Query with status column ===")
params = {"select": "status", "limit": "1"}
try:
    response = requests.get(table_url, headers=headers, params=params)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text[:200]}")
except Exception as e:
    print(f"Exception: {e}")

print("\n=== Test 4: Query with all common columns ===")
# Try different possible column names
for col_set in [["id", "activation_code", "status", "plan", "created_at"],
                ["id", "code", "is_used", "plan", "created_at"],
                ["id", "activation_code", "is_used", "plan", "created_at"]]:
    params = {"select": ",".join(col_set), "limit": "1"}
    print(f"\nTrying columns: {col_set}")
    try:
        response = requests.get(table_url, headers=headers, params=params)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Data keys: {list(data[0].keys()) if data else 'No data'}")
            break
        else:
            print(f"Error: {response.text[:200]}")
    except Exception as e:
        print(f"Exception: {e}")

print("\n=== Test 5: Insert a test record and check its structure ===")
test_data = {
    "activation_code": "TEST-STRUCTURE-001",
    "status": "unused",
    "plan": "standard"
}
try:
    response = requests.post(table_url, headers=headers, json=test_data)
    print(f"Insert status: {response.status_code}")
    if response.status_code == 201:
        record = response.json()
        print(f"Inserted record structure: {record}")
        
        # Clean up
        if isinstance(record, list) and len(record) > 0:
            record_id = record[0].get("id")
            delete_url = f"{table_url}?id=eq.{record_id}"
            delete_response = requests.delete(delete_url, headers=headers)
            print(f"Cleanup delete status: {delete_response.status_code}")
except Exception as e:
    print(f"Insert exception: {e}")

print("\n=== Check complete ===")