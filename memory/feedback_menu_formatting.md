---
name: Hugo menu sub-item formatting
description: What works and what doesn't for visually indenting child menu items in the Stack theme sidebar
type: feedback
---

Use `".\u00a0\u00a0\u00a0\u00a0Name"` for child menu items — dot first, then 4 non-breaking spaces (U+00A0), then the name.

**Why:** The Stack theme has no native dropdown/nested menu support. Visual indentation is the only option. Regular spaces collapse in HTML rendering, so they don't produce visible indent. Non-breaking spaces (`\u00a0`) do render. The dot acts as a subtle visual marker that also anchors the indent.

**How to apply:**
- In `config.toml` menu entries, write the name as `".\u00a0\u00a0\u00a0\u00a0Name"` — use actual U+00A0 characters or JSON `\u00a0` escapes
- Do NOT use regular spaces — they will collapse
- Do NOT use `↳` or `•` — user found them "too busy"
- Child items sit immediately below their parent section in the flat menu list, ordered by `weight`
