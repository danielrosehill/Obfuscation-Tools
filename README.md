# Obfuscation Tools

![Obfuscation Tools header](images/header.png)

Agent skills for sharing real material without sharing the real details. Instead of blanking things out, they replace identifying details with plausible stand-ins, so the result stays useful and still reads as real.

| Redaction | Obfuscation |
|---|---|
| `Failed on [ENTITY] at [IP]` | `Failed on light.guest_bedroom_ceiling at 192.168.50.41` |

The two main uses:

- **Bug reports and logs.** Entity names, IPs, hostnames and IDs change, but subnets, group membership, formats and errors survive, so a maintainer can debug it as if it were the original.
- **Sensitive documents.** Whistleblower disclosures, complaints and incident diaries keep their narrative while people, organisations, places and dates change.

## Proximity

The main parameter is how close replacements stay to the originals, chosen from the privacy and risk background:

- **conservative**: the lightest touch, with near neighbours of the originals. For low-risk sharing with outsiders.
- **moderate**: same category, clearly a different thing.
- **liberal**: only the role in the story survives. For when an insider could recognise the source, or exposure carries real consequences.

Details are in [`references/proximity-levels.md`](references/proximity-levels.md) and [`references/technical-substitutions.md`](references/technical-substitutions.md).

## Skills

- `obfuscate-bug-report`: obfuscate a bug report, log or config while keeping it debuggable.
- `obfuscate-document`: obfuscate a document at a chosen proximity level.
- `propose-substitutions`: preview and approve the replacement table before anything changes.
- `scan-and-obfuscate`: detect PII and secrets, then replace the findings. Uses [`pii-scanner`](https://github.com/danielrosehill/Claude-PII-Scanner-Plugin) if it's there, and falls back to regex if not.

## Script

`scripts/obfuscate.py` uses only the Python standard library, so replacements don't depend on a model rewriting text correctly.

```bash
python3 scripts/obfuscate.py scan   log.txt --profile home-assistant --out findings.json
python3 scripts/obfuscate.py apply  log.txt --map map.json --out log.obfuscated.txt
python3 scripts/obfuscate.py verify log.obfuscated.txt --map map.json
```

- `scan` lists IPs (classed as private or public), MACs, emails, hostnames, UUIDs, secrets, home-directory users and coordinates. `--profile home-assistant` adds entity IDs.
- `apply` replaces in one pass, longest value first, so `10.0.0.1` doesn't touch `10.0.0.12` and a replacement is never rewritten. It rejects maps that merge two values or collide with text already in the source, and it won't overwrite the input.
- `verify` looks for any surviving original, including case changes and other forms such as `kitchen_ceiling` for `Kitchen Ceiling`. It exits 1 on a leak.

`test-data/bug-report/` has a worked example with synthetic data: `ha-log.original.txt`, `ha-log.map.json` and `ha-log.obfuscated.txt`.

## Limits

- `verify` proves mapped values are gone. It can't prove the map was complete, so a person should still read the output.
- Swapping names doesn't hide facts. Who attended a meeting, or who could access a file, can identify a source with no names at all. Skills check for this at liberal, but no tool guarantees anonymity.
- An obfuscated document contains altered facts, so it isn't evidence. Keep the original unchanged, and take legal advice before a formal disclosure.
- Maps decode the output, so they're stored in the plugin's data directory, away from the files they produced.

## Installation

```bash
claude plugins install obfuscation-tools@danielrosehill
```

## History

Started in December 2024 as an LLM assistant configuration for helping whistleblowers anonymise documents, then became the `anonymisation-assistant` plugin in April 2026. Renamed and widened to `obfuscation-tools` in November 2026. The original prompts remain in `configurations/`, and synthetic diary fixtures in `test-data/`.

## License

MIT
