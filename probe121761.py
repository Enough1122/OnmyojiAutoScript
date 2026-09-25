from tools.approval_detection import _scan_shell, _iter_shell_command_starts, detect_hardline_command
from tools.terminal_tool_sudo import _scan_shell as sudo_scan, _count_real_sudo_invocations, _rewrite_compound_background
from tools.shell_heredoc import strip_inert_heredoc_bodies
cases = [
    r"echo $'\\'x\\'' ; reboot",
    r"echo $'\\'x\\'\\'' ; reboot",
    r"echo $'abc' ; reboot",
    r"echo $'abc\\' ; reboot",
    r"echo $'abc\\'x' ; reboot",
    r"echo $'abc\\\\' ; reboot",
    r"echo $'abc\\'; reboot",
    r"echo $'abc\\' #; reboot",
    r"echo $'abc\\' #x; reboot",
    r"echo $'\\' ; reboot",
    r"echo $'\\'' ; reboot",
    r"echo $'\\''' ; reboot",
]
for s in cases:
    print('CASE', repr(s))
    print(' approval scan', list(_scan_shell(s, comments=True)))
    print(' starts', list(_iter_shell_command_starts(s)))
    print(' hardline', detect_hardline_command(s))
print('HEREDOC')
for s in [r"echo ok\r#x <<'EOF'\nreboot\nEOF", r"echo ok\r#x <<'EOF'\nreboot\nEOF; echo tail", r"echo ok\r#x <<'EOF'\nreboot\nEOF\n tail"]:
    print(repr(s), '=>', repr(strip_inert_heredoc_bodies(s)))
print('SUDO SCAN')
for s in [r"echo ok\r#x; sudo reboot", r"echo ok\r#x\r sudo reboot", r"echo ok\r#x; echo x & sudo reboot", r"echo ok\r#x; echo x && sudo reboot &"]:
    print(repr(s), list(sudo_scan(s)), _count_real_sudo_invocations(s), _rewrite_compound_background(s))
