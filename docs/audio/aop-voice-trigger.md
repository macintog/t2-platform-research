# AOP audio and voice trigger

[Research map](../README.md#aop-audio) · [Evidence catalog](../../catalog/README.md)

The signed AOP image identifies separate voice-trigger and AOP-audio firmware.
Together with the host AppleAOPAudio comparator, it establishes high- and
low-power microphone clocks, listen-on-gesture state, AP sleep and wake
notifications, retained historic audio, wake hints, and four channel masks for
supported, enabled, voice-trigger, and history channels. This is a distinct
subsystem from the host-visible bridge-audio PCI function. The retained Linux
stack has no AOP-audio owner. Firmware property selector `0xc9` has now been
bounded to an exact 16-byte object containing those four 32-bit masks. A
separate control dispatcher accepts a 36-byte-base `SubPacket`, reads type at
`+0x04` and declared length at `+0x1c`, and supports the contiguous type range
`0xc3000000` through `0xc3000007`; outer commands `0x25` and `0x26` carry
40-byte client-power and 32-byte haptic requests. That controller function has
no timestamp field. Rehydrated build-matched `AppleAOPAudio` text closes the
separate live/historic envelope: packed `SpuMCAPacket` is a 20-byte header with
64-bit timestamp at `+0x00`, 64-bit byte count at `+0x08`, 32-bit total size at
`+0x10`, and audio payload at `+0x14`. Service type 1 carries live bytes after
the 36-byte `SubPacket`; type 5 nests the 20-byte historic packet there. Both
callbacks bound actual and declared sizes. The producer-side timestamp unit
remains unproven.

## Evidence and scope

These findings retain the build and observation limits of the
[Linux compatibility inventory](../platform/linux-support.md). Exact source
revisions, module identities, and disassembly anchors are in
[Platform artifacts and method](../method/platform-artifacts.md).
