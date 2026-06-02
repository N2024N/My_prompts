import requests
import json

print("=== 直接测试Supabase REST API ===")

SUPABASE_URL = "https://nbdgzuuilowcaiazldve.supabase.co"
# 测试三个密钥
keys = [
    "sb_publishable_uv2YamrT0CiUyaR9_-QHHw_hgyNVVA0",  # anon/public key
    "sb_secret_E4qv-011de1r0MNTu-RnFw_gogvOgCP",       # 旧secret key
    "sb_secret_qDaUOyofEJ596T68w6kK3A_Xl_P2VsX"        # 新secret key
]

# 测试1: 使用apikey头访问REST端点
print("\n--- 测试1: 使用apikey头访问REST ---")
for i, key in enumerate(keys, 1):
    print(f"\n密钥 {i}: {key[:20]}...")
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}"
    }
    
    # 测试rest/v1/端点
    try:
        response = requests.get(f"{SUPABASE_URL}/rest/v1/", headers=headers)
        print(f"  REST端点状态: {response.status_code}")
        if response.status_code == 200:
            print(f"  *** 这个密钥可能有效！ ***")
            print(f"  响应头: {dict(response.headers)}")
        else:
            print(f"  错误: {response.text[:200]}")
    except Exception as e:
        print(f"  请求失败: {type(e).__name__}: {e}")

# 测试2: 使用PostgREST直接查询表
print("\n--- 测试2: 直接查询activation_codes表 ---")
for i, key in enumerate(keys, 1):
    print(f"\n密钥 {i}: {key[:20]}...")
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    
    # 通过PostgREST查询表
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/activation_codes?select=*&limit=1",
            headers=headers
        )
        print(f"  表查询状态: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  *** 查询成功！找到 {len(data)} 条记录 ***")
            if len(data) > 0:
                print(f"  第一条记录: {json.dumps(data[0], indent=2)}")
        else:
            print(f"  错误: {response.text[:200]}")
    except Exception as e:
        print(f"  查询失败: {type(e).__name__}: {e}")

print("\n=== 测试完成 ===")