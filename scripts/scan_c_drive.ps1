# ============================================================
#  C 盘杂物扫描 - 只读,不删任何东西
#  输出: D:\Hermes\C_drive_scan_<timestamp>.md
# ============================================================
$ErrorActionPreference = "SilentlyContinue"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$reportPath = "D:\Hermes\C_drive_scan_$timestamp.md"

$userProfile = $env:USERPROFILE
$computerName = $env:COMPUTERNAME

$targets = @(
    @{ Risk="S1";   Name="系统临时目录 WindowsTemp";                Path="C:\Windows\Temp" }
    @{ Risk="S1";   Name="用户临时目录 AppDataLocalTemp";           Path=Join-Path $userProfile "AppData\Local\Temp" }
    @{ Risk="S1";   Name="回收站 RecycleBin";                       Path="C:\`$Recycle.Bin" }
    @{ Risk="S1";   Name="Windows Update 缓存";                     Path="C:\Windows\SoftwareDistribution\Download" }
    @{ Risk="S1";   Name="Windows 预读取 Prefetch";                 Path="C:\Windows\Prefetch" }
    @{ Risk="S1";   Name="系统小内存转储 Minidump";                 Path="C:\Windows\Minidump" }
    @{ Risk="S1";   Name="缩略图缓存";                              Path=Join-Path $userProfile "AppData\Local\Microsoft\Windows\Explorer" }
    @{ Risk="S1";   Name="Edge 浏览器缓存";                         Path=Join-Path $userProfile "AppData\Local\Microsoft\Edge\User Data\Default\Cache" }
    @{ Risk="S1";   Name="Edge Code Cache";                         Path=Join-Path $userProfile "AppData\Local\Microsoft\Edge\User Data\Default\Code Cache" }
    @{ Risk="S1";   Name="Chrome 缓存";                            Path=Join-Path $userProfile "AppData\Local\Google\Chrome\User Data\Default\Cache" }
    @{ Risk="S1";   Name="Chrome Code Cache";                      Path=Join-Path $userProfile "AppData\Local\Google\Chrome\User Data\Default\Code Cache" }
    @{ Risk="S1";   Name="Firefox 缓存 Profiles";                  Path=Join-Path $userProfile "AppData\Local\Mozilla\Firefox\Profiles" }
    @{ Risk="S1";   Name="pip 缓存";                                Path=Join-Path $userProfile "AppData\Local\pip\cache" }
    @{ Risk="S1";   Name="npm 缓存";                                Path=Join-Path $userProfile "AppData\Local\npm-cache" }
    @{ Risk="S1";   Name="NuGet 缓存";                              Path=Join-Path $userProfile "AppData\Local\NuGet\Cache" }
    @{ Risk="S1";   Name="conda 缓存";                              Path=Join-Path $userProfile ".conda\pkgs" }
    @{ Risk="S1";   Name="用户崩溃转储 CrashDumps";                 Path=Join-Path $userProfile "AppData\Local\CrashDumps" }
    @{ Risk="S1";   Name="DirectX Shader Cache";                    Path=Join-Path $userProfile "AppData\Local\D3DSCache" }
    @{ Risk="S2";   Name="下载文件夹 Downloads";                    Path=Join-Path $userProfile "Downloads" }
    @{ Risk="S2";   Name="桌面 Desktop";                            Path=Join-Path $userProfile "Desktop" }
    @{ Risk="S2";   Name="视频 Videos";                             Path=Join-Path $userProfile "Videos" }
    @{ Risk="S2";   Name="图片 Pictures";                           Path=Join-Path $userProfile "Pictures" }
    @{ Risk="S2";   Name="音乐 Music";                              Path=Join-Path $userProfile "Music" }
)

function Format-Size([long]$Bytes) {
    if ($Bytes -lt 0) { return "N/A" }
    if ($Bytes -ge 1GB) { return "{0:N2} GB" -f ($Bytes / 1GB) }
    if ($Bytes -ge 1MB) { return "{0:N2} MB" -f ($Bytes / 1MB) }
    if ($Bytes -ge 1KB) { return "{0:N2} KB" -f ($Bytes / 1KB) }
    return "$Bytes B"
}

function Get-FolderSizeFast {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        return [PSCustomObject]@{ Size = -1; Status = "Not Found" }
    }
    try {
        $totalSize = 0L
        $errorCount = 0
        $stack = New-Object System.Collections.Generic.Stack[string]
        $resolved = (Resolve-Path -LiteralPath $Path).Path
        $stack.Push($resolved)
        while ($stack.Count -gt 0) {
            $current = $stack.Pop()
            try {
                $di = New-Object System.IO.DirectoryInfo($current)
                foreach ($file in $di.EnumerateFiles()) {
                    try { $totalSize += $file.Length } catch { $errorCount++ }
                }
                foreach ($subDir in $di.EnumerateDirectories()) {
                    $stack.Push($subDir.FullName)
                }
            } catch {
                $errorCount++
            }
        }
        $status = if ($errorCount -gt 0) { "OK ($errorCount 个访问失败)" } else { "OK" }
        return [PSCustomObject]@{ Size = $totalSize; Status = $status }
    } catch {
        return [PSCustomObject]@{ Size = -2; Status = "Error: $($_.Exception.Message)" }
    }
}

