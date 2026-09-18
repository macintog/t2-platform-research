# Bluetooth Marconi power control

[Research map](../README.md#bluetooth) · [Evidence catalog](../../catalog/README.md)

`AppleSPUMarconiControl` supplies a similarly narrow Bluetooth boundary. It
attaches through a dynamic `AppleSPUAppInterface`, sends selector/category
`0x20` with one Boolean power byte, caches requests until the transport is
ready, and retries the pending state. No HCI transport, firmware download,
GPIO sequence, or reset operation was recovered from that component. It should
not be used to explain a host firmware-name or baud-rate symptom without a
matched lifecycle observation.

## Evidence and scope

These findings retain the build and observation limits of the
[Linux compatibility inventory](../platform/linux-support.md). Exact source
revisions, module identities, and disassembly anchors are in
[Platform artifacts and method](../method/platform-artifacts.md).
