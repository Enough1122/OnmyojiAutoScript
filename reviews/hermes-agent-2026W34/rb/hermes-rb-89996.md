> AI code review — automated review for reference; please use your judgment.

Right fix with the failure mode precisely characterized: copytree aborts the whole archive on the first special file, and profiles accumulate live Unix sockets in normal operation. Extracting `_non_exportable_entries` so both the default and named-profile paths share one ignore rule is the correct refactor, lstat catches suffix-less sockets/FIFOs/devices that name rules miss, vanished-mid-walk entries are handled, and the tests bind *real* AF_UNIX sockets plus a FIFO across both export paths (with the macOS `sun_path` workaround noted). One nit:

- hermes_cli/profiles.py:2013 — nit — symlinks survive the archive (`symlinks=True`); a link pointing at an absolute path outside the profile (e.g., to a credentials file elsewhere) will dangle or resolve unexpectedly on the importing machine — consider rewriting or dropping out-of-root absolute symlinks during staging.

No blocking issues found.

— reviewer-b (automated review)
