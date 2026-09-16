> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Right exemption, correctly framed as a consumer convention rather than a syntax question: Helm/Argo/flux template files are only valid YAML *after* rendering, and PyYAML trips on the delimiters themselves. Mirroring the existing CloudFormation/Ansible tag exemptions keeps the gate's philosophy consistent, and the paired tests are exactly right — the exact reported Helm content passes while a tab-mangled plain YAML is still hard-refused and never written.

Nit (non-blocking): tools/file_operations.py:_lint_yaml_inproc — the `"{{" in content and "}}" in content` scan is broader than its docstring claim ("cannot mask a real YAML error"): a file that mixes genuine Go-templates with an otherwise tab-mangled block map will now sail through the gate unlinted. If you want to narrow it without losing coverage, anchor on directive-shaped lines (`re.search(r"(?m)^\s*{{[-#]?", content)` catches Helm/Argo conventions specifically); otherwise soften the docstring to acknowledge the mixed-content tradeoff.
