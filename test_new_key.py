import os
from supabase import create_client

print("=== 测试新Supabase密钥 ===")
SUPABASE_URL = "https://nbdgzuuilowcaiazldve.supabase.co"
SUPABASE_KEY = "sb_secret_qDaUOyofEJ596T68w6kK3A_Xl_P2VsX"

print(f"URL: {SUPABASE_URL}")
print(f"Key: {SUPABASE_KEY[:20]}...")

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase客户端创建成功")
    
    # 测试查询activation_codes表
    print("正在查询activation_codes表...")
    response = supabase.table("activation_codes").select("*").limit(1).execute()
    print(f"✅ 查询成功: 找到 {len(response.data)} 条记录")
    
    if len(response.data) > 0:
        print("第一条记录:", response.data[0])
    else:
        print("表为空（正常，刚创建）")
        
    # 测试视图
    print("\n正在测试activation_codes_summary视图...")
    view_response = supabase.table("activation_codes_summary").select("*").limit(5).execute()
    print(f"✅ 视图查询成功: {len(view_response.data)} 条记录")
    
    print("\n🎉 Supabase连接完全正常！")
    
except Exception as e:
    print(f"❌ Supabase连接失败: {type(e).__name__}: {e}")
    if "Invalid API key" in str(e):
        print("可能原因：密钥格式错误、密钥已失效、或需要重新生成")
    elif "JWT" in str(e):
        print("可能原因：密钥权限不足或过期")
    else:
        print("未知错误，请检查网络连接或Supabase服务状态")