# Research catalog

The catalog is the collection's discovery layer. Paths and section references
in JSON are relative to the repository root. Markdown chapters hold the
analysis; catalogs route readers to it and preserve evidence scope.

The Python scripts in this directory search and maintain those indexes. They
do not communicate with T2 hardware or implement its protocols. Protocol
implementations belong in the separate [reference-code directory](../reference-code/README.md).

## Catalog files

| File | Contents |
| --- | --- |
| [research-map.json](research-map.json) | Topics, aliases, document inventory, qualified relationships, and examined-area dispositions. |
| [findings.json](findings.json) | Stable finding IDs, claims, evidence types, scope, and precise references. |
| [boards.json](boards.json) | Production board identities, policy fields, and artifact hashes. |

Catalog JSON uses ASCII spelling, such as `I2C` and ordinary hyphens, so source
viewers do not flag typographic lookalikes. Use JSON Unicode escapes if an exact
non-ASCII identifier must be preserved.

## Optional scripts

| Script | Purpose |
| --- | --- |
| [research.py](research.py) | Search topic aliases, resolve a topic to evidence, and generate the human research and coverage maps. |
| [check_research.py](check_research.py) | Check links, catalog coverage, board tables, generated maps, JSON character encoding, and privacy patterns. |

Both use Python 3.10 or newer and its standard library. Reading the Markdown or
JSON requires neither script.

## Schema

Each file declares `schema_version`. Version 1 of the research map has these
collections:

- `topics`: stable `id`, readable `title`, search `aliases`, `linux_interfaces`,
  `firmware_components`, user-facing `function`, ordered `references`, and
  `finding_ids`. The first reference is the suggested entry point.
- `documents`: stable `id`, canonical `path`, `title`, document `kind`, and
  topic membership. Cross-cutting methods may apply to several topics.
- `relationships`: `source` and `target` topic IDs, a descriptive `kind`,
  `evidence`, explanation, and source reference. Evidence is `observed`,
  `recovered`, `inferred`, or `unresolved`. Edges are qualified research
  relationships, not an assertion of complete hardware connectivity.
- `coverage`: stable examined-area `id`, `title`, topics, status, residual
  `limit`, and evidence references. Status is `bounded-static-complete`,
  `missing-input`, `runtime-evidence-needed`, `physical-qualification-needed`,
  or `qualification-decision`.
- `interfaces`: a partial host-route tree with stable `id`, interface `type`,
  `parent` ID (null at the root), hardware `identity`, topics, evidence, scope,
  and references. PCI records add numeric `function` and `dart_stream` fields.
  A USB parent identifies host transport, not an inferred firmware owner.

A topic is a retrieval boundary, not a support claim. Linux interface names can
identify a comparator or a missing integration. An alias is a search term, not
a declaration that two devices or protocols are identical. For example, AOP
matches separate audio and sensor topics; LAS routes to lid angle, while ISP
routes to camera controls and AVE routes to encoding.

## Bounded lookups

Read the JSON directly, or use the optional standard-library Python helper:

```sh
python3 catalog/research.py search LAS
python3 catalog/research.py search 05ac:8104 --limit 3
python3 catalog/research.py search AppleKeyStore
python3 catalog/research.py search ISP
python3 catalog/research.py show camera-isp
```

`search` returns at most five results by default (`--limit` accepts 1–50).
Matching ignores case and punctuation. Exact IDs rank before exact aliases;
word matches and prefixes of at least four characters follow. Short acronyms
do not match inside unrelated words. An empty or unknown query returns no results.

`show` accepts a stable topic ID or a unique exact alias. It returns ordered
entry references with current one-based line ranges, complete finding records
including scope, related documents, qualified relationships, and coverage
limits. Ambiguous names produce an error listing candidate topic IDs. It does
not dump entire chapters or infer missing evidence.

For reliable analysis, retrieve the indicated section and its artifact/method
reference. Read the finding's evidence and scope before using it. A negative
result, inferred owner, or unqualified prototype must retain that distinction.

## Maintain one map

Edit the catalog and canonical chapters, then run:

```sh
python3 catalog/research.py build
python3 catalog/check_research.py
```

The first command regenerates [the human research map](../docs/README.md) and
[coverage map](../docs/platform/research-coverage.md). The second checks their
consistency along with topic membership, finding coverage, document inventory,
references, board tables, and privacy patterns. Do not edit generated maps by
hand.

When moving a chapter, update its document record, all references in catalogs,
and Markdown links in the same change. Keep finding IDs stable when correcting
claims. Add new research under its subject; retain acquisition dates and build
identities as provenance within the analysis.
