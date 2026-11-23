---
name: grill-with-docs
description: A relentless interview to sharpen a plan or design, which also creates docs (ADR's and glossary) as we go.
disable-model-invocation: true
---

Call the Skill tool twice, for "grilling" and "domain-modeling".

## Approved specification handoff

When the user confirms the completed design (including an instruction to implement it), keep the accepted scope in one specification document. If there is a ticket, add or update its **Approved specification** link once that document has a published revision. Prefer a commit-pinned repository URL; identify the document as the authoritative accepted scope without copying its decisions into the issue.

Verify that the linked revision contains the accepted decisions and that the issue body contains the link. Preserve the rest of the issue body. If the specification is still local, record the publication/link step as pending in the handoff; complete it when publishing the implementation PR. Do not publish a branch solely to manufacture a link without authorization.
