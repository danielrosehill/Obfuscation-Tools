# Proximity levels

Obfuscation has one main parameter: how close each replacement stays to its original. Pick it from the privacy and risk background, not from taste. Ask once per job unless the user has already said.

| Level | Meaning | People and organisations | Places | Dates | Fits when |
|---|---|---|---|---|---|
| **conservative** | Replacements stay as close as they safely can | Same gender, culture and country; peer organisation of the same kind and size | Same country, similar kind of place | Shift by days | Readers are outsiders, exposure would be embarrassing rather than harmful, and fidelity matters most |
| **moderate** | Same category, clearly a different thing | Same gender and broad culture; same sector, different size or profile | Different region of the same country | Shift by weeks | Default for documents when the risk is unclear |
| **liberal** | Only the role in the story survives | Gender and culture may change if the story doesn't depend on them; adjacent sector; titles generalised | Different country or a generic description | Shift by months, or relative dates only | An insider could recognise the source, or exposure could bring retaliation, legal or safety consequences |

"Conservative" here describes how much changes, not how much privacy you get. Conservative is the lightest touch. Liberal gives the most protection.

## Choosing

Ask, in one message:

1. Who will read this, and could any of them recognise the people or the events?
2. What happens if someone works out the source? (Mild embarrassment, job loss, legal action, physical risk.)
3. Which details must survive for the document to do its job?

Any insider reader, or any serious consequence, means **liberal**. State the recommended level and the reason, and let the user override it.

## Rules at every level

Adapted from the rule set behind the Proximate-Pseudonymizer model:

- One replacement per entity across the whole text and across every document in the case.
- Related forms change together: `Ciarán`, `ciaran.oneill@...`, `C. O'Neill`, `@ciaran_o`.
- Replacements must not be too close. No kept first names, spelling variants or nudged handles.
- Never use a real, identifiable person or organisation as a replacement, even a proximate one. Check that an invented organisation name is not a real company in that sector.
- Relationships, hierarchy, sequence and intervals survive. If A managed B, the replacements keep that.
- Countries and public figures normally stay, unless they narrow the source down.

## What substitution cannot do

Swapping names does not remove the facts. At **liberal**, add a fingerprint pass, because these identify a source after every name has gone:

- Events few people attended or knew about ("only three of us were in that meeting").
- Who could have had access to a document, and any per-recipient differences in it.
- Distinctive phrasing, writing style, or a giveaway anecdote.
- Rare combinations of otherwise ordinary traits.
- File metadata, tracked changes and comments in the source file.

List each one found and ask the user how to handle it. An obfuscated document has altered facts, so it is not evidence and must never be presented as verbatim. The original stays intact and unchanged.
