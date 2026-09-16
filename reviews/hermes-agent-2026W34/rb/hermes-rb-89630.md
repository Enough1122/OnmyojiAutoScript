> AI code review — automated review for reference; please use your judgment.

Review of "feat(vision): preserve user tasks across image analysis paths". This fixes a real quality/security pair of problems: auxiliary vision previously ran a generic "describe everything" prompt regardless of what the user asked, and the fallback cache keyed ONLY on image URL — so the same image analyzed for two different intents returned the wrong cached description. The new module unifies all three surfaces, bounds intent with head/tail-preserving truncation (tasks often trail long context), wraps the task in escaped `<user_task>` tags, and adds an explicit untrusted-image-content injection-defense clause. Suggestions:

1. gateway/run.py:24327 (magic placeholder string) — `user_text.strip() == "(The user sent a message with no text content)"` couples this module to an upstream literal; if the producer rewords it, the placeholder itself becomes the "vision task" — export that constant from wherever it's defined and compare against it.

2. agent/vision_prompt.py:build_vision_prompt (nit, entity fidelity) — `escape(..., quote=True)` converts &, ", ' into entities, so code/text quoted verbatim inside a task renders as `&amp;`/`&quot;` to the vision model — acceptable for defense against tag breakout, but escaping only `<`/`>` (the characters that matter for the fence) would preserve task-text fidelity while keeping the containment property.

3. coverage suggestion — add one test asserting two DIFFERENT intents over the SAME image produce distinct fallback cache entries (the regression this PR fixes), since the cache-key change is easy to undo invisibly.
