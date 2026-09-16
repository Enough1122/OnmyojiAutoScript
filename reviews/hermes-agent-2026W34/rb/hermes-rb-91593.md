> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Right call overall — dropping \`VOLUME\` unblocks Railway-style builders and the new warning documents the trade-off. Points:

- **Dockerfile:422 — removal silently changes persistence behavior for existing no-`-v` users.** With \`VOLUME [ "/opt/data" ]\`, Docker auto-created an anonymous volume whose contents survived \`docker rm\` until explicitly pruned; after this change those users' writes land in the container layer and vanish on replace/redeploy. The docs warning covers *new* readers, but existing deployments won't re-read docs. Suggestion: pair this with a CHANGELOG entry and an upgrade note ("if you ran without \`-v\`, copy data out before upgrading") so the migration path is discoverable.

- **website/docs/user-guide/docker.md:169-173 — surface the same warning where containers actually get launched.** This lives mid-page under a troubleshooting-adjacent section; the quickstart/`docker run` examples earlier in the same page (and the Compose example) are where the mount requirement matters most. A one-line pointer near the first run command would prevent the failure mode rather than explain it afterwards.

- **The Railway claim has no reference.** "Some hosted builders (including Railway) reject that instruction" — linking the builder error/issue in the docs comment (or commit message) would help maintainers judge when it's safe to reintroduce \`VOLUME\` later, e.g. behind a build arg for plain-Docker consumers who want the old guarantee back.

- **No guard against accidental regression.** Nothing fails if someone re-adds \`VOLUME\`; a trivial CI check (`docker inspect --format '{{json .Config.Volumes}}'` on a built image must be `null`) or a lint rule on the Dockerfile would pin the constraint this PR establishes.

Otherwise straightforward and well-scoped — the \`ENV PATH\`/entrypoint machinery around the removed line is untouched, which is correct here.
