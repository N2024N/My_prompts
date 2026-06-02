<#
.SYNOPSIS
通过GitHub API创建仓库并推送代码（适用于无法访问GitHub网页的情况）

.DESCRIPTION
当GitHub网页被屏蔽但API可访问时，使用此脚本通过GitHub REST API创建仓库，
配置git远程仓库，并推送本地代码。

.步骤
1. 生成GitHub Personal Access Token（需要repo权限）
2. 运行此脚本，输入token和仓库名
3. 脚本通过API创建仓库
4. 配置git远程并推送代码

.注意
- 确保git-min已解压并可用
- 确保本地仓库已提交（git commit完成）
#>

param(
    [string]$GitHubToken,
    [string]$RepoName = "ai-prompt-studio",
    [string]$Description = "AI Prompt Engineering Studio - Notion-based prompt management tool",
    [switch]$Private = $false
)

# 设置错误处理
$ErrorActionPreference = "Stop"

# 检查必要工具
function Test-CommandExists {
    param([string]$Command)
    $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}

Write-Host "=== GitHub仓库创建脚本 ===" -ForegroundColor Cyan
Write-Host ""

# 1. 检查git是否可用
$gitPath = ".\git-min\mingw64\bin\git.exe"
if (-not (Test-Path $gitPath)) {
    Write-Host "❌ 未找到git.exe，请先解压MinGit到git-min目录" -ForegroundColor Red
    Write-Host "   MinGit zip文件应解压到: git-min\" -ForegroundColor Yellow
    Write-Host "   当前目录: $(Get-Location)" -ForegroundColor Gray
    exit 1
}

Write-Host "✅ Git可用: $((& $gitPath --version).Trim())" -ForegroundColor Green

# 2. 检查本地仓库状态
$gitStatus = & $gitPath status --porcelain
if ($gitStatus) {
    Write-Host "⚠️  本地仓库有未提交的更改:" -ForegroundColor Yellow
    $gitStatus | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
    Write-Host "  建议先提交更改 (git add . && git commit)" -ForegroundColor Yellow
    $confirm = Read-Host "是否继续? (y/N)"
    if ($confirm -ne 'y') { exit }
}

# 3. 获取GitHub Token
if (-not $GitHubToken) {
    Write-Host ""
    Write-Host "=== 需要GitHub Personal Access Token ===" -ForegroundColor Yellow
    Write-Host "1. 如果你已有Token，请在此输入" -ForegroundColor White
    Write-Host "2. 如果没有Token，需要生成：" -ForegroundColor White
    Write-Host "   a) 通过VPN或手机热点访问: https://github.com/settings/tokens" -ForegroundColor Gray
    Write-Host "   b) 点击 'Generate new token (classic)'" -ForegroundColor Gray
    Write-Host "   c) Token描述: 'AI Prompt Studio Deployment'" -ForegroundColor Gray
    Write-Host "   d) 勾选 'repo' 权限（全选）" -ForegroundColor Gray
    Write-Host "   e) 点击 'Generate token' 并复制token" -ForegroundColor Gray
    Write-Host ""
    Write-Host "注意: Token只显示一次，请妥善保存" -ForegroundColor Red
    Write-Host ""
    
    $GitHubToken = Read-Host "请输入GitHub Personal Access Token" -AsSecureString
    $GitHubToken = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($GitHubToken)
    )
}

if (-not $GitHubToken -or $GitHubToken.Length -lt 40) {
    Write-Host "❌ Token无效或太短" -ForegroundColor Red
    exit 1
}

# 4. 通过API创建仓库
Write-Host ""
Write-Host "=== 通过GitHub API创建仓库 ===" -ForegroundColor Cyan

$apiUrl = "https://api.github.com/user/repos"
$body = @{
    name        = $RepoName
    description = $Description
    private     = $Private
    auto_init   = $false  # 不初始化README，因为我们要推送现有代码
} | ConvertTo-Json

