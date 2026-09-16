> AI code review — automated review for reference; please use your judgment.

Review of "fix(desktop): add WhatsApp QR pairing flow" (sampled: messaging view onboarding flow + tests). Well-covered UX lifecycle: start → poll status → render the backend QR payload LOCALLY as SVG (with the important "Scan with WhatsApp Linked Devices, not the camera app" warning), handle 410-expiry with polling stopped and a retry affordance, detect superseded pairings and clear them, apply an already-linked session with a backend refresh, and — a detail most implementations miss — CANCEL the pairing on its ORIGINAL profile when the active gateway profile changes mid-flow. Tests drive each state through the real view. Suggestions:

1. apps/desktop/src/app/messaging/index.tsx (QR staleness) — WhatsApp linked-device payloads rotate server-side; if the status poll succeeds repeatedly with the SAME qr_payload after expiry windows pass, the rendered QR may silently be dead while still displayed — consider surfacing an age indicator or re-requesting the payload when the status reports a new one.

2. nit — the QR <img> alt text is present (good), but consider also offering "Copy pairing code" for accessibility on audio-only setups.
