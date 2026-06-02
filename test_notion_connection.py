#!/usr/bin/env python3
"""
测试Notion API连接
"""
import os
import sys
from dotenv import load_dotenv
from notion_client import Client

# 加载环境变量
load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
if not NOTION_API_KEY:
    print("❌ 未找到NOTION_API_KEY环境变量")
    sys.exit(1)

# 数据库ID
DATABASE_IDS = {
    "prompts": "36d3431ec8e68076a1e7000c59505208",
    "prompt_versions": "36e3431ec8e6804d9f6a000c493f4cc4",
    "evaluations": "36e3431ec8e680de85b2000c8a2d278a",
    "prompt_templates": "36e3431ec8e680b4b39e000c06943ed0"
}

def test_notion_connection():
    """测试Notion连接和数据库访问"""
    print("[工具] 测试Notion API连接...")
    print(f"API Key: {NOTION_API_KEY[:15]}...")
    
    try:
        # 初始化客户端
        notion = Client(auth=NOTION_API_KEY)
        
        # 测试1: 获取用户信息（验证API密钥）
        print("\n[列表] 测试1: 验证API密钥...")
        user_info = notion.users.me()
        print(f"[成功] API密钥有效 - 用户: {user_info.get('name', 'Unknown')}")
        
        # 测试2: 检查每个数据库
        print("\n[列表] 测试2: 检查数据库访问权限...")
        for db_name, db_id in DATABASE_IDS.items():
            try:
                print(f"  检查 {db_name} 数据库 ({db_id[:8]}...)")
                response = notion.databases.retrieve(database_id=db_id)
                db_title = response.get("title", [])
                if isinstance(db_title, list) and db_title:
                    title_text = db_title[0].get("plain_text", "Untitled")
                else:
                    title_text = str(db_title)
                print(f"  [成功] {db_name}: '{title_text}' - 访问成功")
                
                # 额外：查询几条记录（如果有）
                try:
                    query_result = notion.databases.query(database_id=db_id, page_size=1)
                    count = len(query_result.get("results", []))
                    print(f"    包含 {count} 条记录")
                except Exception as query_error:
                    print(f"    [警告] 查询失败（可能无记录）: {str(query_error)[:100]}")
                    
            except Exception as db_error:
                print(f"  [失败] {db_name}: 访问失败 - {str(db_error)[:100]}")
                
        # 测试3: 创建测试记录（仅prompts数据库）
        print("\n[列表] 测试3: 测试创建记录...")
        try:
            test_title = "API集成测试 - 请删除"
            test_content = "这是通过API创建的测试记录，用于验证集成是否正常工作。"
            
            new_page = notion.pages.create(
                parent={"database_id": DATABASE_IDS["prompts"]},
                properties={
                    "Name": {
                        "title": [
                            {
                                "text": {
                                    "content": test_title
                                }
                            }
                        ]
                    },
                    "Content": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": test_content
                                }
                            }
                        ]
                    },
                    "Category": {
                        "select": {
                            "name": "test"
                        }
                    }
                }
            )
            
            page_id = new_page.get("id")
            print(f"[成功] 创建成功 - 页面ID: {page_id}")
            print(f"   标题: {test_title}")
            print(f"   URL: {new_page.get('url')}")
            
            # 记录测试页面的ID，以便后续清理
            with open("test_page_id.txt", "w") as f:
                f.write(page_id)
            
        except Exception as create_error:
            print(f"[失败] 创建失败: {str(create_error)[:150]}")
            
        print("\n[庆祝] Notion API集成测试完成！")
        
    except Exception as e:
        print(f"[失败] Notion连接失败: {str(e)}")
        sys.exit(1)

def test_supabase_connection():
    """测试Supabase连接"""
    print("\n[工具] 测试Supabase连接...")
    
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("[失败] 未找到Supabase环境变量")
        return
    
    print(f"URL: {SUPABASE_URL}")
    print(f"Key: {SUPABASE_KEY[:10]}...")
    
    try:
        # 尝试导入supabase
        from supabase import create_client, Client as SupabaseClient
        
        supabase: SupabaseClient = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # 测试查询activation_codes表
        print("\n[列表] 测试Supabase表访问...")
        try:
            response = supabase.table("activation_codes").select("*").limit(1).execute()
            print(f"[成功] activation_codes表访问成功")
            print(f"   表结构正常，当前记录数: {len(response.data)}")
            
            # 测试函数
            print("\n[列表] 测试数据库函数...")
            try:
                # 测试generate_activation_codes函数（生成1个测试码）
                result = supabase.rpc("generate_activation_codes", {"p_count": 1, "p_plan": "standard"}).execute()
                if result.data:
                    print(f"[成功] generate_activation_codes函数正常")
                    test_code = result.data[0].get("activation_code")
                    print(f"   生成的测试激活码: {test_code}")
                    
                    # 测试use_activation_code函数
                    use_result = supabase.rpc("use_activation_code", {"p_activation_code": test_code}).execute()
                    if use_result.data and use_result.data[0].get("success"):
                        print(f"[成功] use_activation_code函数正常 - 激活码使用成功")
                    else:
                        print(f"[警告] use_activation_code函数返回异常: {use_result.data}")
                else:
                    print("[警告] generate_activation_codes函数未返回数据")
                    
            except Exception as func_error:
                print(f"[失败] 函数测试失败: {str(func_error)[:100]}")
                
        except Exception as table_error:
            print(f"[失败] 表访问失败: {str(table_error)[:100]}")
            print("   请确认supabase_schema.sql已正确执行")
            
    except ImportError:
        print("[失败] supabase库未安装")
    except Exception as e:
        print(f"[失败] Supabase连接失败: {str(e)[:150]}")

if __name__ == "__main__":
    print("=" * 60)
    print("AI Prompt Engineering Studio - 集成测试")
    print("=" * 60)
    
    test_notion_connection()
    test_supabase_connection()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)