> AI code review — automated review for reference; please use your judgment.

Good observability gap closed: `status` now distinguishes "API key present" from "provider actually runnable", which is exactly the mismatch (#90610) where every voice reply silently degraded to text while the ElevenLabs key row showed ✓. Scoping the check to explicitly-configured providers (free Edge default excluded) is the right call and is tested in both directions, and the ElevenLabs install hint now reflects the uv-managed venv instead of recommending a pip that isn't there.

1. `hermes_cli/status.py:~231–235` — the message asserts **"SDK missing"** as the reason, but it prints whenever `check_tts_requirements()` returns falsy for any reason; if that checker also fails on other prerequisites (a missing `ffmpeg` for some providers, an unset model default), the status line points users at the wrong fix — why it matters: a wrong remediation string converts a helpful diagnostic into a misdiagnostic — suggestion: have `check_tts_requirements()` expose its reason (or return a tuple) and render that, or soften the wording to "`<provider>` not runnable — check that its SDK/prerequisites are installed".

2. Nit (`:~240–241`): the outer `except Exception: pass) keeps the report alive (correct) but a `logger.debug(..., exc_info=True)` would keep future probe bugs diagnosable instead of silently disappearing.

— reviewer-a · automated agent review (Hermes week-review)
