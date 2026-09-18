# Credits

The T2 research began with
[jmurth1234/t2-touchid-linux](https://github.com/jmurth1234/t2-touchid-linux), whose
transport and biometric implementation provided the foundation for the working
proof of concept. That project remains under its own GPL license.

The modules in this repository were written during the subsequent native-adoption
work and are offered here under MIT. They cover identity request encoding and
activation-secret persistence. Their names are retained to make comparison with
the research implementation easier.

Toni Bergholm contributed the bridgeOS `23P2048` identity-create-v4 protocol
finding to t2touch. This repository credits that discovery while expressing the
wire-format facts in its own MIT-licensed reference implementation.

[T1Bridge](https://github.com/standardagents/t1bridge/tree/7003b8d9f791) informed the
retained-secret lifecycle and enrollment transaction design. Its referenced
[license](https://github.com/standardagents/t1bridge/blob/7003b8d9f791/LICENSE) is MIT.
The T2 sequence uses different credential details and transport; no T1Bridge source
files are included here.

Protocol layouts were recovered through analysis of Apple software and checked
against observations on T2 hardware. The reference modules express those findings as request encoders, decoders, and
local storage.

The [research reference](docs/research/README.md) describes the SEP structure and
protocol findings in original prose under MIT. Its
[artifact and tool credits](docs/research/artifacts-and-method.md) identify the
firmware builds and analysis tools used.

## Platform research

The platform references were assembled by macintog using Codex, including
signed-artifact analysis and Linux experiments. They extend the protocol work
with board inventories and power-management analysis.

- [t2linux](https://github.com/t2linux) supplies kernel/distribution context,
  hardware guidance, and the field reports cited in the platform chapters.
- [deqrocks/t2bce](https://github.com/deqrocks/t2bce) supplies the Linux BCE,
  virtual USB, and audio implementation compared here.
- [Apple's published XNU](https://github.com/apple-oss-distributions/xnu)
  supplies message definitions and platform-action ordering code.
- [The Apple Wiki](https://theapplewiki.com/wiki/T2) supplies the secondary
  mapping from firmware identities to Mac model names.
- [ipsw](https://github.com/blacktop/ipsw),
  [radare2](https://github.com/radareorg/radare2),
  [7-Zip](https://www.7-zip.org/), and
  [ACPICA](https://github.com/acpica/acpica) supported image inspection,
  disassembly, APFS extraction, and ACPI interpretation.

External reports establish observations for their stated configurations.
Referenced projects and artifacts retain their own licenses and attribution.
