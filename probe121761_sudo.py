from tools.terminal_tool_sudo import _scan_shell, _count_real_sudo_invocations, _rewrite_real_sudo_invocations
cases = [
    'echo $(true)#x; sudo apt-get update',
    'echo a$(true)#x; sudo apt-get update',
    'echo hi\r#x; sudo apt-get update',
    'echo hi\xa0#x; sudo apt-get update',
    'echo hi;#x; sudo apt-get update',
    'echo hi #x; sudo apt-get update',
    'echo hi # sudo apt-get update',
    "echo 'hi #x; sudo apt-get update'",
]
for s in cases:
    print(repr(s))
    print(list(_scan_shell(s)))
    print('count', _count_real_sudo_invocations(s))
    print('rewrite', _rewrite_real_sudo_invocations(s))
