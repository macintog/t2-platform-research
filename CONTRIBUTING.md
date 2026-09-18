# Contributing research

Send a correction with the topic or finding ID, exact artifact or source
revision, and evidence that changes the claim. Distinguish static analysis,
hardware observation, source comparison, and inference. A negative result is
useful when it rules out an explanation or identifies a concrete missing input.

For hardware reports, include the model/board, kernel and driver revisions,
firmware build when known, transition type, relevant configuration, outcome,
and relative event timing. Follow the
[investigation guide](docs/method/investigation-guide.md) when choosing excerpts.
Keep installation-specific identities, raw camera images, unrelated machine
state, and firmware payloads out of contributions.

## Place findings by subject

Research lives under `docs/` by subsystem, with cross-cutting platform, power,
and method references. Extend an existing chapter when it answers the same
question. Create a narrowly named chapter when a reader needs a separate
contract or evidence record. Research rounds and acquisition dates are
provenance; they do not determine the directory hierarchy.

Give each finding a stable ID in [findings.json](catalog/findings.json). Add its topic
membership and any new aliases, document routes, or qualified relationships
to [research-map.json](catalog/research-map.json). Include both Linux-facing
names and names found in firmware or investigation logs. Do not treat aliases
as proof that two implementations or devices are equivalent.

Keep build, board, observation date, evidence type, and residual limits next to
the claim. Update affected older explanations when new evidence changes them;
date historical observations instead of silently turning them into current
support claims. A complete static investigation can still require runtime
qualification or a missing artifact.

## Check the collection

After changing a catalog or its linked chapters, regenerate the human maps and
run the structural checks:

```sh
python3 catalog/research.py build
python3 catalog/check_research.py
python3 -m unittest discover -s catalog/tests -v
```

The checks validate references and anchors, finding/topic coverage, board data,
generated-map consistency, ASCII JSON encoding, and common privacy hazards. They do
not establish technical correctness or hardware support. If reference code
changes, also run the [appendix checks](reference-code/README.md#validation).

Consult the [catalog guide](catalog/README.md) before changing its schema or
moving a document. Preserve finding IDs and update all affected references;
keep one maintained copy of each analysis.
