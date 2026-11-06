#!/usr/bin/env python3
"""Deterministic scan / apply / verify for obfuscation-tools. Standard library only.

  obfuscate.py scan   FILE [--profile home-assistant] [--out findings.json]
  obfuscate.py apply  FILE --map MAP.json --out OUTPUT
  obfuscate.py verify OUTPUT --map MAP.json [--profile home-assistant]

The map is JSON: {"entries": [{"original": "...", "replacement": "...", "type": "..."}]}.
A flat {"original": "replacement"} object also works.

Exit codes: 0 ok, 1 leak or invalid map, 2 usage or I/O error.
"""
import argparse
import ipaddress
import json
import re
import sys
from pathlib import Path

DOC_NETS = [ipaddress.ip_network(n) for n in
            ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24", "2001:db8::/32")]
IGNORED_IPS = {"0.0.0.0", "127.0.0.1", "255.255.255.255", "255.255.255.0", "::1", "::"}

DETECTORS = {
    "private-key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "secret": r"\b(?:sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{40,}"
              r"|xox[baprs]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16}"
              r"|eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+)\b",
    "secret-assignment": r"(?i)\b(?:password|passwd|pwd|secret|token|api[_-]?key)\b[\"']?\s*[=:]\s*[\"']?([^\s\"',}]{4,})",
    "bearer": r"(?i)\bbearer\s+([A-Za-z0-9._~+/=-]{8,})",
    "email": r"[\w.+-]+@[\w-]+\.[\w.-]*\w",
    "ipv4": r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w]|\.\d)",
    "ipv6": r"(?<![\w:.])(?:[0-9A-Fa-f]{1,4}:){2,7}(?::?[0-9A-Fa-f]{1,4})+(?![\w:])",
    "mac": r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b",
    "uuid": r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b",
    "hex-id": r"\b[0-9a-f]{24,64}\b",
    "private-hostname": r"(?i)\b[a-z0-9][a-z0-9-]*(?:\.[a-z0-9-]+)*\.(?:local|lan|home|internal|corp|intranet|home\.arpa)\b",
    "url-host": r"(?i)\bhttps?://([a-z0-9.-]+\.[a-z]{2,})",
    "home-path-user": r"(?:/home/|/Users/|C:\\Users\\)([A-Za-z0-9._-]+)",
    "coordinate": r"(?i)\b(?:lat|latitude|lon|lng|longitude)\b[\"']?\s*[=:]\s*[\"']?(-?\d{1,3}\.\d{3,})",
}
PROFILES = {
    "home-assistant": {
        "ha-entity": r"\b(?:alarm_control_panel|automation|binary_sensor|button|calendar|camera|climate"
                     r"|cover|device_tracker|fan|group|humidifier|input_[a-z]+|light|lock|media_player"
                     r"|person|remote|scene|script|sensor|siren|switch|update|vacuum|weather|zone)"
                     r"\.(?!turn_on\b|turn_off\b|toggle\b|reload\b|py\b|yaml\b)[a-z0-9_]+\b",
    },
}
PUBLIC_DOMAINS = re.compile(r"(?i)(^|\.)(example\.(com|net|org)|github\.com|githubusercontent\.com"
                            r"|home-assistant\.io|pypi\.org|python\.org)$")


def read(path):
    try:
        return Path(path).read_text(encoding="utf-8", errors="surrogateescape")
    except OSError as e:
        die(str(e))


