#!/usr/bin/env python3
"""
Final integration test for AI Prompt Engineering Studio
Tests all components: Notion, Supabase, DeepSeek configuration
"""
import os
import sys
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

print("=" * 70)
print("AI Prompt Engineering Studio - Final Integration Test")
print("=" * 70)

# Test results
test_results = []

def test_step(name, func, *args):
    """Run a test step and record results"""
    print(f"\n{'='*60}")
    print(f"Test: {name}")
    print(f"{'='*60}")
    
    try:
        result = func(*args)
        test_results.append({"name": name, "status": "PASS", "details": result})
        print(f"[PASS] {name}")
        if result and isinstance(result, dict):
            for k, v in result.items():
                if k != "details":
                    print(f"   {k}: {v}")
        return True
    except Exception as e:
        test_results.append({"name": name, "status": "FAIL", "details": str(e)})
        print(f"[FAIL] {name}")
        print(f"   Error: {e}")
        return False

def test_env_vars():
    """Test required environment variables"""
    required = [
        ("NOTION_API_KEY", "Notion API Key"),
        ("DEEPSEEK_API_KEY", "DeepSeek API Key"),
        ("SUPABASE_URL", "Supabase Project URL"),
        ("SUPABASE_KEY", "Supabase Service Key")
    ]
    
    missing = []
    for var, desc in required:
        value = os.getenv(var)
        if not value:
            missing.append(f"{desc} ({var})")
        else:
            print(f"   ✅ {desc}: {value[:10]}...")
    
    if missing:
        raise ValueError(f"Missing environment variables: {', '.join(missing)}")
    
    return {
        "notion_api_key": "configured",
        "deepseek_api_key": "configured", 
        "supabase_url": "configured",
        "supabase_key": "configured"
    }

def test_notion_connection():
    """Test Notion API connection and database access"""
    from notion_client import Client
    
    api_key = os.getenv("NOTION_API_KEY")
    notion = Client(auth=api_key)
    
    # Database IDs (from main.py)
    databases = {
        "prompts": "36d3431ec8e680169aa5f78ff6c7e1e6",
        "prompt_versions": "36e3431ec8e68045a413fc20efd7a4c8",
        "evaluations": "36e3431ec8e6808cb129f5c60b0a56b9",
        "prompt_templates": "36e3431ec8e680009298ea5aff019272"
    }
    
    results = {}
    for name, db_id in databases.items():
        try:
            response = notion.databases.query(database_id=db_id, page_size=1)
            count = len(response.get('results', []))
            results[name] = {"status": "accessible", "record_count": count}
        except Exception as e:
            results[name] = {"status": "error", "error": str(e)[:100]}
    
    # Check all databases
    accessible = sum(1 for r in results.values() if r["status"] == "accessible")
    total = len(databases)
    
    if accessible < total:
        failed = [name for name, r in results.items() if r["status"] != "accessible"]
        raise ValueError(f"Only {accessible}/{total} databases accessible. Failed: {failed}")
    
    return {
        "accessible_databases": accessible,
        "total_databases": total,
        "details": results
    }

def test_supabase_connection():
    """Test Supabase connection and activation codes table"""
    from supabase_service import get_supabase_service
    
    service = get_supabase_service()
    
    # Test connection
    if not service.test_connection():
        raise ConnectionError("Supabase connection test failed")
    
    # Test stats query
    stats = service.get_activation_code_stats()
    
    if "error" in stats:
        raise ValueError(f"Supabase stats query failed: {stats['error']}")
    
    # Test validation (with a test code that likely exists)
    test_code = "TEST-12345"
    validation = service.validate_activation_code(test_code)
    
    return {
        "connection": "success",
        "total_codes": stats.get("total_codes", 0),
        "used_codes": stats.get("used_codes", 0),
        "available_codes": stats.get("available_codes", 0),
        "validation_test": validation.get("valid", False),
        "plan_distribution": stats.get("plan_distribution", {})
    }

def test_deepseek_config():
    """Test DeepSeek API configuration (without making actual call)"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not api_key or not api_key.startswith("sk-"):
        raise ValueError("DeepSeek API key missing or invalid format")
    
    # Test endpoint availability (just check if key looks valid)
    return {
        "api_key_format": "valid",
        "endpoint": "https://api.deepseek.com/v1/chat/completions"
    }

def test_fastapi_app():
    """Test FastAPI app can be imported and initialized"""
    # Try to import main app components
    try:
        from main import app, NOTION_DATABASE_IDS, NOTION_API_KEY, DEEPSEEK_API_KEY
        
        # Check app metadata
        title = app.title
        version = app.version
        
        # Check configuration
        config_ok = all([
            NOTION_API_KEY is not None,
            DEEPSEEK_API_KEY is not None,
            len(NOTION_DATABASE_IDS) == 4
        ])
        
        if not config_ok:
            raise ValueError("App configuration incomplete")
        
        return {
            "app_title": title,
            "app_version": version,
            "notion_databases": len(NOTION_DATABASE_IDS),
            "deepseek_configured": DEEPSEEK_API_KEY is not None
        }
        
    except ImportError as e:
        raise ImportError(f"Failed to import app modules: {e}")
    except Exception as e:
        raise Exception(f"App initialization failed: {e}")

def main():
    """Run all integration tests"""
    print("\n>>> Starting integration tests...")
    
    # Run tests in order
    tests = [
        ("Environment Variables", test_env_vars),
        ("Notion API Integration", test_notion_connection),
        ("Supabase Integration", test_supabase_connection),
        ("DeepSeek Configuration", test_deepseek_config),
        ("FastAPI Application", test_fastapi_app)
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        if not test_step(test_name, test_func):
            all_passed = False
            # Optionally continue other tests
            # break
    
    # Summary
    print(f"\n{'='*70}")
    print("TEST SUMMARY")
    print(f"{'='*70}")
    
    passed = sum(1 for r in test_results if r["status"] == "PASS")
    failed = sum(1 for r in test_results if r["status"] == "FAIL")
    
    print(f"Total Tests: {len(test_results)}")
    print(f"[PASS] Passed: {passed}")
    print(f"[FAIL] Failed: {failed}")
    
    if failed > 0:
        print("\nFailed tests:")
        for r in test_results:
            if r["status"] == "FAIL":
                print(f"  - {r['name']}: {r['details']}")
    
    # Overall status
    if all_passed:
        print(f"\n*** ALL TESTS PASSED! System is ready for deployment.")
        print("\nNext steps:")
        print("1. Deploy to Railway (railway.app)")
        print("2. Configure environment variables in Railway")
        print("3. Test production endpoints")
        print("4. Set up Gumroad integration")
        return 0
    else:
        print(f"\n!!! {failed} test(s) failed. Please fix before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())