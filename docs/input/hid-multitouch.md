# HID input, HIDSPI, and multitouch

[Research map](../README.md#multitouch) · [Evidence catalog](../../catalog/README.md)

## HIDSPI update and reset protocol

The retained J152f InputDevice package makes the top-case investigation more
specific. Its firmware-update protocol uses reports `0xb0` through `0xb3` for
initialization, chunk transfer, commit/status, and reset. Reports `0x13`,
`0xb8`, `0xbb`, and `0xbc` expose signing state, update parameters, component
versions, and hardware identity. Exact updater payloads include aggregate
initialization `b0 c3 bc`, per-target initialization `b0 62 72`, target commit
`b2 00`, status query `b2 a1`, aggregate commit `b2 c3 bc`, and reset `b3`.
They do not define ordinary input-report layouts. The HIDSPI policy specifies 256-byte
transfers, a 16-byte header, bounded retry, reset/detach/reattach teardown, and
SMC-event handling for quiesce, resume, restart, boot, shutdown, and OS boot.
These are concrete lifecycle requirements rather than a generic instruction to
retry a failed HID transaction.

## Power-state counter report

Input interface 2 also defines a 65-byte report `0x7e`: one report-ID byte
followed by sixteen four-byte power-state counters. Named fields include
`Active`, `Ready`, `Anticip`, `Diag`, and `ForceOnly`. Byte order, wrap, and
state exclusivity still require a trace, but the shape is sufficient for a
bounded read-only decoder.

## Multitouch report gate and AFU boundary

The embedded multitouch firmware distinguishes touch and force calibration,
tracks `NotTracking`, `MakeTouch`, `Touching`, and `BreakTouch` states, names
separate `FingerCluster` and `PalmThumbCluster` objects, and contains diagnostics
that label force-centroid coordinates in micrometers and force in grams. The
wire fields and scaling for those values remain unresolved. The retained Apple
driver admits exactly report IDs `0x28`, `0x29`, `0x31`, `0x43`, `0x44`,
`0x45`, `0x50`, `0x60`, and `0x73` through `0x76`, then forwards every
admitted frame to its raw user-client queue. Only `0x50` and `0x60` have
additional in-kext handling. Report `0x50` accepts exact 8-, 12-, and 16-byte
critical-error layouts, with bit fields and 32- or 64-bit timestamps at
recovered offsets. Exact `60 02` sets availability true, terminates an existing
multitouch device if present, and schedules an asynchronous rebuild. This
narrows the capture scope while leaving the opaque 144-byte contact report's
semantics in the absent `MultitouchHID.plugin`. The ST firmware's separate
internal path-response exchange is now bounded end to end: an `eb` request and
`e1` length response lead to an `ea` header, cookie check, two checksums, and a
variable payload copy. Its normal and recovery callers both use `0x6d9` as a
maximum capacity, not a fixed force or image length; a cleanup caller uses the
null-output branch. None of the three direct callers assigns a host report ID,
and the response helper omits an explicit inner-length-at-least-two check, so a
host reimplementation must add that lower bound. The firmware also
has explicit low-power, reboot, baseline, communication-error, bounded-reset,
and prior-power-state restoration paths. Recovering the contact report's
packed layout, rather than extending the generic HID descriptor parser, is the
direct path to pressure, palm, and recovery support.

## Evidence and scope

These findings retain the build and observation limits of the
[Linux compatibility inventory](../platform/linux-support.md). Exact source
revisions, module identities, and disassembly anchors are in
[Platform artifacts and method](../method/platform-artifacts.md).
