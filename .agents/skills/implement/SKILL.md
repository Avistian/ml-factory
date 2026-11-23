---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

Implement the work described by the user in the spec or tickets.

If the user passes a ticket reference, fetch it from the issue tracker and state its title before starting. If the reference is ambiguous, ask.

## Implementation preflight

Before changing implementation files:

1. Inspect the branch, worktree and remote. Read the ticket's **Approved specification** link when present; otherwise use the ticket and locally accepted specification. Follow the latest user-approved scope and preserve accepted design and glossary edits already present locally.
2. Fetch the target base (normally `origin/main`) and record its SHA. Reconcile the working branch with that fetched base before implementation. Preserve uncommitted work in an explicit checkpoint or isolated checkout; resolve routine conflicts without discarding accepted decisions or unrelated edits. Prefer merging on an already published branch to avoid rewriting others' history. If fetching is unavailable, report that the base is unverified instead of claiming it is current.
3. Read the refreshed repository instructions and check targets. Run its existing checkout/environment preflight and tracked-file guard when available. For r0, use `make preflight tracked-files`; when deliberately reusing an environment, select this checkout with `PYTHONPATH=src`. Confirm the reported interpreter and source path belong to the intended environment and checkout.

Preflight is complete when the recorded base is an ancestor of the working branch, accepted design edits are preserved, and the available repository guards pass. Reuse those guards rather than create a second validation system.

Call the Skill tool with "tdd" where possible, at pre-agreed seams.

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Once done, call the Skill tool with "code-review" to review the work.

Commit your work to the current branch.
