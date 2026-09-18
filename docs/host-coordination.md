# Host coordination

Host firmware determines how Intel system power management reaches the T2.
The recovered J152f ACPI contract and Apple's APP7777 coordinator describe
different provider configurations. They must remain separate.

## J152f ACPI

On one MacBookPro16,1 / J152f configuration, the T2 appears under
`\_SB.PCI0.RP17`. Read-only DSDT/SSDT inspection established:

- `RP17` exposes `_PRW` on GPE `0x69`, with lowest wake state 3.
- Its `_DSM` publishes `apple-coprocessor-version` with bytes
  `00 00 02 00 00 00 00 00`; their encoding remains uninterpreted.
- Functions 0–3 are `ANS2`, `IOBC`, `SEPM`, and `ADIO`.
- `IOBC`, `SEPM`, and `ADIO` implement `_PS0`/`_PS3` by clearing/setting
  the low two bits of PCI config `PSTA` at offset `0x44`.
- `ANS2` has empty `_PS0`/`_PS3` methods and publishes
  `pci-functions-dependent = 1`.
- `IOBC` and `SEPM` publish `pci-msi-flags = 1`; all four return `_STA = 0x0f`.

The examined tables contained no `APP7777`, ASOC, `SOCW`, `MBXC`, PNIC, WDOG,
or `MSTD` path. No ACPI method was evaluated. These observations establish the
examined firmware's boundary, not all revisions of J152f host firmware.

A useful Linux trace would show root-port and per-function PM ordering,
dependency handling, and actual D-state transitions. The DeviceTree's shared
T2 link is a reason to inspect coordination across these callbacks.

## APP7777 comparator

RecoveryOS `25G83` contains `AppleEmbeddedOSSupportHost`. Its IOKit personality
requires `IONameMatch = APP7777` under `IOACPIPlatformDevice`. Its methods show
a coordinated host power transaction:

1. Register priority sleep/wake interest.
2. Map sleep to 0 and wake/power-on to 1.
3. Evaluate ASOC `SOCW`, retry up to three times, and read/clear completion
   through `MBXC`.
4. Acknowledge the host notification after asynchronous work with a
   ten-second deadline.
5. On capability changes, wait for AppleSMC and read the two-byte `MSTD` key
   to check supporting-device quiescence.
6. Maintain separate sleep, power-on, and quiesce failure counts.

PNIC and WDOG provide panic/watchdog interrupt paths. Reset and DFU operations
are separate from the ordinary transaction.

The required provider is absent from the examined J152f tables. This driver is
therefore an Apple design comparator, with applicability to other machines
still to be established. Its methods are not a generic T2 recipe.

## SMC platform actions

The Apple host SMC implementation publishes `IOPlatformSleepAction` and
`IOPlatformWakeAction` values of `0xffffffff`. Its callbacks include
`setSMCToSleepStatic` and `wakeSMCFromSleepStatic`.

Public XNU [platform-action code](https://github.com/apple-oss-distributions/xnu/blob/main/iokit/Kernel/IOPlatformActions.cpp)
sorts sleep actions by signed ascending priority and reverses the supplied
priority for wake. The recovered value becomes -1 for sleep and 1 after
unsigned negation for wake. This places SMC before ordinary positive-priority
sleep actions and after their reversed wake actions, subject to that ordering
implementation. The public source is supporting mechanism evidence; it is not
a build-matched execution trace of RecoveryOS `25G83`.

## Graphics and root-port ownership

The MacBookPro16,1 board personality selects `Config3` in `AppleMuxControl2`:

| Property | Value |
| --- | --- |
| `PowerUpDownSequence` | `3` |
| `SaveRootPort` | `6` |
| `S0iControl` | `0x60990c89` |
| `GPUMinimumOffTime` | `200` |

No unit is assigned to the final value without a decoded consumer.
The implementation saves/restores GPU and HDA PCI state, handles
`PEG0 WillPowerOn` and `PEG0 HasPoweredOff`, waits for power-change interrupts,
and tracks `fPMSleepDone`. AMD and IOGraphics implementations expose matching
sleep/wake and mux acknowledgement paths.

Static analysis identifies coordinated ownership of the GPU/HDA/root-port
subtree. It does not establish a total callback sequence spanning SMC,
graphics, RP17/T2, and physical USB. A board-matched runtime trace is needed to
interleave these paths and compare them with Linux.
