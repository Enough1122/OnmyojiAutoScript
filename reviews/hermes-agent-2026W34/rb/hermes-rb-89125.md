> AI code review — automated review for reference; please use your judgment.

Clean and complete for its scope: the singular alias rides argparse's native `aliases`, dispatch goes through `func` so nothing else needs to change (verified no code path compares `args.command == "plugins"`), and the new test asserts both spellings parse to identical actions *and* bind the same handler — which is the assertion that actually matters for an alias, since a mismatched `func` would be the realistic failure mode.

No blocking issues found.

Nit: if the docs' CLI reference enumerates the plugins subcommand spelling anywhere (website/docs tools-reference / CLI page), add the singular there too so users who guess `hermes plugin list` from documentation don't discover it only by trial; likewise the shell-completion definitions, if any exist, will need the alias added to stay consistent.

— Reviewed by Hermes AI reviewer (reviewer-f2)
