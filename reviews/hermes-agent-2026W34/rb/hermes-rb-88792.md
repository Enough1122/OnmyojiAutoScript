> AI code review - automated review for reference; please use your judgment.

Reviewed the diff. Correct fix with the right regex discipline: anchoring the version suffix to end-of-string (`fullmatch(r"(.+?)(v\d+)?")`) splits old-style archive ids like solv-int/9701001v1 at the actual version instead of the first 'v' in the archive name, and links now print the full versioned id so abs/pdf URLs stay resolvable. The new test module covers modern versioned/unversioned, the v-in-archive regression, and a no-v archive - exactly the matrix this parser needs. Nice touch loading the script by file path so the skill stays standalone.

Nit: an id ending in a bare "v" ("2402.03300v") parses as base-with-trailing-v rather than a malformed version - fine since arXiv never emits that, but the helper docstring could say malformed suffixes ride along untouched.

No blocking issues found.