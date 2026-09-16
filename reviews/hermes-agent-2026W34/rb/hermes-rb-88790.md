> AI code review - automated review for reference; please use your judgment.

Reviewed the diff. Important hardening: the old `content[:MAX_SCAN_CHARS]` truncation meant anything past the cap reached the model completely unscanned - precisely where an injected payload in a large context file would hide. Head+tail chunking with finding dedup bounds runtime at 2x the cap while covering both realistic injection placements, and the tests are thorough: past-cap detection, head-preservation, large-benign false-positive control, cross-chunk dedup counting, and invisible-unicode in the tail.

- Known bound worth stating in the docstring: content strictly BETWEEN the head window and the tail window (a >2x-cap file with the payload buried mid-body) remains unscanned. The current design is the right bounded trade - just name it so nobody assumes full coverage.

- Nit: the PR carries an unrelated contributors/emails identity file; splitting it out keeps this security diff attributable cleanly.