# Contributing

Send a correction with the affected finding ID or document section, the exact
artifact or source revision, and the evidence that changes the claim. State
whether the result is static analysis, a hardware observation, or an inference.
A failed experiment is useful when it distinguishes competing explanations.

For hardware reports, include the model/board, kernel and driver revisions,
firmware build when known, transition type, relevant configuration, observed
outcome, and relative event timing. Follow the
[investigation guide](docs/investigation-guide.md) when selecting log excerpts.
Keep installation-specific identities and unrelated machine state out of the
submission. Explain an observation in terms of its configuration instead of
replacing identifying text with redaction markers.

Maintain both protocol and platform research here. Cross-link the relevant
chapters when a dependency spans subjects. Product-specific authentication and
desktop behavior belongs in t2touch, whose references pin a research revision.

Run the repository checks after editing:

```sh
python3 -m unittest discover -s tests -v
python3 examples/encode_identity.py
python3 scripts/verify.py
```

The checks validate document links, findings references, board data, artifact
hash syntax, and common privacy hazards. They do not replace a technical or
privacy review. Changes to the board data must agree with the readable table.