$diskInfo = Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Name -eq 'C' } | Select-Object Name, @{N='UsedGB';E={[math]::Round($_.Used/1GB,2)}}, @{N='FreeGB';E={[math]::Round($_.Free/1GB,2)}}, @{N='TotalGB';E={[math]::Round(($_.Used+$_.Free)/1GB,2)}}

Write-Host "=== C 盘整体使用 ===" -ForegroundColor Yellow
if ($diskInfo) {
    Write-Host ("总: {0} GB | 已用: {1} GB | 剩余: {2} GB" -f $diskInfo.TotalGB, $diskInfo.UsedGB, $diskInfo.FreeGB) -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== 开始扫描杂物路径 ===" -ForegroundColor Yellow

$results = @()
$i = 0
foreach ($t in $targets) {
    $i++
    Write-Host ("[{0}/{1}] {2}" -f $i, $targets.Count, $t.Path) -ForegroundColor Cyan
    $sizeInfo = Get-FolderSizeFast -Path $t.Path
    $results += [PSCustomObject]@{
        Risk = $t.Risk
        Name = $t.Name
        Path = $t.Path
        Size = $sizeInfo.Size
        Status = $sizeInfo.Status
    }
}

$results = $results | Sort-Object Size -Descending

$md = New-Object System.Collections.Generic.List[string]
$md.Add("# C 盘杂物扫描报告")
$md.Add("")
$md.Add("**生成时间**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")
$md.Add("**机器名**: $computerName")
$md.Add("**用户**: $env:USERNAME")
$md.Add("")
if ($diskInfo) {
    $md.Add("**C 盘使用**: 总 $($diskInfo.TotalGB) GB / 已用 $($diskInfo.UsedGB) GB / 剩余 $($diskInfo.FreeGB) GB")
    $md.Add("")
}
$md.Add("## 图例")
$md.Add("")
$md.Add("- S1 Safe: 临时文件 / 缓存 / 回收站 / 程序缓存 - 可以放心清")
$md.Add("- S2 Review: 用户数据 - 需要你逐个看,别批量删")
$md.Add("")
$md.Add("## 扫描结果 (按大小降序)")
$md.Add("")
$md.Add("| 风险 | 类别 | 路径 | 大小 | 状态 |")
$md.Add("|------|------|------|------|------|")

foreach ($r in $results) {
    $riskLabel = if ($r.Risk -eq "S1") { "S1 Safe" } else { "S2 Review" }
    $md.Add("| $riskLabel | $($r.Name) | ``$($r.Path)`` | $(Format-Size $r.Size) | $($r.Status) |")
}

$md.Add("")
$totalSafe = ($results | Where-Object { $_.Risk -eq "S1" -and $_.Size -gt 0 } | Measure-Object -Property Size -Sum).Sum
$totalReview = ($results | Where-Object { $_.Risk -eq "S2" -and $_.Size -gt 0 } | Measure-Object -Property Size -Sum).Sum
$md.Add("## 汇总")
$md.Add("")
$md.Add("- **S1 可安全清理总计**: $(Format-Size $totalSafe)")
$md.Add("- **S2 用户数据总计**: $(Format-Size $totalReview)")
$md.Add("")
$md.Add("## 建议下一步")
$md.Add("")
$md.Add("1. 先清 S1 区域里占用最大的几项 (通常是 Temp / 回收站 / SoftwareDistribution / 浏览器缓存)")
$md.Add("2. 清完回收站之后重启一次, 让 Windows Update 重新检测")
$md.Add("3. S2 区域只清你确定不再需要的旧下载 / 旧安装包")
$md.Add("4. 如果空间还不够, 再扫用户目录下 > 500MB 的大文件")

$md | Out-File -FilePath $reportPath -Encoding UTF8

Write-Host ""
Write-Host "=== 报告已生成: $reportPath ===" -ForegroundColor Green
Write-Host ""
Write-Host "=== 汇总 ===" -ForegroundColor Yellow
Write-Host ("S1 可安全清理: " + (Format-Size $totalSafe)) -ForegroundColor Green
Write-Host ("S2 用户数据:   " + (Format-Size $totalReview)) -ForegroundColor DarkYellow
Write-Host ""
Write-Host "Top 8 最大项:" -ForegroundColor Yellow
$top8 = $results | Select-Object -First 8
foreach ($r in $top8) {
    $riskLabel = if ($r.Risk -eq "S1") { "[Safe]  " } else { "[Review]" }
    Write-Host ("  {0} {1,-10} {2}" -f $riskLabel, (Format-Size $r.Size), $r.Name)
}
