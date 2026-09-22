$found = Get-Process | Where-Object { $_.MainWindowTitle -like 'OAS-Server*' }
if (-not $found) {
  Write-Output 'NOT_FOUND'
  exit 0
}
Add-Type -Name Win32Util -Namespace Win32 -MemberDefinition @'
[DllImport("user32.dll")]
public static extern bool ShowWindow(System.IntPtr hWnd, int nCmdShow);
'@
foreach ($p in $found) {
  [Win32.Win32Util]::ShowWindow($p.MainWindowHandle, 6) | Out-Null
  Write-Output ("MINIMIZED pid=" + $p.Id + " title=" + $p.MainWindowTitle)
}
