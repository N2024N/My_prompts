import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_VERSION = "2022-06-28"

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json"
}

print("Testing Notion Integration...")
print(f"API Key (first 20 chars): {NOTION_API_KEY[:20]}...")

# 1. 测试列出数据库
print("\n1. Testing database list...")
try:
    response = requests.post(
        "https://api.notion.com/v1/search",
        headers=headers,
        json={"filter": {"property": "object", "value": "database"}}
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data.get('results', []))} databases")
        for db in data.get('results', []):
            print(f"  - {db.get('title', [{}])[0].get('plain_text', 'Untitled')} (ID: {db['id']})")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")

# 2. 测试特定数据库（prompts）
print("\n2. Testing specific database (prompts)...")
db_id = "36d3431ec8e68076a1e7000c59505208"
try:
    response = requests.get(
        f"https://api.notion.com/v1/databases/{db_id}",
        headers=headers
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Database title: {data.get('title', [{}])[0].get('plain_text', 'Untitled')}")
        print(f"Database URL: {data.get('url', 'N/A')}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")

# 3. 测试查询数据库内容
print("\n3. Testing database query...")
try:
    response = requests.post(
        f"https://api.notion.com/v1/databases/{db_id}/query",
        headers=headers,
        json={"page_size": 1}
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data.get('results', []))} pages")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")