$headers = @{
    "Authorization" = "token $GitHubToken"
    "Accept"        = "application/vnd.github.v3+json"
    "User-Agent"    = "AI-Prompt-Studio-Deploy-Script"
}

try {
    Write-Host "正在创建仓库 '$RepoName'..." -ForegroundColor White
    $response = Invoke-RestMethod -Uri $apiUrl -Method POST -Headers $headers -Body $body -ContentType "application/json"
    
    Write-Host "✅ 仓库创建成功!" -ForegroundColor Green
    Write-Host "   仓库名: $($response.name)" -ForegroundColor Gray
    Write-Host "   仓库URL: $($response.html_url)" -ForegroundColor Gray
    Write-Host "   SSH URL: $($response.ssh_url)" -ForegroundColor Gray
    Write-Host "   HTTPS URL: $($response.clone_url)" -ForegroundColor Gray
    
    $cloneUrl = $response.clone_url
    
} catch {
    Write-Host "❌ 仓库创建失败: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        $statusDescription = $_.Exception.Response.StatusDescription
        Write-Host "   HTTP状态码: $statusCode ($statusDescription)" -ForegroundColor Yellow
        
        # 尝试读取错误详情
        try {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $errorBody = $reader.ReadToEnd()
            $reader.Close()
            $errorJson = $errorBody | ConvertFrom-Json -ErrorAction SilentlyContinue
            if ($errorJson) {
                Write-Host "   错误信息: $($errorJson.message)" -ForegroundColor Yellow
            }
        } catch {}
    }
    exit 1
}

# 5. 配置git远程仓库
Write-Host ""
Write-Host "=== 配置git远程仓库 ===" -ForegroundColor Cyan

# 检查是否已有远程仓库
$remotes = & $gitPath remote -v
if ($remotes) {
    Write-Host "当前远程仓库配置:" -ForegroundColor White
    $remotes | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
    
    $confirm = Read-Host "是否移除现有远程仓库并添加新的? (y/N)"
    if ($confirm -eq 'y') {
        & $gitPath remote remove origin 2>$null
    } else {
        Write-Host "❌ 用户取消操作" -ForegroundColor Yellow
        exit
    }
}

# 添加新的远程仓库（使用HTTPS URL，包含token）
$remoteUrl = $cloneUrl -replace '^https://', "https://$GitHubToken@"
& $gitPath remote add origin $remoteUrl

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 远程仓库配置成功" -ForegroundColor Green
} else {
    Write-Host "❌ 远程仓库配置失败" -ForegroundColor Red
    exit 1
}

# 6. 推送代码
Write-Host ""
Write-Host "=== 推送代码到GitHub ===" -ForegroundColor Cyan

Write-Host "正在推送代码到 'origin/main'..." -ForegroundColor White
& $gitPath push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 代码推送成功!" -ForegroundColor Green
    Write-Host ""
    Write-Host "=== 部署完成 ===" -ForegroundColor Green
    Write-Host "1. 访问仓库: $($response.html_url)" -ForegroundColor White
    Write-Host "2. 登录 Railway: https://railway.app" -ForegroundColor White
    Write-Host "3. 选择 'Deploy from GitHub'" -ForegroundColor White
    Write-Host "4. 选择 'ai-prompt-studio' 仓库" -ForegroundColor White
    Write-Host "5. Railway将自动构建部署" -ForegroundColor White
} else {
    Write-Host "❌ 代码推送失败" -ForegroundColor Red
    Write-Host "   尝试使用普通HTTPS URL（可能需要手动认证）..." -ForegroundColor Yellow
    
    # 使用普通URL重试（将弹出浏览器认证）
    & $gitPath remote set-url origin $cloneUrl
    & $gitPath push -u origin main
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 推送失败，请手动操作:" -ForegroundColor Red
        Write-Host "   1. 访问: $($response.html_url)" -ForegroundColor Gray
        Write-Host "   2. 手动执行: git push -u origin main" -ForegroundColor Gray
        Write-Host "   3. 如果要求登录，请使用浏览器认证" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "脚本执行完成!" -ForegroundColor Cyan