def die(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(2)


def classify_ip(value):
    """Return a subtype, or None if the value is not worth flagging."""
    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        return None
    if value in IGNORED_IPS or ip.is_loopback or ip.is_unspecified or ip.is_multicast:
        return None
    if any(ip in n for n in DOC_NETS if n.version == ip.version):
        return None
    if ip.is_link_local:
        return "link-local"
    return "private" if ip.is_private else "public"


def scan(text, profile=None):
    detectors = dict(DETECTORS)
    if profile:
        detectors.update(PROFILES[profile])
    found = {}
    for lineno, line in enumerate(text.splitlines(), 1):
        for category, pattern in detectors.items():
            for m in re.finditer(pattern, line):
                value = m.group(1) if m.groups() else m.group(0)
                subtype = None
                if category in ("ipv4", "ipv6"):
                    subtype = classify_ip(value)
                    if subtype is None:
                        continue
                if category == "url-host" and PUBLIC_DOMAINS.search(value):
                    continue
                item = found.setdefault((category, value), {
                    "category": category, "subtype": subtype, "value": value, "count": 0, "lines": []})
                item["count"] += 1
                if lineno not in item["lines"]:
                    item["lines"].append(lineno)
    return sorted(found.values(), key=lambda f: (f["category"], f["lines"][0]))


def load_map(path):
    try:
        data = json.loads(read(path))
    except json.JSONDecodeError as e:
        die(f"{path}: {e}")
    entries = data.get("entries") if "entries" in data else [
        {"original": k, "replacement": v} for k, v in data.items()]
    return [e for e in entries if e.get("original")]


def check_map(entries, text):
    problems, seen_rep, originals = [], {}, {e["original"] for e in entries}
    for e in entries:
        o, r = e["original"], e["replacement"]
        if o == r:
            problems.append(f"replacement equals original: {o!r}")
        if r in originals:
            problems.append(f"replacement is also a real value: {r!r}")
        if r in seen_rep and seen_rep[r] != o:
            problems.append(f"two originals share a replacement, which merges distinct things: {r!r}")
        seen_rep[r] = o
        if pattern_for(r).search(text):
            problems.append(f"replacement already appears in the source, which would be ambiguous: {r!r}")
    return problems


def pattern_for(value):
    left = r"(?<![A-Za-z0-9_])" if re.match(r"\w", value[0]) else ""
    right = r"(?![A-Za-z0-9_])" if re.match(r"\w", value[-1]) else ""
    if value[0].isdigit():
        left += r"(?<!\d\.)"
    if value[-1].isdigit():
        right += r"(?!\.\d)"
    return re.compile(left + re.escape(value) + right)


def apply_map(text, entries):
    """One pass, longest original first, so a replacement is never rewritten again."""
    table = {e["original"]: e["replacement"] for e in entries}
    alternatives = [pattern_for(o).pattern for o in sorted(table, key=len, reverse=True)]
    counts = dict.fromkeys(table, 0)

    def swap(match):
        counts[match.group(0)] += 1
        return table[match.group(0)]

    return re.sub("|".join(alternatives), swap, text), counts


def squash(value):
    return re.sub(r"[^a-z0-9]", "", value.lower())


def verify(text, entries, profile=None):
    lowered, squashed = text.lower(), squash(text)
    replacements = {e["replacement"] for e in entries}
    squashed_reps = [squash(r) for r in replacements]
    leaks, possible = [], []
    for e in entries:
        o = e["original"]
        if o.lower() in lowered and not any(o.lower() in r.lower() for r in replacements):
            leaks.append(o)
        elif len(squash(o)) >= 5 and squash(o) in squashed and not any(squash(o) in r for r in squashed_reps):
            possible.append(o)
    residue = [f for f in scan(text, profile)
               if f["value"] not in replacements
               and not any(f["value"] in r for r in replacements)]
    return {"leaks": leaks, "possible_variant_leaks": possible, "unmapped_detections": residue}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("scan", "apply", "verify"):
        p = sub.add_parser(name)
        p.add_argument("file")
        if name != "scan":
            p.add_argument("--map", required=True)
        if name != "apply":
            p.add_argument("--profile", choices=sorted(PROFILES))
        if name != "verify":
            p.add_argument("--out", required=name == "apply")
    args = parser.parse_args()
    text = read(args.file)

    if args.command == "scan":
        result = json.dumps(scan(text, args.profile), indent=2, ensure_ascii=False)
        if args.out:
            Path(args.out).write_text(result + "\n", encoding="utf-8")
        else:
            print(result)
        return 0

    entries = load_map(args.map)
    if args.command == "apply":
        if Path(args.out).resolve() == Path(args.file).resolve():
            die("--out must differ from the input; originals are never overwritten")
        problems = check_map(entries, text)
        if problems:
            print(json.dumps({"map_problems": problems}, indent=2, ensure_ascii=False))
            return 1
        output, counts = apply_map(text, entries)
        Path(args.out).write_text(output, encoding="utf-8", errors="surrogateescape")
        print(json.dumps({"out": args.out, "replacements": sum(counts.values()),
                          "unused_originals": [o for o, n in counts.items() if n == 0]},
                         indent=2, ensure_ascii=False))
        return 0

    report = verify(text, entries, args.profile)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if report["leaks"] else 0


if __name__ == "__main__":
    sys.exit(main())
