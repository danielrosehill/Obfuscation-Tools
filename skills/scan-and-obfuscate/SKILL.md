---
name: scan-and-obfuscate
description: "Scan files for PII and secrets with gitleaks, Presidio and a personal inventory, then replace findings with stand-ins, not blanks."
---

# Scan and obfuscate

Detect PII with the `pii-scanner` framework, then obfuscate the findings. Detection tells you what's there. This skill turns those findings into realistic replacements, not blanks. Use it when the concern is unknown exposure across a file or folder, rather than a report you already know you are sharing.

## Inputs

- **Target**: a file, or a folder of text files.
- **Proximity level**: see `references/proximity-levels.md`. Ask once if not given.
- **Material type**: technical (logs, configs) or prose (documents). If mixed, handle each file by its type.

## Steps

1. **Detect.** Run these layers and merge the results:
   - The `pii-scan` skill from the `pii-scanner` plugin, if available: credentials from gitleaks, generic PII from Presidio, and matches against the user's personal inventory. Inventory matches matter most, since they are the user's own real data. Use its report's raw matches, kept in its data directory, as your input.
   - The built-in regex layer, which adds technical identifiers the framework doesn't focus on, such as MACs, UUIDs, private hostnames and coordinates:
     ```bash
     python3 "${CLAUDE_PLUGIN_ROOT}/scripts/obfuscate.py" scan <file> --out <work>/findings.json
     ```
   If `pii-scanner` isn't available, tell the user the scan is reduced to regex and your own reading: there are no NER names or inventory matches.
2. **Triage.** Sort findings into:
   - **Remove**: private keys and live credentials. Secrets get an obvious fake value or removal, never a realistic stand-in.
   - **Obfuscate**: identifying values.
   - **Keep**: false positives, public facts, and the user's deliberate public details such as an intended author name.
3. **Build the map.** Technical values follow `references/technical-substitutions.md`. Prose follows `references/proximity-levels.md`. One map per case covers all files, so a value gets the same replacement everywhere.
4. **Review.** Show counts by category and the proposed table. In the conversation, mask secrets and inventory values. Wait for approval.
5. **Apply and verify** per file. Outputs are new files and originals stay untouched:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/obfuscate.py" apply <file> --map <map> --out <output>
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/obfuscate.py" verify <output> --map <map>
   ```
6. **Rescan the outputs** with the same detection layers. Every remaining finding must be a replacement you chose or a confirmed false positive. Scanners will flag realistic replacements, so compare the findings against the map, not against zero.
7. Report files written, counts by category, anything kept and why, and the map path.

## Data storage

Maps go in `${CLAUDE_USER_DATA:-${XDG_DATA_HOME:-$HOME/.local/share}/claude-plugins}/obfuscation-tools/maps/`. Never store one in a scanned repo or beside the output.

## Notes

- If `CLAUDE_PLUGIN_ROOT` is unset, download `scripts/obfuscate.py` from `https://raw.githubusercontent.com/danielrosehill/Obfuscation-Tools/main/scripts/obfuscate.py` to the working directory.
- This works on file contents only. Rewriting git history is a separate decision for the user, and anything already published stays exposed.
