# Camera ISP exposure and UVC controls

[Research map](../README.md#camera-isp) · [Evidence catalog](../../catalog/README.md)

The retained camera descriptor exposes no standard camera-terminal or
processing-unit controls. Its 26-byte extension unit declares one possible
control but publishes a zero control bitmap, so it enables no selector. The
earlier apparent extension-selector lead was a descriptor-structure
misinterpretation. Initial exposure, image policy, and privacy-LED ownership
must instead be traced through AppleM8/ISP properties and lifecycle code. One
internal property path has been traced through the user-client boundary: for
command conversion, `SetCameraProperty(0)` substitutes `0.0` for inputs
outside inclusive `[-3,3]`, computes `exp2` of the working value, converts it
to 16-bit Q8, and emits a 20-byte ISP command with opcode `0x0204` through
IOKit selector 7; on success it caches the original input. The kernel routine
that gates this operation is identified independently, and its selector-7
dispatch-table entry remains unproven. This is not a UVC selector. The
connection to caller policy and the component controlling privacy and the LED
remain unresolved.

The retained state-7 completion warning occurred during cancellation while
complete frames still arrived; it should be treated as a teardown race until
reopen and recovery behavior are separately qualified.

## Evidence and scope

These findings retain the build and observation limits of the
[Linux compatibility inventory](../platform/linux-support.md). Exact source
revisions, module identities, and disassembly anchors are in
[Platform artifacts and method](../method/platform-artifacts.md).
