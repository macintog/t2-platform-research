# Credits and provenance

T2 platform research is an original research collection maintained by
[macintog](https://github.com/macintog), with Codex used for analysis,
implementation, and review. It combines firmware and host-software analysis,
protocol reconstruction, Linux source comparisons, and configuration-specific
hardware observations. The explanations, catalogs, and reference modules use
the repository's [MIT license](LICENSE).

## Contributed findings and observations

Toni Bergholm contributed the bridgeOS `23P2048` identity-create-v4 finding and
the J214K hardware qualification recorded in the
[version-4 reference](docs/sep/aks-create-v4-j214k.md#evidence-boundaries-and-reported-hardware-qualification).
The reference distinguishes that report from retained offline analysis and
does not extend it to untested lifecycle or graphical behavior.

Reports from t2linux contributors and other hardware users supply observations
for the configurations cited in individual chapters. Those reports retain
their attribution and uncertainty; a reported symptom is not automatically a
confirmed cause.

## Implementations and sources used in the research

| Source | Contribution to this work |
| --- | --- |
| [jmurth1234/t2-touchid-linux](https://github.com/jmurth1234/t2-touchid-linux) | Transport and biometric implementation used in the early working proof of concept. Subsequent SEP mechanisms and reference modules are documented here with their own evidence. |
| [T1Bridge](https://github.com/standardagents/t1bridge/tree/7003b8d9f791) | A comparator for retained-secret lifecycle and enrollment transactions; T2 credentials and transport differ. No T1Bridge source files are included. |
| [t2linux](https://github.com/t2linux) | Kernel and distribution context, hardware guidance, and attributed field reports. |
| [deqrocks/t2bce](https://github.com/deqrocks/t2bce) | Linux BCE, virtual USB, and bridge-audio implementations compared with recovered firmware contracts. |
| [Apple's published XNU](https://github.com/apple-oss-distributions/xnu) | Public message definitions and platform-action ordering comparators, distinguished from build-matched binary evidence. |
| [The Apple Wiki](https://theapplewiki.com/wiki/T2) | Secondary mappings between firmware board identities and Mac model names. |

Other narrowly used implementations are cited at the relevant finding. Exact
revisions, addresses, hashes, and evidence limits belong with the analysis,
rather than in a general list of acknowledgments.

## Analysis tools and artifacts

Artifact acquisition and analysis used OpenCorePkg's macrecovery, ipsw,
DyldExtractor, sepsplit-rs, radare2, 7-Zip, and ACPICA. Their roles and recorded
versions are documented in [SEP artifacts and method](docs/method/sep-artifacts.md#research-credits)
and [platform artifacts and method](docs/method/platform-artifacts.md).

Apple firmware and host software are subjects of the analysis. Firmware
payloads are not included. Referenced software, reports, and artifacts retain
their own licenses and attribution; this collection's MIT license applies to
its original material and does not relicense those sources.
