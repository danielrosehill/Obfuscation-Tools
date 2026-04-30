---
name: propose-substitutions
description: Use when the user wants to *preview* the anonymisation plan for a sensitive document before any text is rewritten — produce a table of detected identifiers and proposed replacements for review and approval, then apply only on confirmation. Use this instead of anonymise-document when the user wants control over the swaps (e.g. they have preferred pseudonyms, or want to verify nothing important is being scrubbed).
---

# Propose Substitutions

Two-phase anonymisation: **propose** first, **apply** only after the user approves. This addresses a real failure mode — the assistant picking replacements that are too close to the originals, or scrubbing detail that the user actually wanted preserved.

## Phase 1 — Propose

1. Read the source document (file path or pasted text).
2. Scan for identifying markers across the categories from `anonymise-document` (names, organisations, locations, dates, unique characteristics, etc.).
3. Produce a substitution table:

   | # | Type | Original | Proposed replacement | Rationale |
   |---|------|----------|----------------------|-----------|
   | 1 | person | Anna Karpov | Sara Mitchell | unrelated common name; preserves female gender |
   | 2 | org | Acme Pharma EMEA | Bridgewell Therapeutics | plausible peer in same industry |
   | 3 | date | 14 March 2024 | 22 May 2024 | shifted +69 days; preserves Tuesday weekday |
   | … | | | | |

4. Flag anything ambiguous — entities that *could* be identifying but the user might want to preserve (e.g. a regulatory body, a public incident).
5. **Stop.** Ask the user to:
   - approve the table as-is, or
   - edit specific rows (replace this name with that one), or
   - add/remove entries.

## Phase 2 — Apply

Once approved, hand off to `anonymise-document`'s rewriting procedure but using the **locked substitution map** from Phase 1 instead of inventing replacements on the fly. Output the anonymised document with the standard header and the final substitution log.

## When to prefer this over `anonymise-document`

- The user has strong preferences about pseudonyms (e.g. consistent across multiple documents).
- The document is high-stakes (legal disclosure, regulator submission) and the user needs an explicit audit trail before any rewrite happens.
- Multiple documents share entities and the user wants one canonical name-map applied across all of them.

## Persisting the name-map

If the user is processing several related documents, save the approved substitution table to `test-data/name-maps/<case-id>.md` (or wherever the user prefers) so subsequent documents reuse the same swaps. Consistency across documents is what makes a coordinated disclosure credible.
