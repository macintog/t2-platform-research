# Dual-GPU graphics: gmux, panel timing, and VFCT

[Research map](../README.md#graphics) · [Evidence catalog](../../catalog/README.md)

## Intel panel sequencing

J152f's working Intel route and broken AMD duplicate-panel route are now tied
to distinct firmware inputs. Intel reads a valid 256-byte panel EDID and drives
3072×1920 even though i915 reports no VBT. MacEFI's `CoffeelakeGraphics`
component selects Intel platform ID `0x3e9b0008` for the J152 profile. Its five
AAPL00 `Panel*` properties are not published: the conditional publication path
is disabled, and all five backing panel fields are zero. MacEFI instead
programs the PCH panel-sequencer registers directly. The decoded timings are
12.5 ms for panel power-up, 210 ms for backlight-on, 74 ms for panel
power-down, and 250 ms for backlight-off. The configured cycle-delay field
encodes zero. A read-only live i915 check reports 13/210/74/250/500 ms: it
preserves the four component timings within register granularity and raises
the effective cycle delay to 500 ms from its other sources.

## AMD VFCT connector topology

AMD obtains its Navi 14 ROM from ACPI VFCT. The hash-bound J152f VFCT image
header selects `1002:7340` at function 0 but sets both subsystem IDs to zero,
despite PCI reporting Apple subsystem `106b:0210`. The retained amdgpu path
correctly matches vendor, device, and function without requiring the subsystem
IDs and treats the bus number as a preference. That behavior should survive
any connector or switching fix. Its ATOM object tables describe five paths:
one LCD1/eDP path and four DisplayPort paths, each with connector, encoder,
AUX/I2C, and HPD relationships. The internal panel entry supplies neither a
DTD nor link rate/lane count; it carries only a 500 ms power-off delay, and the
single PowerPlay platform-capability word is zero. VFCT therefore supplies
topology and a ROM, not a complete panel-training or power-policy recipe.

## gmux policy and switch transactions

AppleMuxControl2 selects `Config3` for this board, with
`PowerUpDownSequence = 3`, `SaveRootPort = 6`,
`S0iControl = 0x60990c89`, and `GPUMinimumOffTime = 200`. The parser retains
`S0iControl` only when bit 0 is set; maps the two sequence bits to policy bits
`0x8` and `0x200`; maps nonzero power-up compensation and root-port saving to
`0x80` and `0x100`; maps clamshell values 1 and 2 to `0x20` and `0x40`; and
clamps root-port and minimum-off values to 6 and 250. State handlers use
5,000, 2,000, 3,000, and 9,000 ms watchdogs. Those internal policy bits and
Apple state IDs are evidence for design, not a proposed Linux ABI.

The state machine coordinates gmux, both framebuffers, the discrete GPU, its
HDA function, the PEG root port, backlight, display and AUX routes, readiness
gates, interrupts, timeouts, reset validation, aborts, and bounded error
handling. The EG-reset restore path retries once; a separate sequential switch-
error budget begins at five. Recovery saves HDA before G3D, performs at most
one reset, polls the vendor ID and G3D BAR0 within fixed bounds, and has a
separate HDA restore or abort path. The current Linux
`force_igd` patch reaches a useful cold-boot endpoint but implements only the
route selection and default-VGA choice. MacEFI's IGD and DIS route tuples
exactly match Linux's current gmux constants: ports (`0x10`, `0x28`, `0x40`),
IGD values (`2`, `1`, `2`), and DIS values (`3`, `2`, `3`). EFI command 4
zeros `0x50`, command 8 zeros `0x58`, and command 12 zeros both in
`0x50`-then-`0x58` order; all three then program the full IGD route in display,
AUX, external order. Linux's helper currently writes AUX, display, external.
The semantic name of `0x58` remains unresolved, but its command chronology is
no longer unknown. EFI polls mailbox readiness around primitive writes but has
no semantic route readback or interrupt wait, and dispatch does not propagate
per-write failure or roll back earlier writes. The bounded prototype is
internal-eDP-only and symmetric across i915 and amdgpu: it keeps both connector
objects registered, represents unknown ownership and generation-stale state,
and gates detect, mode enumeration, AUX access, and stream construction. It
does not cover external DP/MST, HPD, or HDA. Both DRM reprobe callbacks are
currently null, `NEEDS_EDP_CONFIG` has no consumer, and J152f amdgpu lacks the
PX PM-domain wrapper. Safe runtime power-off and switching therefore still
require a larger prepare/switch/validate/commit-or-abort transaction.

## Evidence and scope

These findings retain the build and observation limits of the
[Linux compatibility inventory](../platform/linux-support.md). Exact source
revisions, module identities, and disassembly anchors are in
[Platform artifacts and method](../method/platform-artifacts.md).
