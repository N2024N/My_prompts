# Git下载状态检查脚本
Write-Host "=== Git下载状态检查 ===" -ForegroundColor Cyan

# 检查git.exe是否存在
$gitPath = "git-min\bin\git.exe"
if (Test-Path $gitPath) {
    Write-Host "✅ Git已安装" -ForegroundColor Green
    Write-Host "位置: $((Get-Item $gitPath).FullName)" -ForegroundColor Gray
    Write-Host "版本: " -NoNewline -ForegroundColor Gray
    & $gitPath --version
} else {
    Write-Host "❌ Git未找到" -ForegroundColor Red
    Write-Host ""
    
    # 检查zip文件是否存在
    $zipPath = "D:\Download\MinGit-2.54.0-64-bit.zip"
    if (Test-Path $zipPath) {
        Write-Host "✅ MinGit zip文件已下载: $zipPath" -ForegroundColor Green
        Write-Host ""
        Write-Host "=== 解压指南 ===" -ForegroundColor Yellow
        Write-Host "执行以下命令解压:" -ForegroundColor White
        Write-Host "cd c:\Users\qiaole_900\WorkBuddy\20260527152739" -ForegroundColor Gray
        Write-Host "Expand-Archive -Path '$zipPath' -DestinationPath 'git-min' -Force" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "或使用Windows资源管理器:" -ForegroundColor White
        Write-Host "1. 右键点击 $zipPath" -ForegroundColor Gray
        Write-Host "2. 选择'全部解压...'" -ForegroundColor Gray
        Write-Host "3. 目标文件夹: c:\Users\qiaole_900\WorkBuddy\20260527152739\git-min\" -ForegroundColor Gray
    } else {
        Write-Host "❌ 未找到MinGit zip文件" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "=== 下载指南 ===" -ForegroundColor Yellow
        Write-Host "1. 最新下载链接: https://github.com/git-for-windows/git/releases/download/v2.54.0.windows.1/MinGit-2.54.0-64-bit.zip"
        Write-Host "2. 国内镜像: https://npm.taobao.org/mirrors/git-for-windows/v2.54.0/MinGit-2.54.0-64-bit.zip"
        Write-Host "3. 保存到: D:\Download\" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "备用方案: GitHub网页上传" -ForegroundColor Magenta
    Write-Host "如果解压失败，直接访问 https://github.com/new 创建仓库并上传文件" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=== 项目状态 ===" -ForegroundColor Cyan
$mainFiles = @("main.py", "requirements.txt", "Dockerfile", "README.md")
foreach ($file in $mainFiles) {
    if (Test-Path $file) {
        Write-Host "✅ $file" -ForegroundColor Green
    } else {
        Write-Host "❌ $file 缺失" -ForegroundColor Red
    }
}