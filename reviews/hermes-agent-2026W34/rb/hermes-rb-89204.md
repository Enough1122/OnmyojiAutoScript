> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Right-sized fix: YAML silently parses bare timestamps into `datetime` objects, so any config containing one made the TUI's `config.get full` RPC throw on serialization; the recursive `json_safe` walk covers dicts/lists/tuples and converts `date`/`time` (`datetime` included via subclassing) to ISO strings, and the regression test asserts both the transformed value *and* that the whole response round-trips through `json.dumps`.
