$roots = @('C:/Windows','C:/ProgramData','C:/Program Files')
$rows = @()
foreach ($root in $roots) {
  foreach ($d in (Get-ChildItem -LiteralPath $root -Directory -Force -ErrorAction SilentlyContinue)) {
    try {
      $files = Get-ChildItem -LiteralPath $d.FullName -Recurse -Force -File -ErrorAction SilentlyContinue
      $s = ($files | Measure-Object Length -Sum).Sum
      $rows += [pscustomobject]@{ Path=$d.FullName; GB=[math]::Round($s/1GB,2); N=$files.Count }
    } catch {}
  }
}
$rows | Sort-Object GB -Descending | Select-Object -First 25 | ForEach-Object { '{0}|{1} GB|{2} files' -f $_.Path, $_.GB, $_.N }
'---RESTORE-POINTS---'
try { (Get-ComputerRestorePoint -ErrorAction Stop | Measure-Object).Count } catch { 'RP-QUERY-FAILED' }
'SCAN3-DONE'
