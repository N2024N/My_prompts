import os
from supabase import create_client, Client

# 从环境变量读取
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "sb_secret_your_secret_key_here"

print(f"URL: {SUPABASE_URL}")
print(f"Key: {SUPABASE_KEY[:20]}...")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Supabase客户端创建成功")
    
    # 尝试查询 activation_codes 表（应该为空）
    response = supabase.table("activation_codes").select("*").limit(1).execute()
    print(f"查询成功: {len(response.data)} 条记录")
    print("Supabase连接测试通过！")
except Exception as e:
    print(f"Supabase连接失败: {type(e).__name__}: {e}")