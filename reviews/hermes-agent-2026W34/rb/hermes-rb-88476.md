> AI code review — automated review for reference; please use your judgment.

Brief supplement (a parallel automated pass reviewed this concurrently): one wording item before merge — the PR TITLE says "fails open," but that describes the OLD bug; the new code fails CLOSED (emits `<invalid-url>` rather than risking a credentialed string). Security reviewers skim titles, so rewording to "…fails closed on schemeless proxy URLs" would prevent misreading the direction of the change.
