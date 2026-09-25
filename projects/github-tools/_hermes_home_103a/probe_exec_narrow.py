"""Narrow the 0xC0000005: is it os.execvpe specifically, or all exec* on this host?

This decides A (PR picks a broken-on-Windows API => publishable) vs
B (host CPython is broken => environment, stay silent).
"""
import os
import subprocess
import sys
import tempfile

tmp = tempfile.mkdtemp()
child = os.path.join(tmp, "child.py")
with open(child, "w") as fh:
    fh.write("import pathlib,sys\npathlib.Path(sys.argv[1]).write_text('ran')\n")


def run(label, wrapper):
    marker = os.path.join(tmp, "ran.txt")
    if os.path.exists(marker):
        os.remove(marker)
    try:
        rc = subprocess.Popen(
            [sys.executable, "-c", wrapper, sys.executable, child, marker]
        ).wait(timeout=15)
    except subprocess.TimeoutExpired:
        rc = "TIMEOUT"
    print(f"{label:34s} rc={rc!s:12s} child_ran={os.path.exists(marker)}")


run("os.execv(file, argv)", "import os,sys;os.execv(sys.argv[1], sys.argv[1:])")
run("os.execve(file, argv, env)", "import os,sys;os.execve(sys.argv[1], sys.argv[1:], os.environ)")
run("os.execvp(file, argv)", "import os,sys;os.execvp(sys.argv[1], sys.argv[1:])")
run("os.execvpe(file, argv, env)", "import os,sys;os.execvpe(sys.argv[1], sys.argv[1:], os.environ)")

print()
print("python:", sys.version)
print("platform:", sys.platform)
print("os.execvpe exists:", hasattr(os, "execvpe"))
