#!/usr/bin/env python3
"""
Test Supabase statistics query
"""
import os
from dotenv import load_dotenv
from supabase_service import get_supabase_service

# Load environment variables
load_dotenv()

def test_stats():
    print("Testing Supabase statistics query...")
    
    try:
        # Get service instance
        service = get_supabase_service()
        print(f"Supabase URL: {service.url[:50]}...")
        
        # Test connection first
        if not service.test_connection():
            print("ERROR: Connection test failed")
            return
        
        print("Connection test successful")
        
        # Test stats query
        print("\nTesting get_activation_code_stats()...")
        stats = service.get_activation_code_stats()
        
        print(f"Stats result: {stats}")
        
        if "error" in stats:
            print(f"ERROR in stats query: {stats['error']}")
            # Try manual query
            test_manual_query(service)
        else:
            print(f"Success! Total codes: {stats.get('total_codes', 0)}")
            
    except Exception as e:
        print(f"Exception in test: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

def test_manual_query(service):
    """Test manual query to debug"""
    print("\n--- Manual query test ---")
    
    import requests
    
    # Get headers from service
    headers = service.headers
    table_url = f"{service.url}/rest/v1/activation_codes"
    
    print(f"Table URL: {table_url}")
    print(f"Headers: {headers}")
    
    # Try different query formats
    test_params = [
        {"select": "*"},
        {"select": "id,activation_code,status"},
        {"select": "id"},
        {},  # No params
    ]
    
    for i, params in enumerate(test_params):
        print(f"\nTest {i+1}: params={params}")
        try:
            response = requests.get(table_url, headers=headers, params=params)
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  Success! Got {len(data)} records")
                if data:
                    print(f"  First record keys: {list(data[0].keys())}")
                break
            else:
                print(f"  Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"  Exception: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_stats()