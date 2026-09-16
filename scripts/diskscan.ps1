$tops = @('C:/Windows','C:/Program Files','C:/Program Files (x86)','C:/ProgramData','C:/Python314','C:/Intel')
foreach ($p in $tops) {
  try {
    $s = (Get-ChildItem -LiteralPath $p -Recurse -Force -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum
    '{0}|{1:N2} GB' -f $p, ($s/1GB)
  } catch { "$p|ERR" }
}
'SCAN-DONE'
