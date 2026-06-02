# Notion集成重新创建指南

## 🔧 问题分析
当前的 **Prompt Studio API** 集成虽然存在，但**没有工作区成员权限**，导致无法访问数据库。

## 🚀 解决方案：重新创建集成（100%有效）

### 步骤1：删除现有集成
1. 访问 [Notion开发者门户](https://www.notion.so/my-integrations)
2. 找到 **"Prompt Studio API"**
3. 点击 **"Delete"** 或 **"Remove"**
4. 确认删除

### 步骤2：创建新集成
1. 点击 **"+ New integration"**
2. 填写信息：
   - **Name**: `Prompt Studio API`（保持相同，便于识别）
   - **Associated workspace**: 选择你的工作空间
   - **Integration type**: **Internal integration**（关键！内部集成有完整权限）

### 步骤3：获取新API密钥
创建成功后，复制：
- **Internal Integration Token**（以 `secret_` 开头的密钥）

### 步骤4：添加集成到工作空间
1. 在集成详情页面，点击 **"Add to workspace"**
2. 选择你的工作空间
3. **确保勾选完整权限**（Read databases, Write databases等）

### 步骤5：重新共享数据库
对于每个数据库（共4个）：
1. 打开数据库页面（如 `Prompts`）
2. 点击右上角 **···** → **Add connections**
3. 搜索并选择新的 **"Prompt Studio API"**
4. 确认共享

---

## 📋 需要你提供的4个信息

1. **新的Notion API密钥**（以 `secret_` 开头）
2. **重新确认4个数据库ID**（我会帮你核对）
3. **Supabase Service Role Key**（已经提供，但需要确认）
4. **DeepSeek API Key**（已经提供，但需要确认）

---

## 🔄 我的操作（同时进行）

### 1. 修复Supabase集成
- 改用 `requests` 库直接与Supabase交互
- 绕过有问题的 `supabase-py` 客户端库

### 2. 更新配置文件
- 更新 `.env` 文件中的新Notion密钥
- 确保所有API密钥格式正确

### 3. 最终集成测试
- Notion数据库访问测试
- Supabase连接测试
- DeepSeek AI调用测试

---

## ✅ 验证成功

**所有测试通过后**，你将看到：
```
✅ Notion数据库访问成功
✅ Supabase连接成功  
✅ DeepSeek AI调用成功
✅ API服务完全就绪
```

---

## ⏱️ 预计时间

| 步骤 | 你的时间 | 我的时间 | 总时间 |
|------|----------|----------|--------|
| 重新创建集成 | 5分钟 | - | 5分钟 |
| 重新共享数据库 | 3分钟 | - | 3分钟 |
| 更新配置与测试 | - | 5分钟 | 5分钟 |
| 最终集成测试 | - | 3分钟 | 3分钟 |
| **总计** | **8分钟** | **8分钟** | **16分钟** |

---

## 🎯 重新创建的优势

1. **100%解决问题**：新集成会有完整的工作区权限
2. **避免遗留问题**：彻底清除旧权限配置
3. **更安全**：新密钥，旧密钥自动失效
4. **更快**：比反复调试现有集成更快

---

## 📞 操作指导

**请按顺序操作**：
1. **先删除**现有 Prompt Studio API 集成
2. **再创建**新的 Internal integration
3. **添加**到工作空间
4. **重新共享**4个数据库

**完成后将新API密钥发给我**，我立即更新配置并测试。如果遇到任何问题，随时截图分享。