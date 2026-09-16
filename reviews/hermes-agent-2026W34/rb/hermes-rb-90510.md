> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Thoroughly done: all four native-child log reads now state \`-Encoding UTF8\`, the reasoning lives as a comment at the redirect site where the BOM-less bytes are created, and the test module is unusually good — measured PS 5.1 behavior on ja-JP recorded in the docstring, an explicit out-of-scope statement for \`Tee-Object\`'s BOM'd UTF-16LE logs so nobody "finishes the job" into a misdecode, and a premise pin that \`[Console]::OutputEncoding\` remains display-only.

Nit: the regression test matches four specific \`Get-Content\` shapes by regex, so a future read written in a different parameter order (\`Get-Content -Raw -Path $logPath\`) slips through uncovered. A stronger and simpler invariant: assert *every* \`Get-Content\` line in install.ps1 contains \`-Encoding\`, with a tiny named allowlist for the Tee-Object-fed reads — that fails loudly on any new unannotated read regardless of argument order.

No blocking issues found.