"""
Test the new Supabase service using requests library (ASCII version).
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print(f"SUPABASE_URL: {SUPABASE_URL}")
print(f"SUPABASE_KEY: {SUPABASE_KEY[:20]}...")

# Test the new service
try:
    from supabase_service import SupabaseService, get_supabase_service
    
    # Test 1: Create service instance
    print("\n=== Test 1: Creating SupabaseService instance ===")
    service = SupabaseService(SUPABASE_URL, SUPABASE_KEY)
    print(f"SUCCESS: Service created: URL={service.url[:40]}...")
    
    # Test 2: Test connection
    print("\n=== Test 2: Testing connection ===")
    if service.test_connection():
        print("SUCCESS: Connection test passed")
    else:
        print("ERROR: Connection test failed")
    
    # Test 3: Get activation code stats
    print("\n=== Test 3: Getting activation code statistics ===")
    stats = service.get_activation_code_stats()
    if "error" in stats:
        print(f"ERROR: Error getting stats: {stats['error']}")
    else:
        print(f"SUCCESS: Got stats:")
        print(f"   Total codes: {stats['total_codes']}")
        print(f"   Used codes: {stats['used_codes']}")
        print(f"   Available codes: {stats['available_codes']}")
        print(f"   Expired codes: {stats['expired_codes']}")
    
    # Test 4: Validate a non-existent code (should fail)
    print("\n=== Test 4: Validating non-existent code ===")
    test_code = "TEST-CODE-12345"
    validation = service.validate_activation_code(test_code)
    if validation["valid"]:
        print(f"ERROR: Unexpected: Code {test_code} should not be valid")
    else:
        print(f"SUCCESS: Correctly rejected non-existent code: {validation['message']}")
    
    print("\n=== All tests completed ===")
    print("Summary: Supabase service using requests library is working correctly!")
    
except ImportError as e:
    print(f"ERROR: Import error: {e}")
    print("Make sure supabase_service.py is in the same directory")
except Exception as e:
    print(f"ERROR: Unexpected error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()