# Investigation guide

[Research map](../README.md) · [Evidence catalog](../../catalog/README.md)

Choose a specific board, transition, and failed contract. The existing evidence
supports targeted tracing before another broad sequence of sleep attempts.

## Establish the host boundary

For boards beyond J152f, collect the relevant ACPI device descriptions and PCI
function relationships. Identify the T2 root port, `_PRW`, `_PS0`, `_PS3`,
`_DSM` dependencies, and whether an APP7777 provider exists. Report selected
properties rather than a complete machine inventory.

For J152f, trace the Linux path through `RP17`, `ANS2`, `IOBC`, `SEPM`, and
`ADIO`. Compare the actual per-function order and D-states with the recovered
ACPI dependency property. Keep graphics and physical USB events in the same
time base.

## Resolve the next protocol questions

| Question | Discriminating evidence |
| --- | --- |
| Which producer emitted the retained incoming VHCI `0x50`? | Outer BCE completion and queue ID, direction, all 16 VHCI bytes, producer call site, and controller state |
| What completes SMC quiesce/resume? | Paired notifications, acknowledgements, and decoded completion fields |
| Which component requested wake? | PMGR source ID/name/flags plus observed wake event |
| Can a late completion poison the next transition? | BCE slot generation, a proposed VHCI epoch, pending work, drain outcome, and subsequent command ownership |
| What survives hibernate? | Per-IOP RTBuddy policy plus ANS/SEP/xART reconstruction chronology |
| How do host ordering constraints interleave? | A board-matched trace across SMC, graphics, T2 root port, and physical USB |
| Did bridgeOS crash, watchdog, or only lose transport? | Clock-correlated host trace plus unified log, panic, stackshot, watchdog tailspin, or crash report from the same transition |
| Which AOP sensor contract is in use? | Endpoint discovery and version, property selector and size, report layout, calibration version/format and any integrity fields, plus paired AOP/Linux timestamps |

The September 2026 incoming-`0x50` snapshot did not retain the outer queue or
completion record, so it cannot answer the first question. Apple firmware
consumes host-reported event `0x50` as an exception. Linux separately reserves
BCE management opcode `0x50` for an unused memory-queue property command, while
its VHCI enum defines no base command `0x50`. Numeric equality across those
framing and direction domains is not protocol equality. Do not copy the
firmware-side recovery call into a Linux event handler.

The same provenance rule applies to the delayed
`data URB unexpected completion state=7` retained in September 2026. It is
consistent with stale or displaced accounting, but it does not prove that
VHCI caused the following transition failure. Preserve the queue generation,
completion index, pending URB, and surrounding transition before assigning a
cause.

## Limit recovery to the confirmed fault scope

For a future recovery implementation, keep a valid endpoint stall local to the
endpoint. Rebuild one virtual USB
child only when its port or device state is the failed boundary. A command
reply mismatch, repeated cancellation timeout, completion-index mismatch, or
completion from a retired queue generation is controller-wide evidence: stop
new URBs, cancel waiters, drain work, remove the HCD, stop DMA, and rebuild the
complete BCE/VHCI queue graph under a new epoch.

Escalate beyond the BCE function only when the local rebuild fails or the
evidence names the shared link or DART. A shared-link reset must coordinate
ANS2, BCE, SEP, and audio, then verify streams `1/0/2/3` before accepting any
client. Limit the attempt count and report the failed acceptance gate instead
of looping reset or queue registration.

## Correlate bridgeOS postmortems

Remote diagnostics are a post-event path, not a reset API. If transport
returns after a failure, a constrained sysdiagnose can supply unified logs,
panics, stackshots, watchdog tailspins, and crash reports. Capture the clocks
needed to relate those records to Linux:

1. Record Linux `CLOCK_REALTIME`, `CLOCK_BOOTTIME`, and the current boot scope
   immediately before and after the transition.
2. Bracket the RemoteXPC request with the same two Linux clocks.
3. Preserve each bridgeOS record's UTC timestamp, numeric time, and boot scope
   privately. Do not publish the boot identifier.
4. Correlate on a transaction visible to both sides, such as a BCE save or
   restore request and reply. Do not use archive completion time as event time.
5. Report the clock-offset interval and its width. Split the timeline if
   `realtime - boottime` changes instead of forcing one offset.
6. Keep event time, crash-report creation time, and archive collection time as
   separate fields.

A bridgeOS boot can span multiple Linux boots. An unavailable diagnostic path
can mean transport loss rather than daemon failure, so absence of a retrieved
archive is not evidence that bridgeOS stayed healthy.

## Treat hibernate as a complete chain

Account separately for image discovery, host ANS2 image I/O, platform S4 entry,
T2-internal ANS notification/shutdown, BCE/VHCI reconstruction, SEP endpoint
state, xART clients, and SMC reconciliation. Then check the restored host and
peripherals. Advertising `disk` or successfully writing an image qualifies
only a small part of that chain.

The ordinary ANS `0x309`/`0x30a` pair is decoded. Its S4 placement, a complete
S4-specific call graph, remaining SMC payload meanings, and PMGR routing
selector names remain open.

The AOP accel/gyro strings resolve service presence but not a Linux wire
contract. The separate lid-angle sensor (LAS, USB `05ac:8104`) has a strongly
inferred `las`/HID-relay owner and one recorded report-1 read in whole
degrees; it does not supply the accel/gyro ABI. Before proposing an IIO
interface for those sensors, recover one read-only property and report pair
with exact endpoint discovery, version, sizes, calibration checks, timestamp
units, and discontinuity behavior. Do not derive those values from another
Apple AOP generation's endpoint table.

## Report a usable wake

A returning kernel callback is not enough. Record whether the internal display,
keyboard, trackpad, storage I/O, audio, camera, Touch Bar where present, and
network access returned. Include external displays or desktop Ethernet when
those devices belong to the selected configuration. Check for delayed errors
and whether a later transition still works.

Separate deep sleep, s2idle, hibernate, and `pm_test` stages in every result.
Record the kernel and driver revisions, bridgeOS build when established, GPU
policy, attached peripherals, power source, and the exact test boundary.
Use relative times within the experiment. Report unknown fields as unknown;
do not infer firmware version from a downloaded analysis artifact.

## Contribute evidence without machine identity

Model and board identifiers, firmware builds, source revisions, PCI device IDs,
and protocol constants make results reproducible. Hostnames, account names,
network addresses, serial numbers, machine IDs, filesystem UUIDs, and unrelated
service state do not explain these mechanisms.

Name the signed artifact, byte length, SHA-256 digest, source revision, and the
offset coordinate system. For the portable kernelcache, distinguish the
40,058,908-byte universal-wrapped loader input from its 40,058,880-byte body.
For AOP, state whether an offset addresses the signed IM4P or the payload. For
split dyld caches, report virtual addresses rather than pretending they are
offsets in the main cache file. See [Artifacts and
method](platform-artifacts.md) for the reviewed identities and anchors.

Extract the relevant message body and configuration facts before sharing a
report. Preserve the relationship among events and their relative timing.
A small reviewed excerpt is more useful than a full journal whose unrelated
content obscures the transition.
