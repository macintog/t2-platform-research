# Power management

This reference separates Apple host code, bridgeOS code, and Linux driver
behavior. The analyzed firmware is bridgeOS `23P6068`; the Apple host comparator
is RecoveryOS `25G83`. [Artifact hashes](artifacts-and-method.md) bind the
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
VHCI and audio clients, and reconstructs queues and the root hub for no-state
resume. Its PM completion and shutdown paths are substantive support. They do
not prove restoration of unrelated host devices or every virtual peripheral.

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

These are complementary observations, not yet a complete bidirectional
protocol mapping. The firmware branch consumes a host-reported exception;
the Linux report describes an event received from firmware. Before assigning
identical semantics, trace the producer, queue direction, framing, and state on
both sides. A matching number alone cannot establish that Linux should call an
equivalent recovery operation, or that doing so would repair
[the reported post-resume desynchronization](https://github.com/t2linux/kernel/issues/24).

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

Apple's [IOMessage definitions](https://github.com/apple-oss-distributions/xnu/blob/main/iokit/IOKit/IOMessage.h)
identify the two notification constants. The binary analysis supplies the ANS
mapping. These are ordinary-sleep negotiation and cancellation; an S4-specific
opcode and complete hibernate sequence have not been recovered.

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
[storage research](research/boot-and-storage.md).

The SEP transport examined in the Linux experiments had probe/remove paths
but no driver PM or shutdown callbacks. Generic PCI PM may or may not be
sufficient; this requires endpoint and queue-lifetime evidence. The inactive
control reproduced the leading failures without active SEP transport, so the
missing callbacks are not an established cause of those failures.

## PCIe and peripheral lifecycle

`AppleEmbeddedPCIeUpLinkMgmt` tracks function D-states, link L-states, LTSSM,
LTR, PERST relay, and S0 deassertion deadlines. It coordinates SMC and reset
callbacks and waits for link/PHY readiness. `AppleEmbeddedPCIE` adds port
quiesce/resume, deep-sleep entry/exit, refclock gating, endpoint reset, and
link-failure handling. Four successful host callbacks cannot prove this shared
link state machine completed.

Bridge audio saves/restores registers and has shutdown handling. AOP audio
has low-power microphone states. Multitouch has reset, auto-suspend, and
power-state messaging; J152f's SPI device has its own clock/reset sequence.
Camera/ISP, display/media, USB PHYs, and biometric hardware have separate power
policies. Watchdog code includes AP/system/userspace monitoring and an extended
quiesce watchdog, so a non-return can also involve firmware timeout enforcement.

These dependencies define [post-wake acceptance](investigation-guide.md).
They do not make every enumerated driver a suspect in each failure.
