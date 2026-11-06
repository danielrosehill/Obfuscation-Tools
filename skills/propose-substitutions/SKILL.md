---
name: propose-substitutions
description: "Preview an obfuscation plan as a table of identifiers and proposed replacements for approval, then apply it across documents."
---

# Propose substitutions

Two phases: **propose** first, **apply** only after approval. This guards against replacements too close to the originals, and against scrubbing detail the user wanted kept. It works for documents and for technical material.

## Phase 1: Propose

1. Read the source and settle the proximity level from `references/proximity-levels.md`.
2. Find the identifying details, using the categories in `obfuscate-document` or `obfuscate-bug-report`.
3. Produce the table:

   | # | Type | Original | Proposed replacement | Rationale |
   |---|------|----------|----------------------|-----------|
   | 1 | person | Anna Karpov | Sara Mitchell | moderate: unrelated common name, same gender |
   | 2 | org | Acme Pharma EMEA | Bridgewell Therapeutics | moderate: invented peer in the same sector |
   | 3 | date | 14 March 2024 | 23 May 2024 | shifted +70 days, weekday preserved |
   | 4 | ha-entity | light.marlowe_nursery_ceiling | light.guest_bedroom_ceiling | keeps domain and device; room and name changed |

4. Flag entries that could go either way, such as a regulator or a public incident the user may want kept.
5. **Stop.** Ask the user to approve the table, edit rows, or add and remove entries.

## Phase 2: Apply

Save the approved table as the case map, then continue from the apply step of `obfuscate-document` or `obfuscate-bug-report` with the locked map. Don't invent replacements during apply. Anything new that turns up goes back to the user.

## When to use this

- The user has preferred pseudonyms.
- The document is high-stakes and needs an explicit review step.
- Several documents share entities, because consistency across them is what keeps a coordinated disclosure credible.

## Data storage

Approved maps go in `${CLAUDE_USER_DATA:-${XDG_DATA_HOME:-$HOME/.local/share}/claude-plugins}/obfuscation-tools/maps/<case-id>.json`:

```json
{
  "case": "<case-id>",
  "level": "moderate",
  "entries": [{"original": "...", "replacement": "...", "type": "person"}]
}
```

Never store a map in a repo or beside the output.
