Get-Process | Where-Object { $_.MainWindowTitle -ne '' } |
  Select-Object Name, Id, MainWindowTitle |
  Format-Table -AutoSize | Out-String -Width 200 | Write-Output
