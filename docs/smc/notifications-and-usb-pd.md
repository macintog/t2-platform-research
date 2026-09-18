# SMC notifications, charging, and USB-PD

[Research map](../README.md#smc) · [Evidence catalog](../../catalog/README.md)

## SMC notification envelope

The signed AppleSMC implementation also shows why a working key interface is
not complete platform support. It contains system-state, power-state, thermal,
battery-authentication, and HID notification channels; named quiesce and
resume completion events; wake reasons; milliwatt power budgets; battery
overcharge and accessory-power handling; and per-port USB-PD state. Linux
currently exposes generic key access, fans, temperature entries, backlight, and
the `BCLM` charge limit, but not this notification and completion fabric.
Build-bound selectors are now known for prepare-for-S0, quiesce/resume,
wake-system, PCIe-ready, AP-sleep/AP-awake, and quiesce/resume-complete events.
The quiesce path reads and writes four-byte `MBSE`, writes one-byte `NTAP = 1`,
and the recovered overcharge path updates one-byte `BNOC`. The bridgeOS inbound
queue envelope uses byte 7 as a channel type and bytes 6, 5, and 4 as its
three-octet payload; bytes 0 through 3 are ignored in the recovered drain path.
Channel letters `p`, `q`, `r`, `s`, `t`, and `v` select system, power, HID,
battery-authentication, gas-gauge, and thermal handlers. That direction is
separate from the x86 host comparator's four-byte outbound `NMSN` write.
AppleSSM proves that byte 6 is its selector and byte 5 is the target power
state for `system-state-change`; special channels prove that bytes 5 and 4 are
event-specific arguments rather than a universal status/header pair.

## USB-PD current and voltage layouts

The per-port USB-PD keys are also narrower than an untyped key dump suggests.
`D%dIR` and `D%dAR` are resolved current limits in mA; `D%dVR` and `D%dSM`
are resolved/maximum voltage values in mV. `D%dSC` is seven zero-padded
`{u16 current_mA, u16 voltage_mV}` PDO records, with `D%dAI` selecting the
active record. `D%dos` packs low-16-bit current and voltage followed by the
adapter ID and family. Adapter description, ID, and family are independently
bound. The declared four-character SMC data types remain unavailable because
the charger fetches key info dynamically and caches only the attribute byte;
recovering those type codes requires a runtime `getKeyInfo` response or the
producer-side SMC key table.

## Evidence and scope

These findings retain the build and observation limits of the
[Linux compatibility inventory](../platform/linux-support.md). Exact source
revisions, module identities, and disassembly anchors are in
[Platform artifacts and method](../method/platform-artifacts.md).
