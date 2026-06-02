# 清理和部署脚本
Write-Host "=== C盘清理与部署脚本 ===" -ForegroundColor Green

# 1. 清理临时文件
Write-Host "`n[1/5] 清理临时文件..." -ForegroundColor Yellow
$tempPaths = @(
    "$env:TEMP",
    "$env:SystemRoot\Temp",
    "$env:LOCALAPPDATA\Temp",
    "C:\Windows\Temp"
)

foreach ($path in $tempPaths) {
    if (Test-Path $path) {
        try {
            Get-ChildItem -Path $path -File -Recurse -ErrorAction SilentlyContinue | 
                Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-7)} |
                Remove-Item -Force -ErrorAction SilentlyContinue
            Write-Host "  清理完成: $path" -ForegroundColor Gray
        } catch {
            Write-Host "  跳过: $path (无权限)" -ForegroundColor DarkGray
        }
    }
}

# 2. 清理下载文件夹（30天前）
Write-Host "`n[2/5] 清理下载文件夹..." -ForegroundColor Yellow
$downloadPath = "$env:USERPROFILE\Downloads"
if (Test-Path $downloadPath) {
    try {
        $oldFiles = Get-ChildItem -Path $downloadPath -File -ErrorAction SilentlyContinue |
            Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)}
        $oldCount = ($oldFiles | Measure-Object).Count
        $oldFiles | Remove-Item -Force -ErrorAction SilentlyContinue
        Write-Host "  删除 $oldCount 个旧文件" -ForegroundColor Gray
    } catch {
        Write-Host "  跳过下载文件夹清理" -ForegroundColor DarkGray
    }
}

# 3. 清理软件缓存
Write-Host "`n[3/5] 清理软件缓存..." -ForegroundColor Yellow
$cachePaths = @(
    "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Cache",
    "$env:LOCALAPPDATA\Microsoft\Windows\INetCache",
    "$env:LOCALAPPDATA\Microsoft\Windows\INetCookies"
)

foreach ($path in $cachePaths) {
    if (Test-Path $path) {
        try {
            Remove-Item -Path "$path\*" -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "  清理完成: $(Split-Path $path -Leaf)" -ForegroundColor Gray
        } catch {
            # 忽略权限错误
        }
    }
}

# 4. 清理回收站
Write-Host "`n[4/5] 清理回收站..." -ForegroundColor Yellow
try {
    $shell = New-Object -ComObject Shell.Application
    $recycleBin = $shell.Namespace(0xA)
    $recycleBin.InvokeVerb("Empty Recycle Bin")
    Write-Host "  回收站已清空" -ForegroundColor Gray
} catch {
    Write-Host "  回收站清理失败 (可能需要手动清理)" -ForegroundColor DarkGray
}

# 5. 显示磁盘空间
Write-Host "`n[5/5] 磁盘空间报告..." -ForegroundColor Yellow
Get-WmiObject Win32_LogicalDisk -Filter "DeviceID='C:'" | ForEach-Object {
    $totalGB = [math]::Round($_.Size/1GB, 2)
    $freeGB = [math]::Round($_.FreeSpace/1GB, 2)
    $usedGB = $totalGB - $freeGB
    $usagePercent = [math]::Round(($usedGB/$totalGB)*100, 1)
    
    Write-Host "  C盘容量: $totalGB GB" -ForegroundColor Gray
    Write-Host "  已使用: $usedGB GB ($usagePercent%)" -ForegroundColor Gray
    Write-Host "  可用空间: $freeGB GB" -ForegroundColor Green
}

Write-Host "`n=== 清理完成 ===" -ForegroundColor Green
Write-Host "`n下一步:"
Write-Host "1. 登录 Railway (railway.app)"
Write-Host "2. 进入项目 'graceful-strength'"
Write-Host "3. 在画布上点击 'Add a Service'"
Write-Host "4. 选择 'GitHub repo' 或 'Docker Image'"
Write-Host "`n如果需要CLI部署:"
Write-Host "1. 下载 Node.js: https://nodejs.org/"
Write-Host "2. 安装后运行: npm install -g @railway/cli"
Write-Host "3. railway login"
Write-Host "4. cd 到项目目录，运行 railway up"

# 暂停查看结果
Write-Host "`n按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")