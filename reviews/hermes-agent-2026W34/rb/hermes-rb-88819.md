> AI code review — automated review for reference; please use your judgment.

Correct and well-proven: `urlopen` follows redirects with the Authorization header attached, so a compromised/MITM'd peer could harvest the Bearer key via one 302; routing through `open_credentialed_url` closes it, and the test is the gold standard — two *real* HTTP servers, a successful redirect to an attacker origin, and an assertion that the key never arrived.

— reviewer-b (automated review)

No blocking issues found.
