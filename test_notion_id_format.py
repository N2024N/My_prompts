#!/usr/bin/env python3
"""
Notion数据库ID格式测试脚本
测试用户提供的URL中的两种ID格式
"""
import os
from notion_client import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Notion API key
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
if not NOTION_API_KEY:
    print("❌ ERROR: NOTION_API_KEY not found in .env file")
    exit(1)

print(f"🔑 NOTION_API_KEY found: {NOTION_API_KEY[:10]}...")

# ID candidates from user's URL
# URL: https://app.notion.com/p/36d3431ec8e680169aa5f78ff6c7e1e6?v=36d3431ec8e68076a1e7000c59505208
URL_PATH_ID = "36d3431ec8e680169aa5f78ff6c7e1e6"  # From p/{id}
URL_VIEW_ID = "36d3431ec8e68076a1e7000c59505208"   # From v={id}

# Current ID in code
CURRENT_ID = "36d3431ec8e68076a1e7000c59505208"

# Test with and without hyphens
def add_hyphens(db_id):
    """Convert 32-char ID to 8-4-4-4-12 format"""
    if len(db_id) == 32 and '-' not in db_id:
        return f"{db_id[:8]}-{db_id[8:12]}-{db_id[12:16]}-{db_id[16:20]}-{db_id[20:]}"
    return db_id

# All ID variants to test
ID_VARIANTS = [
    ("current_no_hyphen", CURRENT_ID),
    ("current_with_hyphen", add_hyphens(CURRENT_ID)),
    ("url_path_no_hyphen", URL_PATH_ID),
    ("url_path_with_hyphen", add_hyphens(URL_PATH_ID)),
    ("url_view_no_hyphen", URL_VIEW_ID),
    ("url_view_with_hyphen", add_hyphens(URL_VIEW_ID)),
]

try:
    # Initialize Notion client
    notion = Client(auth=NOTION_API_KEY)
    print("✅ Notion客户端创建成功")
    
    success_count = 0
    
    print(f"\n🔍 测试 {len(ID_VARIANTS)} 种ID格式...")
    print("=" * 60)
    
    for variant_name, db_id in ID_VARIANTS:
        try:
            print(f"\n📊 测试: {variant_name}")
            print(f"   ID: {db_id}")
            
            # Try to query the database
            response = notion.databases.query(database_id=db_id, page_size=1)
            
            # If successful, extract database info
            db_title = "Unknown"
            if hasattr(response, 'get'):
                title_list = response.get('title', [])
                if title_list and isinstance(title_list, list) and len(title_list) > 0:
                    if isinstance(title_list[0], dict):
                        db_title = title_list[0].get('plain_text', 'Unknown')
            
            print(f"   ✅ 成功！数据库标题: {db_title}")
            
            # Try to get record count
            try:
                count_response = notion.databases.query(database_id=db_id, page_size=100)
                result_count = len(count_response.get('results', []))
                print(f"   记录数: {result_count}")
            except:
                print(f"   记录数: 读取失败（但有访问权限）")
            
            success_count += 1
            
        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ 失败: {type(e).__name__}")
            if "Could not find database" in error_msg:
                print(f"     原因: 数据库未找到或权限不足")
            elif "permission" in error_msg.lower():
                print(f"     原因: 权限问题")
            elif "rate limit" in error_msg.lower():
                print(f"     原因: 速率限制")
            else:
                print(f"     原因: {error_msg[:80]}")
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 测试结果汇总:")
    print(f"  ✅ 成功: {success_count}/{len(ID_VARIANTS)}")
    print(f"  ❌ 失败: {len(ID_VARIANTS) - success_count}/{len(ID_VARIANTS)}")
    
    if success_count > 0:
        print("\n🎉 找到有效的数据库ID格式！")
        # Find the successful ones
        print("\n有效ID格式:")
        for variant_name, db_id in ID_VARIANTS:
            # We can't track which ones succeeded without storing results
            # Will just show all variants
            pass
    else:
        print("\n🔴 所有ID格式测试失败，可能是权限问题")
        print("建议：重新创建Notion集成")
        
except Exception as e:
    print(f"❌ Notion客户端初始化失败: {type(e).__name__}: {e}")
    print("\n可能原因:")
    print("1. API密钥无效")
    print("2. 网络连接问题")
    print("3. Notion服务暂时不可用")