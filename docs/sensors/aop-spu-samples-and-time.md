# AOP and SPU sensor properties and time

[Research map](../README.md#aop-sensors) · [Evidence catalog](../../catalog/README.md)

The retained host sensor owner is also executable, not personality-only.
`AppleSPUHIDDriver` uses selector `0x0d` with four bytes for accelerometer
measurement range and `0x65` with one byte for factory mode; selectors `0x16`,
`0x5c`, and `0x00` carry four-byte batch, raw, and report intervals. Timesync
message `0xe3ff8100` is exactly 24 bytes and becomes a 17-byte HID report:
report ID `0xb0` plus two 64-bit values. The `AppleSPUHIDInterface` endpoint is
created dynamically from the AOP service report, so producer-side sample
layout, scale, axes, calibration schema, and timestamp unit remain the exact
missing edge.

## Evidence and scope

These findings retain the build and observation limits of the
[Linux compatibility inventory](../platform/linux-support.md). Exact source
revisions, module identities, and disassembly anchors are in
[Platform artifacts and method](../method/platform-artifacts.md).
