# Investigation guide

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
| Does incoming VHCI `0x50` correspond to the firmware's host-exception branch? | Producer and consumer, queue direction, complete framing, and controller state |
| What completes SMC quiesce/resume? | Paired notifications, acknowledgements, and decoded completion fields |
| Which component requested wake? | PMGR source ID/name/flags plus observed wake event |
| Can a late completion poison the next transition? | Queue generation, pending work, drain outcome, and subsequent command ownership |
| What survives hibernate? | Per-IOP RTBuddy policy plus ANS/SEP/xART reconstruction chronology |
| How do host ordering constraints interleave? | A board-matched trace across SMC, graphics, T2 root port, and physical USB |

The first question is not answered by copying a firmware-side recovery call
into a Linux host handler. The two sides can assign different meanings to the
same numeric value.

## Treat hibernate as a complete chain

Account separately for image discovery, host ANS2 image I/O, platform S4 entry,
T2-internal ANS notification/shutdown, BCE/VHCI reconstruction, SEP endpoint
state, xART clients, and SMC reconciliation. Then check the restored host and
peripherals. Advertising `disk` or successfully writing an image qualifies
only a small part of that chain.

The ordinary ANS `0x309`/`0x30a` pair is decoded. Its S4 placement, a complete
S4-specific call graph, remaining SMC payload meanings, and PMGR routing
selector names remain open.

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

Extract the relevant message body and configuration facts before sharing a
report. Preserve the relationship among events and their relative timing.
A small reviewed excerpt is more useful than a full journal whose unrelated
content obscures the transition.
