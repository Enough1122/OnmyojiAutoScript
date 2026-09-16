$keys = @('HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*',
         'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*',
         'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*')
foreach ($k in $keys) {
  Get-ItemProperty $k -ErrorAction SilentlyContinue |
    Where-Object { $_.DisplayName -like '*Doubao*' -or $_.DisplayName -like '*豆包*' } |
    ForEach-Object { '{0} || {1} || {2}' -f $_.DisplayName, $_.DisplayVersion, $_.UninstallString }
}
'---PROC---'
Get-Process | Where-Object { $_.ProcessName -like '*Doubao*' -or $_.ProcessName -like '*doubao*' } |
  ForEach-Object { '{0} (pid {1})' -f $_.ProcessName, $_.Id }
'---WINGET---'
& "$env:LOCALAPPDATA\Microsoft\WindowsApps\winget.exe" list --name Doubao 2>&1 | Select-Object -First 8
'FIND-DONE'
