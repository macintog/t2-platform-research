# T2 platform research

Original research into Apple T2 hardware, firmware, and the interfaces Linux
needs to use them. The collection brings together recovered protocols,
board topology, driver comparisons, hardware observations, and the boundaries
that remain unresolved.

## Find a subsystem

| Subject | Start with |
| --- | --- |
| Secure Enclave and Touch ID | [SEP services and AKS identity](docs/README.md#sep) · [Fingerprint lifecycle](docs/README.md#fingerprint) |
| Dual-GPU graphics | [gmux, i915/amdgpu, panel timing, and VFCT](docs/README.md#graphics) |
| Audio | [Bridge audio state and clock feedback](docs/README.md#bridge-audio) · [AOP audio and voice trigger](docs/README.md#aop-audio) |
| Camera and media | [ISP exposure and UVC controls](docs/README.md#camera-isp) · [AVE video encoding](docs/README.md#ave) |
| Sensors | [Lid-angle sensor (LAS)](docs/README.md#las) · [AOP/SPU motion and time](docs/README.md#aop-sensors) · [Ambient light](docs/README.md#als) |
| Input | [Trackpad and Force Touch](docs/README.md#multitouch) · [Touch Bar USB/DRM](docs/README.md#touch-bar) |
| Power and charging | [Sleep, wake, and hibernate](docs/README.md#power) · [SMC, battery, thermal, and USB-PD](docs/README.md#smc) |
| Transport and storage | [BCE, VHCI, and DART](docs/README.md#bce) · [ANS2, NVMe, and xART](docs/README.md#storage) |
| Boot and recovery | [iBoot, EFI, firmware updates, and Linux boot](docs/README.md#boot) |
| Network and clocks | [Wi-Fi](docs/README.md#wifi) · [Bluetooth](docs/README.md#bluetooth) · [Thunderbolt](docs/README.md#thunderbolt) · [Ethernet](docs/README.md#ethernet) · [RTC](docs/README.md#rtc) |

The [research map](docs/README.md) connects Linux names, firmware components,
device IDs, functionality, and findings. The
[platform overview](docs/platform/pci-services-and-dma.md) explains the host/T2
boundary; the [board matrix](docs/platform/board-configurations.md) identifies
model-specific policy. The [coverage map](docs/platform/research-coverage.md)
states what was examined and what evidence is still needed.

## Read the evidence

The main firmware inventory covers 16 production configurations in bridgeOS
`23P6068`. Most host observations concern MacBookPro16,1 / J152fAP. A separate
SEP reference covers identity-create-v4 on MacBookPro16,2 / J214K with
`23P2048`. A recovered interface or a successful experiment on one configuration
does not establish support across the family.

Chapters distinguish static analysis, hardware observations, comparisons, and
inference. [Artifact identities and extraction methods](docs/method/platform-artifacts.md)
and the [SEP artifact record](docs/method/sep-artifacts.md) make results
traceable without redistributing firmware. Use the
[investigation guide](docs/method/investigation-guide.md) to identify a missing
measurement or contribute a correction.

## Machine-readable references

- [Research catalog](catalog/research-map.json): topic IDs, aliases, Linux and
  firmware names, document routes, qualified relationships, and coverage.
- [Findings](catalog/findings.json): stable finding IDs with evidence type, scope, and
  links to the analysis.
- [Boards](catalog/boards.json): production configurations and DeviceTree identities.
- [Catalog guide](catalog/README.md): schema, lookup commands, and maintenance
  rules. Human maps are generated from the same catalog.

## Repository contents

| Directory | Purpose |
| --- | --- |
| [docs](docs/README.md) | Research chapters, evidence, and subsystem maps for readers. |
| [catalog](catalog/README.md) | Machine-readable indexes and optional scripts to search them, regenerate maps, and check the collection. |
| [reference-code](reference-code/README.md) | Python implementations of recovered AKS message formats and activation-bundle storage, with examples and tests for integrators. |

The catalog scripts operate on this repository's documents and indexes. The
reference code illustrates specific protocol and persistence contracts; it
does not provide a driver or fingerprint service. Neither is needed to read
the research, and there is nothing to install.

## Reuse and contributions

The original explanations, reference code, and collection tools use the
[MIT license](LICENSE). [Credits](CREDITS.md) identify contributed findings,
comparison sources, and analysis tools. [Contributing](CONTRIBUTING.md) explains
how to add evidence and keep both reader and machine indexes useful.
