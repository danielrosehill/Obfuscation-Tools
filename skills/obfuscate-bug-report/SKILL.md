---
name: obfuscate-bug-report
description: "Obfuscate a bug report, tool log or config before sharing. Swaps IPs, hostnames and entity names for stand-ins, keeps it debuggable."
---

# Obfuscate a bug report

Prepare a bug report, log, config or stack trace for a public tracker by replacing real details with realistic stand-ins. This is not PII redaction: `[REDACTED]` and `<ip>` markers destroy the structure a maintainer needs. A good result reads like a real report from a different, equally real setup.

## Inputs

- **Source**: file paths or pasted text. Save pasted text to a working file first.
- **Proximity level**: see `references/proximity-levels.md`. Use the level the user named. Otherwise recommend **conservative** and ask once, because a public bug report usually carries low risk.
- **The bug**: one sentence on what is being reported. Without this you can't tell which details are load-bearing, so ask if it isn't clear from the source.
- **Case ID** (optional): a short name, used to reuse a map across follow-up comments on the same issue.

## Steps

1. Read `references/technical-substitutions.md`.
2. Run the scanner for structured values. Add `--profile home-assistant` for Home Assistant material:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/obfuscate.py" scan <source> --out <work>/findings.json
   ```
3. Read the source yourself for what regex misses: custom names, room and device names, people, projects, employers, addresses, SSIDs, and identifying free text.
4. Decide what is load-bearing for this bug. List any trait you are keeping and why.
5. Build the map at `<maps-dir>/<case-id>.json` (see Data storage), with every form of each value as its own entry. Load the existing map first if the case has one.
6. Show the user the table of original, replacement and type, with load-bearing notes. Skip this only if the user asked for no review. If the bug hinges on a value that can't be obfuscated, say so here.
7. Apply it. This refuses a map with collisions and never overwrites the source:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/obfuscate.py" apply <source> --map <map> --out <source-stem>.obfuscated<ext>
   ```
8. Verify. A non-zero exit means an original survived:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/obfuscate.py" verify <output> --map <map>
   ```
   Add entries for `leaks` and `possible_variant_leaks`, judge each of the `unmapped_detections`, and repeat from step 7 until clean.
9. Read the output once as the maintainer would. Check that subnets, groups, ordering and error text still make sense.
10. Give the user the output path. Offer this line for the report: "Identifying values are replaced with stand-ins; structure, versions and errors are unchanged." It stops maintainers from chasing a fake address.

If the bug can't be reproduced from the obfuscated values and the maintainer asks, map replacements back from the saved map for a private reply.

## Screenshots and attachments

This skill handles text. Screenshots need image redaction, and files need metadata stripped. Tell the user about any that come with the report.

## Data storage

Maps go in `${CLAUDE_USER_DATA:-${XDG_DATA_HOME:-$HOME/.local/share}/claude-plugins}/obfuscation-tools/maps/`. A map decodes the output, so never place one beside the output, inside a repo, or in the report.

## Notes

- If `CLAUDE_PLUGIN_ROOT` is unset because the skill was loaded without installing the plugin, download `scripts/obfuscate.py` from `https://raw.githubusercontent.com/danielrosehill/Obfuscation-Tools/main/scripts/obfuscate.py` to the working directory.
- A private key in the source stops the job until its block is removed.
- `verify` proves the mapped values are gone. It cannot prove the map was complete, so steps 3 and 9 still matter.
