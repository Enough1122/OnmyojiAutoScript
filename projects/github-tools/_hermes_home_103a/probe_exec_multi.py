"""Run the exec* matrix under whatever interpreter is passed as argv[1].

Usage: <python> probe_exec_multi.py
Prints the interpreter and the rc for each exec* variant so we can tell a
broken host build apart from a Windows-wide limitation.
"""
import os
import subprocess
import sys
import tempfile

tmp = tempfile.mkdtemp()
child = os.path.join(tmp, "child.py")
with open(child, "w") as fh:
    fh.write("import pathlib,sys\npathlib.Path(sys.argv[1]).write_text('ran')\n")

print("interpreter:", sys.executable, sys.version.split()[0], sys.platform)
for label, wrapper in (
    ("execv ", "import os,sys;os.execv(sys.argv[1], sys.argv[1:])"),
    ("execvp", "import os,sys;os.execvp(sys.argv[1], sys.argv[1:])"),
    ("execve", "import os,sys;os.execve(sys.argv[1], sys.argv[1:], os.environ)"),
    ("execvpe", "import os,sys;os.execvpe(sys.argv[1], sys.argv[1:], os.environ)"),
):
    marker = os.path.join(tmp, "ran.txt")
    if os.path.exists(marker):
        os.remove(marker)
    try:
        rc = subprocess.Popen([sys.executable, "-c", wrapper, sys.executable, child, marker]).wait(timeout=15)
    except subprocess.TimeoutExpired:
        rc = "TIMEOUT"
    print(f"  {label} rc={rc!s:12s} child_ran={os.path.exists(marker)}")
