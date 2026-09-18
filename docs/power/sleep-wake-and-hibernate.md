# Sleep, wake, and hibernate

[Research map](../README.md#storage) · [Evidence catalog](../../catalog/README.md)

This reference separates Apple host code, bridgeOS code, and Linux driver
behavior. The analyzed firmware is bridgeOS `23P6068`; the Apple host comparator
is RecoveryOS `25G83`. [Artifact hashes](../method/platform-artifacts.md) bind the
findings to those inputs.

## BCE state preservation

The host `IOBufferCopyController::sendSleepMessage()` begins with a 4 KiB state
buffer and sends `SAVE_STATE_AND_SLEEP` (`0x17`). A firmware rejection (`0x19`)
returns a required size. The host rounds up and retries requests through 1 MiB.
`SAVE_RESTORE_STATE_COMPLETE` (`0x1a`) reports completion. Failure to construct
the memory descriptor or DMA command selects `SLEEP_NO_STATE` (`0x14`).

On wake, a retained descriptor selects `RESTORE_STATE_AND_WAKE` (`0x18`),
expecting `0x1a`, then releases the mapping and buffer. Without a descriptor,
the host sends `RESTORE_NO_STATE` (`0x15`). The recovered ordinary-suspend
policy is stateful-first with a bounded buffer negotiation and a setup-failure
fallback. It does not describe every firmware rejection as a no-state fallback.

The analyzed Linux t2bce stack implements this command family, coordinates
VHCI and audio clients, and rebuilds the virtual USB topology for no-state
resume. It forgets child devices, restarts the controller, cycles virtual-port
power, and calls `usb_root_hub_lost_power()`. The host VHCI message and event
queue allocations persist across that path; Linux does not re-register the
complete queue graph. Its PM completion and shutdown paths are substantive
support, but they do not prove that bridgeOS reconstructed every peer-side
queue or that unrelated host devices and virtual peripherals recovered.

RTBuddy's cold-boot-after-hibernate policy is a separate S4 mechanism. It must
not be presented as a third ordinary BCE save-state choice.

## VHCI exceptions and message direction

The bridgeOS `AppleUSBVHCIFirmware` controller has Off, Sleep, Suspend, and On
states. Its state machine handles queues, devices, ports, remote wake, shutdown,
and exceptions that may need to wait for another power state. Some exception
paths return the controller to Off.

In this firmware's `processInterrupts()`, event `0x50` selects a branch that
logs `exception reported by host` and calls `hardwareException(0x10)`. Unknown
events take a different branch. This identifies an exception path on the
**firmware side**.

The Linux host's `bce_vhci_handle_system_event()` at
[t2bce revision a973d53](https://github.com/deqrocks/t2bce/blob/a973d53c8278e9db5ff8314b816d6880309ed39e/t2bce_vhci/vhci.c#L1143)
dispatches command completions and valid port-status changes, then warns for
other events. An incoming `0x50` has no dedicated branch. The upstream revision
was checked on September 18, 2026 and matches the research checkout revision.

The Linux BCE management-command namespace separately reserves opcode `0x50`
for `SET_MEMORY_QUEUE_PROPERTY` in `t2bce_dma/queue.c`; the pinned source has no
caller. That opcode is not a VHCI system-event definition. The retained
September 2026 incoming-`0x50` log also lacks the outer queue and completion
record needed to identify its producer. These three uses of the same number
must remain separate.

These are complementary observations, not yet a complete bidirectional
protocol mapping. The firmware branch consumes a host-reported exception;
the Linux report describes an event received from firmware. Before assigning
identical semantics, trace the producer, queue direction, framing, and state on
both sides. A matching number alone cannot establish that Linux should call an
equivalent recovery operation, or that doing so would repair
[the reported post-resume desynchronization](https://github.com/t2linux/kernel/issues/24).

VHCI messages are fixed 16-byte records containing `u16 cmd`, `u16 status`,
`u32 param1`, and `u64 param2`. Bit `0x8000` marks a reply and bit `0x4000`
marks cancellation. Five host-to-firmware message submission queues and five
firmware-to-host event submission queues share one completion queue. The
low-level BCE management queue assigns a generation to each command slot and
increments it after timeout, preventing a stale completion from satisfying a
retired waiter. VHCI command replies, deferred USB events, and transfer
completions carry no equivalent epoch.

That difference bounds the desynchronization problem. A command mismatch,
repeated cancellation timeout, completion-index mismatch, or completion from a
retired epoch should quarantine the BCE function and stop new URBs before a
complete local queue rebuild. Endpoint reset and virtual-child reset remain
valid for faults confirmed to be local to those objects. Shared-link recovery
is a separate platform transaction, not a VHCI fallback. See [Reset and queue
boundaries](../platform/pci-services-and-dma.md#reset-and-queue-boundaries).

## Wake aggregation and SMC

In `AppleUSBVHCIFirmwareBCE`, `smcNotification` distinguishes host-running,
host-unusable, sleep/standby, and shutdown states. Sleep/standby calls
`reportSystemWakeEvents()` without itself driving the controller state change.
Host-unusable, shutdown, and the other accepted terminal notification types
enter `hardwareException(1)`.

`reportSystemWakeEvents()` examines up to 16 port objects, ORs their wake events
into a 16-bit mask, and schedules notification when the mask is nonzero.
`smcNotifier()` calls AppleSMC `system-state-notify` with selector `0x80` and
the mask's low and high bytes.

The broader SMC vocabulary includes `PrepareForS0`, `Wake`, `ShutdownOS`,
`SystemRestart`, `SystemShutdown`, `QuiesceDevices`, `QuiesceComplete`,
`ResumeDevices`, `ResumeComplete`, `WakeSystem`, `PCIeReady`, `APSleep`,
`APAwake`, `APPanic`, `ReqOSShutdown`, and `ReqOSSleep`.

This establishes bidirectional system-state coordination beyond sensors and
keyboard backlight. It does not require a Linux host AppleSMC driver to copy
all bridgeOS-side actions. Completion payloads, wake-reason meanings, and the
host initiation path remain incompletely mapped.

## PMGR and RTBuddy

PMGR implements sleep, wake, quiesce, clock/power gating, panic, restart, and AP
wake-source programming. RTBuddy adds per-coprocessor policies including
`power-managed`, `user-power-managed`, `dont-power-on`, `quiesced`,
`no-shutdown`, `sleep-on-hibernate`, `no-hibernate-sleep`, and
`cold-boot-after-hibernate`. Different coprocessors may sleep, survive, or restart
across a transition.

Prelink properties assign PMGR sleep/wake priority 600 and quiesce priority
90000; SEP quiesce priority is 89999. Under XNU's ascending platform-action
ordering, SEP precedes PMGR's final quiesce action. PMGR includes a check that
power-state devices are off. This is a static ordering constraint, not a full
runtime chronology.

The same PMGR arrays occur in every DeviceTree in the analyzed build:

| Property | Record layout | Recovered checks |
| --- | --- | --- |
| `ap-wake-sources` | 36 bytes: little-endian `u32` ID and 32-byte name | IDs `0..351`; 352-source bitmap |
| `ap-wake-source-flags` | 8 bytes: `u32` ID and `u32` flags | Out-of-range IDs rejected |
| `power-domains` | 24 bytes; 16-byte name at offset 8 | Byte 3 is a nonzero domain ID below 64; bytes 0 and 2 are flags; bytes 4–7 are range-checked selectors |

The selectors' semantic names remain unknown. A decoder should preserve their
numeric values instead of inventing names. Static records can label future
traces; they do not show which source actually woke a machine.

## ANS ordinary sleep and cancellation

The bridgeOS `IONVMeFamily::systemPowerChange` path maps
`kIOMessageCanSystemSleep` (`0xe0000270`) to ANS opcode `0x309` and
`kIOMessageSystemWillNotSleep` (`0xe0000290`) to `0x30a`.
`SendSleepNotificationToANS` allocates a 4 KiB command object, writes the opcode
at offset `0x0c`, and checks transport and ANS/ASP status separately. For
`0x309`, reply byte `0x18` bit 0 supplies the caller's accept/veto result.

Apple's [IOMessage definitions at revision
`f6217f891ac0bb64f3d375211650a4c1ff8ca1ea`](https://github.com/apple-oss-distributions/xnu/blob/f6217f891ac0bb64f3d375211650a4c1ff8ca1ea/iokit/IOKit/IOMessage.h)
identify the two notification constants. The binary analysis supplies the ANS
mapping. These are ordinary-sleep negotiation and cancellation; an S4-specific
opcode and complete hibernate sequence have not been recovered. The pinned
public source is the reviewed comparator, not a claim that it matches the
RecoveryOS `25G83` build.

The provider graph places `AppleASCANS2` under `AppleARMIODevice`, RTBuddy
under `AppleA7IOPNub`, and `AppleANS2OOB`/`AppleANS2NVMeController` downstream
of RTBuddy. `NVMeSEPNotifier` attaches to `AppleSEPManager`, establishing a
storage/SEP coordination edge. The embedded controller also has orderly NVMe
shutdown, sleep cancellation, and `nvme-s2r-timeout` policy.

## SEP and persistent clients

BridgeOS `AppleSEPManager` includes endpoint hold/unhold operations, active
endpoint masks, OS-active acknowledgements, sleep-mode selection, sleep-control
abort/error/timeout handling, and a five-second power-gate deadline. It also
coordinates low-power state and FIPS reseeding, has a hibernate-specific boot
path, and participates in xART/gigalocker shutdown.

The xART work identified coordinated client disable and acknowledgements. In
restore/update paths, Apple waits for the APFS container reaper before the
gigalocker shutdown user-client operation. That is evidence about those paths;
it must not be silently promoted to the exact S4 sequence. See the related
[storage research](../storage/sep-persistence-and-nvme.md).

The SEP transport examined in the Linux experiments had probe/remove paths
but no driver PM or shutdown callbacks. Generic PCI PM may or may not be
sufficient; this requires endpoint and queue-lifetime evidence. The inactive
control reproduced the leading failures without active SEP transport, so the
missing callbacks are not an established cause of those failures.

## AOP sensor time and retention

Fifteen of the sixteen signed DeviceTrees publish the base AOP children
`accel`, `aop-audio`, `gyro`, and `pressure`; J160 publishes none of those
children. The signed T2 AOP image independently names accelerometer and
gyroscope implementations, a separate `systick` service, endpoint enable and
version checks, versioned IMU calibration, 64-bit sample timestamps, and
bounded historical queues.

Those facts establish distinct lifecycle obligations without supplying a
Linux sensor ABI. A suspend-aware consumer must preserve the AOP timestamp and
Linux receipt boottime, estimate their offset with uncertainty, and start a new
generation after an AOP or host discontinuity. It must validate calibration
version and format, plus any integrity fields recovered from the sensor
contract, before applying it. It must also handle historical-queue
backpressure. Static artifacts do not establish accel/gyro endpoint numbers,
property selectors, timestamp units, axis orientation, or checksum fields.
For lid angle specifically, the J152f/J215 `las` child, `hidrelay-enable`,
`LASC` calibration property, and AOP MA781/MagAlpha/LAS cluster strongly
suggest AOP ownership of the lid-angle sensor (USB `05ac:8104`). The missing DeviceTree
product ID and relay parser leave the exact transport connection unproven.
Do not project that result onto the other AOP sensors or invent their units and time semantics.

## PCIe and peripheral lifecycle

`AppleEmbeddedPCIeUpLinkMgmt` tracks function D-states, link L-states, LTSSM,
LTR, PERST relay, and S0 deassertion deadlines. It coordinates SMC and reset
callbacks and waits for link/PHY readiness. `AppleEmbeddedPCIE` adds port
quiesce/resume, deep-sleep entry/exit, refclock gating, endpoint reset, and
link-failure handling. Four successful host callbacks cannot prove this shared
link state machine completed.

All sixteen `23P6068` DeviceTrees place ANS2, BCE, SEP, and audio on the same
x4 Gen2 link and bind them to DART streams `1`, `0`, `2`, and `3`. The stripped
`AppleT8015DART` reload path at `0xfffffff006bd3d5c` visits every controller and
SMMU instance, compares active-stream state across paired SMMUs, and returns to
the outer client-notification path at `0xfffffff006bd3c8c`. This supports a
whole-DART ordering rule: quiesce DMA clients, reconstruct translation state,
invalidate or verify streams, then resume clients. It does not recover the
names of each stripped helper or authorize an x86 host reset.

A BCE function reset is appropriate only while the upstream link and stream 0
remain valid. Shared PERST must be owned above the individual functions and
must coordinate ANS2, BCE, SEP, audio, and all four DART streams. No inspected
x86 Linux driver owns that cross-function transaction.

The bridge-audio endpoint saves and restores five GPR words, but it owns words
0-3 and the macOS host writes only the word-4 sleep cookie. A Linux PM path
must revalidate the current mapping and shared structure rather than replay all
five words. The distinct AOP-audio subsystem has low-power microphone and
retained-history states. Multitouch has reset, auto-suspend, and
power-state messaging; J152f's SPI device has its own clock/reset sequence.
Camera/ISP, display/media, USB PHYs, and biometric hardware have separate power
policies. Watchdog code includes AP/system/userspace monitoring and an extended
quiesce watchdog, so a non-return can also involve firmware timeout enforcement.

These dependencies define [post-wake acceptance](../method/investigation-guide.md).
They do not make every enumerated driver a suspect in each failure.
