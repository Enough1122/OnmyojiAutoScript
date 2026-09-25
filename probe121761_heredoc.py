from tools.shell_heredoc import strip_inert_heredoc_bodies
cases = [
    "echo $(true)#x <<'EOF'\nreboot\nEOF",
    "echo $(true)#x <<'EOF'\nreboot\nEOF; echo tail",
    "echo $(true)#x <<'EOF'\nreboot\nEOF\n tail",
    "echo $(true)#x <<'EOF'\nreboot\nEOF\nrm -rf /",
    "echo hi #x <<'EOF'\nreboot\nEOF",
    "echo hi;#x <<'EOF'\nreboot\nEOF",
]
for s in cases:
    print('CASE', repr(s))
    print('=>', repr(strip_inert_heredoc_bodies(s)))
