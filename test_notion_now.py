import os
from notion_client import Client

print("=== 测试Notion连接状态 ===")

NOTION_API_KEY = "ntn_your_notion_integration_secret"
database_id = "36d3431ec8e68076a1e7000c59505208"  # prompts数据库

try:
    notion = Client(auth=NOTION_API_KEY)
    print("✅ Notion客户端创建成功")
    
    # 尝试查询数据库
    response = notion.databases.retrieve(database_id=database_id)
    print("✅ 数据库访问成功")
    
    title = response.get("title", [{}])
    if title and isinstance(title, list) and len(title) > 0:
        db_title = title[0].get("plain_text", "N/A")
        print(f"📝 数据库标题: {db_title}")
    
    print("🎉 *** Notion连接成功！权限问题已解决 ***")
    
    # 进一步测试：尝试查询一些数据
    print("\n--- 进一步测试：查询数据库内容 ---")
    query_result = notion.databases.query(database_id=database_id, page_size=1)
    if query_result and hasattr(query_result, "results"):
        count = len(query_result.results)
        print(f"✅ 查询成功，找到 {count} 条记录")
        if count > 0:
            print(f"📄 第一条记录ID: {query_result.results[0].get('id', 'N/A')}")
    else:
        print("⚠️  查询成功但无结果（可能是空数据库）")
        
except Exception as e:
    print(f"❌ Notion访问失败: {type(e).__name__}: {e}")
    error_msg = str(e)
    if "Could not find database" in error_msg:
        print("🔍 错误说明: 集成能看到数据库但无访问权限")
        print("💡 解决方案: 检查集成的工作区成员权限")
    elif "API token is invalid" in error_msg:
        print("🔍 错误说明: API密钥无效")
    elif "rate limit" in error_msg.lower():
        print("🔍 错误说明: API速率限制")
    else:
        print("🔍 未知错误，需要进一步排查")