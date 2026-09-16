> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

A genuinely useful orchestration-layer skill: the shared-desk layout (inbox read-only / work / output), the verify-before-delivering rule, the explicit routing table including the LibreOffice/pandoc/tesseract enhancers with approval-gated installs, and the non-negotiables section are all the kind of concrete guardrails skills usually lack. The Arabic typography guidance is technically correct where most get it wrong — complex-script slots (`w:cs`/`a:cs`) are indeed what actually shapes Arabic, and `find_font_ttf`'s exact-family-over-lookalike sort handles the Cairo/CairoPlay trap. Findings:

1. scripts/arabic_style.py:style_docx — only *named styles* are retagged; any run carrying direct formatting (`rFonts` set at run level, which is exactly what most docx-generating code and Word-authored templates do) keeps its Latin font, so an Arabic deliverable can come out half-Cairo/half-Calibri despite the helper reporting success. The pptx branch already walks every run — mirror that here (iterate paragraphs/runs across body, tables, headers/footers and set the cs slot per-run), or at minimum document the style-level limitation in SKILL.md so agents verify rather than trust it.

2. scripts/arabic_style.py:style_pptx — grouped shapes are skipped: a group shape has no `text_frame`, so any text inside `GroupShape.shapes` (common in real decks) never gets the cs slot set. Recurse into `shape.shape_type == MSO_SHAPE_TYPE.GROUP → shape.shapes`. Same one-liner class of gap applies to notes slides if those matter for deliverables.

3. scripts/arabic_style.py:_DOCX_STYLES — Heading 4–6, Caption, Quote, Intense Quote, and table styles aren't covered; an H4-heavy report renders headings in the fallback font while its body is Cairo, which looks like a bug to the user even though the helper "worked". Either extend the tuple or iterate all paragraph styles whose names match known families.
