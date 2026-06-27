---
description: Record the result of an APEX import test for a generated SQL change
argument-hint: "test id or generated SQL path"
---

Create or update an import test result in `apex-test-results/` after the developer tries importing generated SQL in APEX App Builder.

Developer input: `$ARGUMENTS`

Agent steps:
1. Identify the generated SQL path and/or test ID from the developer's message.
2. Identify the related patch manifest and patch spec when possible.
3. Create a Markdown file such as:
   ```text
   apex-test-results/TEST-001-region-title.md
   ```
4. Use the template in `apex-test-results/README.md` when available; otherwise capture:
   - Test ID/name.
   - Source export path.
   - Patch spec path.
   - Generated SQL path.
   - Expected result.
   - Actual result.
   - Pass/fail.
   - Screenshots or evidence links.
   - Import settings used.
   - Notes and required process/tool changes.
5. If the test failed, do not proceed to a more advanced patch capability until the failure is fixed and retested.
6. If the test passed, note which patch operation is validated by the result.
