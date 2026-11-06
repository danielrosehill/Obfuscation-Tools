---
name: obfuscate-document
description: "Obfuscate or anonymise a sensitive document, whistleblower disclosure or complaint: swap names and orgs at a chosen closeness."
---

# Obfuscate a document

Replace identifying details in a document with credible alternatives, keeping its substance intact. The aim is safe sharing: nobody can trace it to specific people or institutions, and it still reads as a true account.

Human review is mandatory. Tell the user to review the output before sharing it.

## Inputs

- **Source**: a file path or pasted text.
- **Proximity level**: conservative, moderate or liberal, from `references/proximity-levels.md`. **Always settle this before rewriting.** If the user hasn't named one, ask the three questions in that file, recommend a level with the reason, and wait for the answer.
- **Output path** (optional): defaults to the source path with an `.obfuscated.md` suffix.
- **Scope hint** (optional): for example "only swap names, keep dates". This overrides the defaults below.
- **Case ID** (optional): reuses one map across related documents.

## What changes

Replace with credible alternatives, not `[REDACTED]` markers, at the chosen level:

- Names of people and organisations, including nicknames, initials, email addresses and handles.
- Locations that could reveal identity.
- Dates, by a consistent offset that preserves intervals and weekdays.
- Job titles specific enough to name one person.
- Institutional affiliations, regulators and schools, unless the user wants them kept.
- Internal system, project and workspace names.
- Unique characteristics: rare traits, distinctive phrasing.

## What stays

- The core narrative and chronology.
- Incident descriptions and their severity.
- Policy violations and procedural failures.
- Power relationships and workplace dynamics.
- Discriminatory or harassing conduct.
- Evidentiary detail the document needs for its purpose.
- The industry context: a hospital story stays a hospital story below liberal.

## Steps

1. Read the source and settle the level.
2. Load the case map if there is one. List every identifying detail and each form it takes.
3. Choose replacements under the rules in `references/proximity-levels.md`. For high-stakes work, or when the user wants control over the swaps, use `propose-substitutions` first.
4. Save the map as JSON in the maps directory (see Data storage).
5. Apply the plain swaps:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/obfuscate.py" apply <source> --map <map> --out <output>
   ```
   Then rewrite by hand whatever a literal swap gets wrong: grammar, pronouns, possessives, and descriptive phrases that identify a person without naming them.
6. Check that chronology and relationships still hold.
7. Verify that no original survives. Fix any leak, then run again:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/obfuscate.py" verify <output> --map <map>
   ```
8. At **liberal**, run the fingerprint pass from `references/proximity-levels.md`, and list what you found for the user to decide on.
9. Prepend the header:
   ```
   OBFUSCATED DOCUMENT
   Notice: Names and specific details have been altered to protect the identities of all parties involved while preserving the document's essential truth and context.
   ```
10. Report the output path, the level used and the map path. Remind the user to review it for giveaway details in the prose.

Keep the substitution table out of the output. It stays in the map, because a table attached to the document would undo the work.

## Data storage

Maps go in `${CLAUDE_USER_DATA:-${XDG_DATA_HOME:-$HOME/.local/share}/claude-plugins}/obfuscation-tools/maps/`. A map reveals everything the document hides. Keep it away from the output.

## Notes

- If `CLAUDE_PLUGIN_ROOT` is unset, download `scripts/obfuscate.py` from `https://raw.githubusercontent.com/danielrosehill/Obfuscation-Tools/main/scripts/obfuscate.py` to the working directory.
- For PDF or Word sources, extract to text and produce a new file. Editing in place can leave originals in metadata, revision history or hidden layers.
- `test-data/` holds synthetic before-and-after diary pairs that show the expected depth of change.
