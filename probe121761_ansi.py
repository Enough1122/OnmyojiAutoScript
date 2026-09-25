from tools.approval_detection import _iter_shell_command_starts, detect_hardline_command
from tools.self_repo_guard import detect_self_repo_git_mutation
from pathlib import Path
import tempfile

root=Path(tempfile.mkdtemp())/'repo'; root.mkdir()
for s in ["echo $'\\'x\\'' ; git checkout main", "echo $'\\'x\\'\\'' ; git checkout main", "echo $'\\''' ; git checkout main"]:
 print(repr(s), detect_hardline_command(s), list(_iter_shell_command_starts(s)), detect_self_repo_git_mutation(s, str(root), root))
