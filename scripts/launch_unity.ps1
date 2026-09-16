# Unity 直接启动器 (绕过 Hub 3.19 窗口后台 bug)
# 用法: 双击 launch_unity.bat 或 PowerShell 运行 launch_unity.ps1

$UnityExe = "D:\SoftWare\Unity\untiy2022.3.62.f2\Editor\Unity.exe"

if (-not (Test-Path $UnityExe)) {
    Write-Host "[ERROR] Unity.exe not found: $UnityExe" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# 别名映射
$aliases = @{
    "aa"   = "D:\AA\unity_asset_chat_trunk_original"
    "igc"  = "D:\AA\unity_asset_chat_trunk_original"
    "main" = "D:\AA\unity_asset_chat_trunk_original"
    "B"    = "D:\AA\unity_asset_B"
    "pss"  = "D:\AA\unity_asset_pss"
    "sk"   = "D:\AA\unity_asset_sk"
}

$input = $args[0]

if (-not $input) {
    Write-Host ""
    Write-Host "可用的项目简称:" -ForegroundColor Cyan
    Write-Host "  aa / igc / main  =  unity_asset_chat_trunk_original"
    Write-Host "  B                =  unity_asset_B"
    Write-Host "  pss              =  unity_asset_pss"
    Write-Host "  sk               =  unity_asset_sk"
    Write-Host ""
    $input = Read-Host "项目路径或简称"
}

# 查别名，否则当路径
if ($aliases.ContainsKey($input.ToLower())) {
    $project = $aliases[$input.ToLower()]
} else {
    $project = $input
}

# 验证
if (-not (Test-Path "$project\Assets")) {
    Write-Host "[ERROR] 项目路径无效: $project" -ForegroundColor Red
    Write-Host "请确认路径包含 Assets 目录"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host " 启动 Unity (绕过 Hub 3.19 bug)" -ForegroundColor Green
Write-Host " 项目: $project" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green

Start-Process -FilePath $UnityExe -ArgumentList "-projectpath `"$project`" -window-mode position -window-position 0,0 -screen-fullscreen 0"
