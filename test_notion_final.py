#!/usr/bin/env python3
"""
最终Notion权限测试脚本
测试所有4个数据库的访问权限
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

# Test database IDs with names
DATABASES = [
    ("prompts", "36d3431ec8e68076a1e7000c59505208"),
    ("prompt_versions", "36e3431ec8e6804d9f6a000c493f4cc4"),
    ("evaluations", "36e3431ec8e680de85b2000c8a2d278a"),
    ("prompt_templates", "36e3431ec8e680b4b39e000c06943ed0"),
]

try:
    # Initialize Notion client
    notion = Client(auth=NOTION_API_KEY)
    print("✅ Notion客户端创建成功")
    
    success_count = 0
    total_count = len(DATABASES)
    
    # Test connection to each database
    for db_name, db_id in DATABASES:
        try:
            print(f"\n📊 测试数据库: {db_name} (ID: {db_id[:8]}...)")
            response = notion.databases.query(database_id=db_id, page_size=1)
            
            # Extract database title
            db_title = "Unknown"
            if hasattr(response, 'get'):
                # Try to get title from response
                title_list = response.get('title', [])
                if title_list and isinstance(title_list, list) and len(title_list) > 0:
                    if isinstance(title_list[0], dict):
                        db_title = title_list[0].get('plain_text', 'Unknown')
            
            print(f"  ✅ 可访问 - 标题: {db_title}")
            
            # Count records if accessible
            try:
                count_response = notion.databases.query(database_id=db_id, page_size=100)
                result_count = len(count_response.get('results', []))
                print(f"  📈 记录数: {result_count}")
            except:
                print(f"  📈 记录数: 读取失败（但有访问权限）")
            
            success_count += 1
            
        except Exception as db_error:
            error_msg = str(db_error)
            print(f"  ❌ 访问失败: {type(db_error).__name__}")
            if "Could not find database" in error_msg:
                print(f"    原因: 数据库未找到或权限不足")
            elif "permission" in error_msg.lower():
                print(f"    原因: 权限问题")
            else:
                print(f"    原因: {error_msg[:100]}")
    
    # Summary
    print(f"\n{'='*50}")
    print("📋 测试结果汇总:")
    print(f"  ✅ 成功: {success_count}/{total_count}")
    print(f"  ❌ 失败: {total_count - success_count}/{total_count}")
    
    if success_count == total_count:
        print("\n🎉 所有数据库访问权限正常！Notion集成已修复！")
    elif success_count > 0:
        print(f"\n⚠️  部分数据库可访问，但仍有{total_count - success_count}个失败")
    else:
        print("\n🔴 所有数据库访问失败，请检查权限设置")
    
except Exception as e:
    print(f"❌ Notion客户端初始化失败: {type(e).__name__}: {e}")