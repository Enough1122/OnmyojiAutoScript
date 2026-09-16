$roots = @('C:/Users/admin/AppData/Local','C:/Users/admin/AppData/Roaming','C:/Program Files (x86)')
$rows = @()
foreach ($root in $roots) {
  foreach ($d in (Get-ChildItem -LiteralPath $root -Directory -Force -ErrorAction SilentlyContinue)) {
    try {
      $s = (Get-ChildItem -LiteralPath $d.FullName -Recurse -Force -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum
      if ($s -gt 200MB) { $rows += [pscustomobject]@{ Path=$d.FullName; GB=[math]::Round($s/1GB,2) } }
    } catch {}
  }
}
foreach ($d in (Get-ChildItem -LiteralPath 'C:/Users/admin' -Directory -Force -ErrorAction SilentlyContinue | Where-Object { $_.Name -ne 'AppData' })) {
  try {
    $s = (Get-ChildItem -LiteralPath $d.FullName -Recurse -Force -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum
    if ($s -gt 200MB) { $rows += [pscustomobject]@{ Path=$d.FullName; GB=[math]::Round($s/1GB,2) } }
  } catch {}
}
$rows | Sort-Object GB -Descending | ForEach-Object { '{0}|{1} GB' -f $_.Path, $_.GB }
'SCAN2-DONE'
