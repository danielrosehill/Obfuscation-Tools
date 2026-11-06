# Technical substitution rules

The test for every swap: **would a maintainer debug this the same way with the replacement as with the original?** The rules below override the proximity level when they conflict.

## Never change

Error messages, exception types, public library stack frames, version numbers, exit and HTTP status codes, config keys, integration or platform names, public hostnames of the software involved, line order, and log levels. These are the bug.

## Load-bearing traits

Before replacing a value, ask what about it could matter, then keep that trait:

- Length, if the bug might involve truncation or limits.
- Character class: a hyphen, a space, a leading digit, uppercase, non-ASCII or right-to-left text. If an entity called `Büro-Licht 2` breaks parsing, its replacement needs an umlaut, a hyphen, a space and a digit.
- Sort order, where the list order matters.
- Membership: if it matters that a name is in the lights group, the replacement must still read as a light in that group.
- Relationships: same subnet, same parent, same prefix, same device.

## By type

| Type | Keep | Replacement |
|---|---|---|
| Private IPv4 | RFC 1918 block, subnet relationships, role of `.1` or a gateway, host octet where it's harmless | Change the subnet octet the same way everywhere: `192.168.77.41` and `192.168.77.5` become `192.168.50.41` and `192.168.50.5`. At liberal, change block too (`10.20.30.x`) |
| Public IPv4 | That it is public | Always a documentation range at every level: `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24` (RFC 5737) |
| IPv6 | Scope (link-local, ULA, global) | Global addresses become `2001:db8::/32` (RFC 3849). ULAs get a different `fd00::/8` prefix |
| Loopback, `0.0.0.0`, multicast, netmasks | Everything | Leave alone |
| Ports | Standard and software-default ports | Change only custom ports that fingerprint a setup |
| MAC address | OUI if the vendor is relevant to the bug | Keep the first three bytes and replace the last three. If the vendor is irrelevant, use a locally administered address (`02:...`) |
| Hostnames | Shape and suffix (`.local`, `.lan`) | Role-style names: `ha-attic.local` becomes `ha-server.local` |
| Domains | That it is a domain | `example.com`, `example.net`, `example.org`, or a `.example` name (RFC 2606) |
| Usernames, emails | Format | `homeuser`, `user@example.com`; several users stay distinct: `user1`, `user2` |
| Paths | Depth, extension, spaces, case | Replace only the identifying segments: `/home/jhartwell/ha-config/` becomes `/home/homeuser/ha-config/` |
| UUIDs, device IDs, serials, hashes | Exact length, alphabet, case, separators | Random value of the same shape, one per original. Don't use repeating digits if the format has a checksum; note it if you can't keep the checksum valid |
| Secrets, tokens, passwords | Length only if relevant | Obvious fake such as `EXAMPLEKEY00`. Never lookalike-random, because readers must not mistake it for a real credential |
| Private keys | Nothing | Remove the whole block. Stop and tell the user |
| Coordinates | Hemisphere and rough scale, if relevant | Round to a nearby generic point, or use a well-known public landmark |
| Timestamps | Intervals, order, milliseconds | Usually leave alone. If they matter for privacy, shift everything by one fixed offset. The timezone offset can reveal location |
| SSIDs, device names, room names, people's names | Character traits and role | Plausible neighbour: `Marlowe Nursery Ceiling` becomes `Guest Bedroom Ceiling` |

## Home Assistant

- Keep the domain: `light.` stays `light.`, `binary_sensor.` stays `binary_sensor.`.
- Keep the naming structure, area then device then function: `light.marlowe_nursery_ceiling` becomes `light.guest_bedroom_ceiling`.
- Keep function words such as `ceiling`, `motion`, `battery` and `occupancy` when the bug concerns them. Rooms and people's names go.
- Keep `device_class`, `platform`, `integration`, service names (`light.turn_on`) and attribute keys.
- A group's replacement must still read as a group of its members. An area shared by entities keeps one shared replacement.
- Treat `secrets.yaml`, `zone.home`, `latitude`, `longitude`, `person.*` and `device_tracker.*` as sensitive.

The same thinking carries over to other systems. Keep the part of a name the software reads, and change the part only the owner chose.

## Forms of the same value

One value often appears in several forms. Map each form explicitly:

- Name forms: `Kitchen Ceiling`, `kitchen_ceiling`, `kitchen-ceiling`, `KitchenCeiling`.
- MAC forms: colons, hyphens, no separators, upper and lower case.
- Encoded forms: URL-encoded, base64, JSON-escaped, and values embedded in filenames, URLs or topic paths.
- Derived values: a hash or ID built from the original. Replace the derived value as its own map entry.
