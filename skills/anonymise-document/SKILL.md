---
name: anonymise-document
description: Use when the user wants to anonymise a sensitive document (whistleblower disclosure, harassment diary, incident report, internal complaint) by replacing identifying details while preserving narrative integrity, factual accuracy, and evidentiary value. Operates on a file path or pasted text and produces an anonymised version with a standard header.
---

# Anonymise Document

Process a sensitive document and produce an anonymised version. The goal is **safe sharing** — strip identifying details so the document cannot be traced back to specific people or institutions, while keeping the substance (incidents, policy violations, dynamics) intact and credible.

Human supervision is mandatory. Always tell the user to review the output before sharing it externally.

## Inputs

- **Source**: a file path, or pasted text. If a path, read it. Default location for fixtures is `test-data/originals/` in this repo.
- **Output path** (optional): where to write the redacted version. Default: alongside the input with `.anonymised.md` suffix.
- **Scope hint** (optional): the user may narrow scope (e.g. "only swap names, keep dates"). Honour this over the defaults below.

## Anonymisation rules

**Replace** (with credible, plausible alternatives — not `[REDACTED]` placeholders):

- Personal names — individuals and organisations
- Specific locations that could reveal identity (city → region; office address → "head office")
- Dates — modify while preserving temporal relationships (e.g. shift everything by a consistent offset; preserve weekdays and intervals)
- Unique identifying characteristics (rare job titles, unusual physical traits, distinctive phrasing)
- Digital platform names where they narrow the surface (e.g. an internal Slack workspace name)
- Highly specific job titles → generalise ("Director of Regulatory Affairs for EMEA" → "senior compliance lead")
- Institutional affiliations — company names, schools, regulators

**Preserve unchanged**:

- Core narrative and chronology
- Incident descriptions and severity
- Policy violations and procedural failures
- Workplace dynamics, power relationships
- Discriminatory or harassing actions
- Evidentiary detail necessary for the document's purpose

**Consistency**:

- Use the same replacement for the same entity throughout the document. Build a mental name-map as you go.
- Preserve professional relationship dynamics — if "Anna" was Bob's manager, the replacement must remain in that managerial position.
- Keep industry-specific context intact (a hospital story stays a hospital story).

## Output format

Prepend this header to the anonymised document:

```
ANONYMIZED DOCUMENT
Date: [Modified Date]
Notice: Names and specific details have been altered to protect the identities of all parties involved while preserving the document's essential truth and context.
```

Then the body. After the body, append a short **Substitution log** — a table of original → replacement for the user's audit. This is critical: without it the user cannot verify the swaps or remember them across documents.

## Procedure

1. Read the source.
2. Identify identifying markers (skim once; list mentally).
3. Build a substitution map. For each entity, choose a credible alternative — common-but-not-real names, plausible institutions, shifted-but-coherent dates.
4. Apply replacements consistently throughout.
5. Verify chronology and relationships still hold.
6. Write the anonymised version to the output path (or print if no path given).
7. Append the substitution log.
8. Remind the user: **review the output before sharing**, especially for inadvertent identifying detail in the prose itself (a unique phrase, a giveaway anecdote).

## Reference fixtures

The `test-data/` folder in this repo contains synthetic diary inputs and their before/after pairs. Use them as style guides for the level of transformation expected.

## Related

- For previewing substitutions before applying them, use `propose-substitutions` instead.
