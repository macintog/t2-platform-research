# T2 SEP and Touch ID research

These notes describe how Linux created its own T2 account identity, enrolled
fingerprints, and restored them after reboot. They cover the Secure Enclave
services, wire formats, and persistent state behind that result.

## Read the protocol references

| Read | For |
| --- | --- |
| [SEP architecture](sep-architecture.md) | Host transports, internal services, mailbox framing, and request ownership. |
| [Identity and authorization](identity-and-authorization.md) | Creating a keybag, preserving its activation input, and authorizing enrollment. |
| [Boot and persistent storage](boot-and-storage.md) | EFI startup, xART, gigalocker backing, and embedded NVMe namespaces. |
| [Fingerprint lifecycle](fingerprint-lifecycle.md) | First enrollment, Catacomb construction, restore, matching, and deletion. |
| [Integration contracts](integration-contracts.md) | Account authority, stable names, interrupted-operation recovery, and client ownership. |
| [Artifacts and method](artifacts-and-method.md) | Firmware identities, analysis tools, and ways to reproduce the findings. |
| [Create-v4 on J214K](create-v4-j214k.md) | The earlier identity-create layout and its reported qualification. |
| [Combined findings index](../../findings.json) | Machine-readable entry points into the same explanations. |

## Scope

The reference platform is MacBookPro16,1 / J152fAP with bridgeOS 10.6 build
`23P6068`. The protocol supports Linux-owned account creation, activation,
fingerprint enrollment, matching, deletion, and persistent Catacomb storage.
The full t2touch integration supplies the transport, authorization, fprintd,
PAM, and desktop behavior around these operations.

MacBookPro16,2 / J214K with bridgeOS `23P2048` uses an explicitly selected
version-4 identity-create body. Its contributor-reported creation, enrollment,
verification, sudo, and restart results do not establish full lifecycle or
graphical coverage on that model. Each protocol reference identifies the
firmware build to which its layouts and findings apply.

The Mac continues to run Apple's bridgeOS and SEP firmware. Broader hardware,
multiple users, suspend recovery, and persistence across a macOS boot require
separate qualification. The reference modules require a hardware integration; compatibility with
untested firmware remains unqualified.

## Reuse

This research is available under the [MIT license](../../LICENSE). The notes are original explanations of the research findings.
Each reference names the tested or analyzed build where that affects the result.
Protocol identifiers belong to their stated interface: an AKS operation number, a BiometricKit command, and an
internal SEP service handle can have the same value without naming the same thing.

## Platform dependencies

[Platform architecture](../platform-architecture.md) maps the host and firmware
boundaries. [Power management](../power-management.md#sep-and-persistent-clients)
explains the SEP/xART dependencies relevant to sleep and shutdown.
