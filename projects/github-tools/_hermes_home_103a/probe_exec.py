"""Host probe: is os.execvpe broken on this host independently of the PR?"""
import os
import subprocess
import sys
import tempfile

marker = os.path.join(tempfile.gettempdir(), "execvpe_marker_probe.txt")
if os.path.exists(marker):
    os.remove(marker)
code = "import pathlib,sys;pathlib.Path(sys.argv[1]).write_text('ran')"

p = subprocess.Popen([sys.executable, "-c", code, marker])
rc = p.wait(timeout=10)
print("baseline: plain subprocess spawn of the same payload rc =", rc,
      "marker:", os.path.exists(marker))
if os.path.exists(marker):
    os.remove(marker)

p = subprocess.Popen([sys.executable, "-c",
                      "import os,sys;os.execvpe(sys.argv[1], sys.argv[1:], os.environ)",
                      sys.executable, "-c", code, marker])
rc = p.wait(timeout=10)
print("PR path: os.execvpe rc =", rc, "marker:", os.path.exists(marker))
