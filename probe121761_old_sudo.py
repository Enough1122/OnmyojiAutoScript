import importlib.util
from pathlib import Path

path = Path('D:/Hermes/pr121761-base-sudo.py')
spec = importlib.util.spec_from_file_location('old_sudo', path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

cases = [
    'echo $(true)#x; sudo apt-get update',
    'echo a$(true)#x; sudo apt-get update',
    'echo hi\r#x; sudo apt-get update',
    'echo hi\xa0#x; sudo apt-get update',
    'echo hi;#x; sudo apt-get update',
    'echo hi #x; sudo apt-get update',
]
for s in cases:
    print(repr(s))
    print(list(m._scan_shell(s)))
    print('count', m._count_real_sudo_invocations(s))
