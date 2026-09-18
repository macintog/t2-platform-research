# Bridge audio: endpoint state and playback clock

[Research map](../README.md#bridge-audio) · [Evidence catalog](../../catalog/README.md)

## Endpoint GPR ownership and lifetime

Apple's bridge-audio endpoint and the Linux driver already agree on a
version-3 shared structure with signature `0x19870423`, room for 20 devices,
128-byte device names, five input and five output stream slots, and 100 memory
segments per stream. Apple's endpoint additionally has explicit `saveGPRs()`
and `restoreGPRs()` paths. The exact saved set is five 32-bit words at offsets
`0x0`, `0x4`, `0x8`, `0xc`, and `0x10`; the restore path then checks the
signature at offset `0x4`. A matched macOS host comparator proves split
ownership: the endpoint writes words 0 and 1 plus mapping-derived words 2 and
3; the host writes only word 4, the sleep cookie `0x19770525`. When that
cookie is lost, the host remaps and revalidates word 2 and the shared
structure it points to. Linux instead binds its shared-structure pointer from word 2 only
at probe and never revalidates it on either resume path. The proposed
five-word host replay is therefore withdrawn: it could restore a stale
endpoint-owned address, and reading back a signature the host just wrote does
not establish endpoint readiness. Further work should target read-only
revalidation and safe rebind, after allocation lifetime is established for
stateful, no-state, and aborted transitions. Runtime loss on this machine
remains unmeasured.

## Playback sampleTime feedback

A separate gap affects the playback clock. Apple's bridge-audio timestamp
command is 45 bytes: a 13-byte outer header, 8-byte base command, 64-bit
timestamp, 64-bit Boolean reset flag, and binary64 `sampleTime` frame
position. Linux parses the timestamp and reset seed but ignores `sampleTime`,
so its interpolation begins from frame zero. That field provides clock
feedback; it does not depend on accepting the withdrawn register replay.

## Evidence and scope

These findings retain the build and observation limits of the
[Linux compatibility inventory](../platform/linux-support.md). Exact source
revisions, module identities, and disassembly anchors are in
[Platform artifacts and method](../method/platform-artifacts.md).
