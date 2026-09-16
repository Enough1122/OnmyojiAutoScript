> AI code review — automated review for reference; please use your judgment.

Right fix, minimal blast radius: `data: null` frames carry no payload, so dropping the deserialized `None` at the single chokepoint every consumer iterates is strictly better than letting an AttributeError kill an otherwise-valid turn. The end-to-end test (through `_interruptible_streaming_api_call`, not just the iterator) proves the turn completes with correct content and finish reason. Points:

1. Scope check: auxiliary/streaming callers that iterate provider streams *outside* `_iter_provider_stream_chunks` (e.g. `call_llm` streaming paths in auxiliary_client) would still crash on a None frame from the same relay class. Worth grepping for other raw `for chunk in stream` sites or funneling them through this helper. (nit)
2. A debug log on drop ("relay sent null SSE frame") would make relay misbehavior visible instead of silently absorbed — cheap and useful when debugging why a vendor's output looks truncated. (nit)
3. Should consecutive-None counts ever matter (relay stuck emitting nulls forever = infinite loop)? The SDK stream terminates server-side eventually; no action needed, just noting the theoretical unbounded-absorb case. (nit)

No blocking issues found.
