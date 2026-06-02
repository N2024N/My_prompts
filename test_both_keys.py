import os
from supabase import create_client, Client

SUPABASE_URL = "https://your-project.supabase.co"

# 测试两个密钥
keys_to_test = [
    ("sb_publishable_your_public_key_here", "可发布密钥 (anon/public)"),
    ("sb_secret_your_secret_key_here", "秘密密钥 (service role)")
]

for key, description in keys_to_test:
    print(f"\n=== 测试 {description} ===")
    print(f"密钥: {key[:20]}...")
    
    try:
        supabase: Client = create_client(SUPABASE_URL, key)
        print("✅ Supabase客户端创建成功")
        
        # 尝试查询 activation_codes 表
        response = supabase.table("activation_codes").select("*").limit(1).execute()
        print(f"✅ 查询成功: {len(response.data)} 条记录")
        print(f"🎉 {description} 测试通过！")
        
    except Exception as e:
        print(f"❌ 连接失败: {type(e).__name__}: {e}")
        
        # 如果是特定错误，提供建议
        if "Invalid API key" in str(e):
            print("💡 建议: 密钥可能已过期或需要重新生成")
        elif "JWT" in str(e):
            print("💡 建议: 密钥格式可能有问题")
        elif "permission" in str(e).lower():
            print("💡 建议: 密钥权限不足，可能需要service role key")