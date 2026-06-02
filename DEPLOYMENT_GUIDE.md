# AI Prompt Engineering Studio - Railway 部署指南

## 概述
本指南将帮助你将 AI Prompt Engineering Studio 部署到 Railway (railway.app)。Railway 是一个现代化的云平台，支持 Docker 和 Python 应用，提供自动 HTTPS、持续部署和简单的环境变量管理。

## 前提条件
1. **Railway 账户**：访问 [railway.app](https://railway.app) 注册（支持 GitHub 登录）
2. **GitHub 账户**（可选）：用于代码仓库同步
3. **环境变量**：确保已准备好以下密钥：
   - `NOTION_API_KEY`: `ntn_140109928707...`
   - `DEEPSEEK_API_KEY`: `sk-a1ede235812b...`
   - `SUPABASE_URL`: `https://nbdgzuuilowcaiazldve.supabase.co`
   - `SUPABASE_KEY`: `sb_secret_qDaUOyofEJ596T68w6kK3A_Xl_P2VsX`

## 部署选项

### 选项一：通过 GitHub 仓库部署（推荐）
**步骤 1：初始化 Git 仓库**
```bash
cd c:/Users/qiaole_900/WorkBuddy/20260527152739
git init
git add .
git commit -m "Initial commit: AI Prompt Engineering Studio"
```

**步骤 2：创建 GitHub 仓库**
1. 访问 [github.com/new](https://github.com/new)
2. 仓库名：`ai-prompt-engineering-studio`（或自定义）
3. 不要初始化 README、.gitignore 或 license
4. 创建仓库后，按照提示推送本地代码：
```bash
git remote add origin https://github.com/你的用户名/仓库名.git
git branch -M main
git push -u origin main
```

**步骤 3：连接 Railway**
1. 登录 [railway.app](https://railway.app)
2. 点击 "New Project" → "Deploy from GitHub repo"
3. 授权 Railway 访问你的 GitHub 账户
4. 选择刚才创建的仓库
5. Railway 会自动检测 Dockerfile 并开始部署

**步骤 4：配置环境变量**
1. 在 Railway 项目页面，进入 "Variables" 标签页
2. 添加以下环境变量：
   ```
   NOTION_API_KEY=ntn_140109928707...
   DEEPSEEK_API_KEY=sk-a1ede235812b...
   SUPABASE_URL=https://nbdgzuuilowcaiazldve.supabase.co
   SUPABASE_KEY=sb_secret_qDaUOyofEJ596T68w6kK3A_Xl_P2VsX
   ```
3. 保存后 Railway 会自动重启服务

**步骤 5：获取部署 URL**
1. 部署完成后，在 "Settings" → "Domains" 中查看默认域名
2. 默认格式：`https://你的项目名.up.railway.app`

### 选项二：使用 Railway CLI 部署（本地直接部署）
**步骤 1：安装 Railway CLI**
```bash
# Windows (PowerShell)
iwr -useb https://railway.app/install.ps1 | iex

# 或使用 npm
npm i -g @railway/cli
```

**步骤 2：登录 Railway**
```bash
railway login
```

**步骤 3：初始化项目**
```bash
cd c:/Users/qiaole_900/WorkBuddy/20260527152739
railway init
```

**步骤 4：部署**
```bash
railway up
```

**步骤 5：设置环境变量**
```bash
railway variables set NOTION_API_KEY=ntn_140109928707...
railway variables set DEEPSEEK_API_KEY=sk-a1ede235812b...
railway variables set SUPABASE_URL=https://nbdgzuuilowcaiazldve.supabase.co
railway variables set SUPABASE_KEY=sb_secret_qDaUOyofEJ596T68w6kK3A_Xl_P2VsX
```

### 选项三：通过 Railway Web 界面直接上传
1. 登录 Railway，点击 "New Project" → "Empty Project"
2. 在项目页面，点击 "Settings" → "General" → "Upload from local"
3. 选择项目文件夹（或压缩为 zip 上传）
4. Railway 会自动构建并部署

## 验证部署
部署完成后，访问以下端点验证服务：

1. **健康检查**：`https://你的域名/health`
   - 预期响应：`{"status":"healthy","timestamp":"..."}`

2. **Notion 集成测试**：`https://你的域名/notion/prompts`
   - 预期响应：显示 Prompts 数据库中的记录

3. **Supabase 集成测试**：`https://你的域名/supabase/stats`
   - 预期响应：显示激活码统计信息

## 故障排除

### 常见问题
1. **部署失败：端口绑定错误**
   - 确保 Dockerfile 中 CMD 使用端口 8000（Railway 默认）
   - Railway 会自动设置 `PORT` 环境变量，代码中已支持

2. **环境变量未生效**
   - 在 Railway 控制台检查变量是否已设置
   - 重启服务：`railway restart` 或 Web 界面点击 "Redeploy"

3. **Notion/Supabase 连接失败**
   - 检查 API 密钥是否正确
   - 确认网络可访问性（Railway 服务可访问外部 API）

4. **Docker 构建缓慢**
   - Railway 使用缓存，首次构建较慢
   - 可考虑使用 `.dockerignore` 排除不必要的文件

### 日志查看
```bash
# Railway CLI
railway logs

# 或通过 Web 界面查看
```

## 后续步骤
1. **自定义域名**：在 Railway "Settings" → "Domains" 中添加
2. **监控**：Railway 提供基本监控和日志
3. **自动伸缩**：Railway 默认自动伸缩，无需配置
4. **数据库备份**：Supabase 提供自动备份，可配置保留策略

## 技术支持
- Railway 文档：https://docs.railway.app
- 项目问题：查看 `README.md` 中的联系方式
- 紧急问题：通过 Railway 控制台提交支持请求