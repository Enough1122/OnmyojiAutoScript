"""Isolate WHY os.execvpe returns 0xC0000005 on this host.

Matrix over the variables that differ between the probe payload and the PR's
real spawn payload:
  A. execvpe with a real script FILE as argv[1] (closest to the PR: argv[1] is
     an absolute path to a .py, no -c payload)
  B. execvpe with `-c` + an embedded-quote payload
  C. execvpe with a real script file, MINIMAL env (not os.environ)
  D. execvpe with a real script file, os.environ
  E. subprocess (no exec) with a real script file, os.environ  -> control
"""
import os
import subprocess
import sys
import tempfile

tmp = tempfile.mkdtemp()
marker = os.path.join(tmp, "ran.txt")
child = os.path.join(tmp, "child.py")
with open(child, "w") as fh:
    fh.write("import pathlib,sys\npathlib.Path(sys.argv[1]).write_text('ran')\n")


def run(label, argv, env=None):
    if os.path.exists(marker):
        os.remove(marker)
    try:
        rc = subprocess.Popen(argv, env=env).wait(timeout=15)
    except subprocess.TimeoutExpired:
        rc = "TIMEOUT"
    print(f"{label:38s} rc={rc!s:12s} marker={os.path.exists(marker)}")


wrapper = "import os,sys;os.execvpe(sys.argv[1], sys.argv[1:], os.environ)"

run("A execvpe + real .py file",
    [sys.executable, "-c", wrapper, sys.executable, child, marker])
run("B execvpe + -c embedded-quote payload",
    [sys.executable, "-c", wrapper, sys.executable, "-c",
     "import pathlib,sys;pathlib.Path(sys.argv[1]).write_text('ran')", marker])
run("C execvpe + real .py file, minimal env",
    [sys.executable, "-c", wrapper, sys.executable, child, marker],
    env={"PATH": os.environ.get("PATH", ""), "SystemRoot": os.environ.get("SystemRoot", "")})
run("D execvpe + real .py file, os.environ",
    [sys.executable, "-c", wrapper, sys.executable, child, marker],
    env=os.environ.copy())
run("E CONTROL subprocess + real .py file",
    [sys.executable, child, marker], env=os.environ.copy())
