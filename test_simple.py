import os
from notion_client import Client
from supabase import create_client

print("=== Supabase 测试 ===")
SUPABASE_URL = "https://nbdgzuuilowcaiazldve.supabase.co"
keys = [
    "sb_publishable_uv2YamrT0CiUyaR9_-QHHw_hgyNVVA0",
    "sb_secret_E4qv-011de1r0MNTu-RnFw_gogvOgCP"
]

for key in keys:
    print(f"\n测试密钥: {key[:20]}...")
    try:
        supabase = create_client(SUPABASE_URL, key)
        print("客户端创建成功")
        # 尝试简单查询
        response = supabase.table("activation_codes").select("*").limit(1).execute()
        print(f"查询成功: {len(response.data)} 条记录")
        print("*** 这个密钥有效！ ***")
    except Exception as e:
        print(f"失败: {type(e).__name__}: {e}")

print("\n\n=== Notion 测试 ===")
NOTION_API_KEY = "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"
database_id = "36d3431ec8e68076a1e7000c59505208"  # prompts数据库

try:
    notion = Client(auth=NOTION_API_KEY)
    print("Notion客户端创建成功")
    
    # 尝试查询数据库
    response = notion.databases.retrieve(database_id=database_id)
    print(f"数据库访问成功")
    print(f"数据库标题: {response.get('title', [{}])[0].get('plain_text', 'N/A')}")
except Exception as e:
    print(f"Notion访问失败: {type(e).__name__}: {e}")
    if "Could not find database" in str(e):
        print("错误说明: 集成能看到数据库但无访问权限")
        print("解决方案: 检查集成的工作区成员权限")