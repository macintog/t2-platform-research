# Research coverage and remaining evidence

This is a dated map of examined questions, not a hardware support matrix.
Scope: bridgeOS `23P6068`, with build and board exceptions in the linked
chapters. Coverage reviewed on 2026-09-18.

“Bounded static analysis complete” means the retained analysis reached its
stated boundary. It does not mean the driver is implemented, safe, or runtime-qualified.
Missing inputs and qualification remain explicit below. A listed next measurement
does not authorize a reset, firmware write, or disruptive hardware experiment.

Generated from [research-map.json](../../catalog/research-map.json).

| Disposition | Examined areas |
| --- | ---: |
| Bounded static analysis complete | 17 |
| Missing artifact or input | 12 |
| Runtime evidence needed | 6 |
| Physical qualification needed | 2 |
| Qualification decision needed | 1 |

<a id="p1"></a>

## P1: Sixteen-board BridgeOS policy

Bounded static analysis complete.

for bridgeOS `23P6068`; revisit only for another signed build or a newly identified field.

Read: [Board configurations](board-configurations.md), [Platform architecture](pci-services-and-dma.md).

<a id="p2"></a>

## P2: J152f host boundary and APP7777 applicability

Bounded static analysis complete.

for provider selection on J152f.

Read: [Dual-GPU graphics: gmux, panel timing, and VFCT](../graphics/gmux-panel-and-vfct.md), [Host ACPI and graphics coordination](../graphics/acpi-and-gpu-ownership.md), [Board configurations](board-configurations.md), [Platform architecture](pci-services-and-dma.md).

<a id="p3"></a>

## P3: Host boundary on the other 15 boards

Missing artifact or input.

sanitized board-indexed ACPI/PCI captures.

Read: [Board configurations](board-configurations.md), [Platform architecture](pci-services-and-dma.md).

<a id="p4"></a>

## P4: Shared upstream PCIe and DART

Bounded static analysis complete.

for the static reset boundary. A cross-function quiesce/invalidate/reattach coordinator is implementation work, and any shared reset remains controlled; neither is an unperformed reversing lead.

Read: [Platform architecture](pci-services-and-dma.md#reset-and-queue-boundaries), [Sleep, wake, and hibernate](../power/sleep-wake-and-hibernate.md#bce-state-preservation).

<a id="p5"></a>

## P5: Remote diagnostics and paired attribution

Missing artifact or input.

one clock-correlated host plus bridgeOS transition capture.

Read: [Investigation guide](../method/investigation-guide.md#correlate-bridgeos-postmortems), [Platform architecture](pci-services-and-dma.md#peripherals-and-diagnostics).

<a id="p6"></a>

## P6: Watchdog, panic, and crash recovery

Missing artifact or input.

paired crash/watchdog records from the same transition.

Read: [Investigation guide](../method/investigation-guide.md#correlate-bridgeos-postmortems), [Platform architecture](pci-services-and-dma.md#peripherals-and-diagnostics).

<a id="p7"></a>

## P7: AppleSMC and PMGR completion/wake fabric

Missing artifact or input.

typed consumers for the remaining event selectors and a caller or symbolized table that names the PMGR routing values. The retained dispatcher, consumer, table, and literal searches exhausted their direct edges; bytes 0-3 cannot supply status because this dispatcher never reads them.

Read: [Sleep, wake, and hibernate](../power/sleep-wake-and-hibernate.md), [Suspend observations](../power/linux-suspend-observations.md), [SMC notifications, charging, and USB-PD](../smc/notifications-and-usb-pd.md), [Sleep, wake, and hibernate](../power/sleep-wake-and-hibernate.md#wake-aggregation-and-smc).

<a id="p8"></a>

## P8: BCE ordinary sleep selection

Bounded static analysis complete.

do not conflate it with hibernate or controller acceptance.

Read: [Platform architecture](pci-services-and-dma.md#reset-and-queue-boundaries), [Sleep, wake, and hibernate](../power/sleep-wake-and-hibernate.md#bce-state-preservation), [Sleep, wake, and hibernate](../power/sleep-wake-and-hibernate.md), [Suspend observations](../power/linux-suspend-observations.md).

<a id="p9"></a>

## P9: VHCI, internal USB, reset, and wake

Bounded static analysis complete.

for the static state/reset map. Adding and testing a VHCI epoch plus BCE-function quarantine/rebuild is off-device implementation work, not outstanding firmware analysis; shared PERST remains outside the VHCI owner.

Read: [Platform architecture](pci-services-and-dma.md#reset-and-queue-boundaries), [Sleep, wake, and hibernate](../power/sleep-wake-and-hibernate.md#bce-state-preservation).

<a id="p10"></a>

## P10: Hibernate as a whole chain

Qualification decision needed.

any S4 qualification requires a recovery-aware, controlled session after static dependency review.

Read: [Sleep, wake, and hibernate](../power/sleep-wake-and-hibernate.md), [Suspend observations](../power/linux-suspend-observations.md).

<a id="s1"></a>

## S1: Host ANS2/root storage

Bounded static analysis complete.

for the host/T2 controller and typed-command boundary. Any new health UI can use the already typed generic NVMe interfaces; firmware update and hibernate qualification are separate implementation/runtime projects, not a static raw-tunnel lead.

Read: [Boot and persistent storage](../storage/sep-persistence-and-nvme.md), [Sleep, wake, and hibernate](../power/sleep-wake-and-hibernate.md#ans-ordinary-sleep-and-cancellation).

<a id="s2"></a>

## S2: BridgeOS internal ANS/NVMe and xART

Bounded static analysis complete.

for the transport boundary; creator recovery is a separate vendor workflow.

Read: [Boot and persistent storage](../storage/sep-persistence-and-nvme.md), [Sleep, wake, and hibernate](../power/sleep-wake-and-hibernate.md#ans-ordinary-sleep-and-cancellation).

<a id="s3"></a>

## S3: SEP services beyond biometrics

Bounded static analysis complete.

for owner, ordering, and causal relevance. Endpoint-specific hold/abort/restart support is protocol implementation work and requires per-service acceptance evidence; it is not a generic PM callback left to discover in the reviewed Linux driver.

Read: [SEP architecture](../sep/services-and-mailboxes.md), [Identity and authorization](../sep/aks-identity-and-authorization.md), [23P2048 identity-create version 4 layout](../sep/aks-create-v4-j214k.md), [Sleep, wake, and hibernate](../power/sleep-wake-and-hibernate.md), [Suspend observations](../power/linux-suspend-observations.md).

<a id="s4"></a>

## S4: Touch ID lifecycle

Bounded static analysis complete.

for compatibility discovery; track productization separately.

Read: [Fingerprint lifecycle](../sep/fingerprint-lifecycle.md), [Fingerprint integration contracts](../sep/fingerprint-integration.md), [Linux integration of SEP identity](../sep/linux-integration.md).

<a id="s5"></a>

## S5: Boot and EFI policy

Bounded static analysis complete.

for the feasible writer, threshold, and direct fallback graph. Resolving the unnamed selectors, predicates, or backend requires a symbolized sibling or controlled trace; another string/direct-branch scan cannot supply them.

Read: [iBoot policy, firmware update, and recovery](../boot/iboot-firmware-update-and-recovery.md), [Boot and distribution integration](../boot/linux-boot-and-updates.md).

<a id="s6"></a>

## S6: Firmware update, erase, and device-mode recovery

Bounded static analysis complete.

for the retained static transaction graph. Exact return-to-original, fail-forward, or recovery-mode selection requires a matched persisted checkpoint/NVRAM snapshot across failure; update execution was not part of this analysis.

Read: [iBoot policy, firmware update, and recovery](../boot/iboot-firmware-update-and-recovery.md), [Boot and distribution integration](../boot/linux-boot-and-updates.md).

<a id="g1"></a>

## G1: Intel panel, EDID, and MacEFI sequencing

Bounded static analysis complete.

for panel timing; lane count and link rate belong to the route/active-link measurement boundary.

Read: [Dual-GPU graphics: gmux, panel timing, and VFCT](../graphics/gmux-panel-and-vfct.md), [Host ACPI and graphics coordination](../graphics/acpi-and-gpu-ownership.md).

<a id="g2"></a>

## G2: gmux ownership and switch transaction

Missing artifact or input.

a gmux/SMC register definition, board-level rail map, or controlled correlation trace that gives port `0x58` device semantics. Exhaustive command/caller/readback review found only writes. The prepare/switch/validate/abort transaction is now implementation design and remains separate from that missing meaning.

Read: [Dual-GPU graphics: gmux, panel timing, and VFCT](../graphics/gmux-panel-and-vfct.md), [Host ACPI and graphics coordination](../graphics/acpi-and-gpu-ownership.md).

<a id="g3"></a>

## G3: AMD/HDA/root-port power, reset, and runtime switch

Physical qualification needed.

require a validated abort path and known recovery route before power, reset, switch, or suspend tests.

Read: [Dual-GPU graphics: gmux, panel timing, and VFCT](../graphics/gmux-panel-and-vfct.md), [Host ACPI and graphics coordination](../graphics/acpi-and-gpu-ownership.md).

<a id="g4"></a>

## G4: Bridge-audio endpoint state and PM revalidation

Bounded static analysis complete.

for ownership, negative replay, and defect discovery. Implementation remains blocked on a safe client-publication protocol, reverse-order SQ/CQ/DMA unwind, IRQ-dispatch quiescence, owned draining of both dynamic work classes, failure injection, and concurrent PM/shutdown/IRQ/work tests before build and hardware qualification.

Read: [Bridge audio: endpoint state and playback clock](../audio/bridge-audio-state-and-clock.md).

<a id="g5"></a>

## G5: Playback clock, codec, DSP, jack, and speaker protection

Bounded static analysis complete.

for static framing and the missing Linux field. Parser/pointer integration is implementation work; timestamp units, simultaneous-direction sharing, and symptom attribution require a matched runtime trace and remain runtime qualification, not static guesses.

Read: [Bridge audio: endpoint state and playback clock](../audio/bridge-audio-state-and-clock.md).

<a id="g6"></a>

## G6: AOP audio and voice trigger

Bounded static analysis complete.

for the retained static controller and host packet paths. Establishing timestamp units/byte-count relation requires the producer-side timebase contract or matched trace; default enablement is a product decision.

Read: [AOP audio and voice trigger](../audio/aop-voice-trigger.md).

<a id="g7"></a>

## G7: AppleSMC charging and thermal policy

Missing artifact or input.

runtime `getKeyInfo` output or the producer-side key table for declared types, plus typed consumers for remaining event selectors. Host call-site, imported-accessor, serializer, and raw-key scans exhausted the retained static scale/layout evidence; no write is justified.

Read: [SMC notifications, charging, and USB-PD](../smc/notifications-and-usb-pd.md), [Sleep, wake, and hibernate](../power/sleep-wake-and-hibernate.md#wake-aggregation-and-smc).

<a id="g8"></a>

## G8: Battery/charging symptom

Runtime evidence needed.

next evidence is a bounded, board-specific event/key/USB-PD trace, not a policy write.

Read: [SMC notifications, charging, and USB-PD](../smc/notifications-and-usb-pd.md), [Sleep, wake, and hibernate](../power/sleep-wake-and-hibernate.md#wake-aggregation-and-smc).

<a id="g9"></a>

## G9: AOP sensors and timesync

Missing artifact or input.

the AOP ready/service assignment plus one producer-side accel/gyro/pressure sample and calibration path tied to the recovered dynamic interface and timestamp envelope. Host-side executable analysis is complete; cross-generation endpoint tables cannot fill the producer edge.

Read: [AOP and SPU sensor properties and time](../sensors/aop-spu-samples-and-time.md), [Sleep, wake, and hibernate](../power/sleep-wake-and-hibernate.md#aop-sensor-time-and-retention).

<a id="i1"></a>

## I1: HIDSPI updater, reset policy, and report 0x7e

Bounded static analysis complete.

for declared structure; counter semantics need a read-only sample.

Read: [HID input, HIDSPI, and multitouch](../input/hid-multitouch.md).

<a id="i2"></a>

## I2: Multitouch, Force Touch, palm, and report bodies

Missing artifact or input.

the build-matched `MultitouchHID.plugin` or equivalent user-client consumer that maps admitted IDs to lengths and fields. The retained AFU caller/copy lane is complete and cannot supply that host-side edge; do not reuse internal layouts as contact fields.

Read: [HID input, HIDSPI, and multitouch](../input/hid-multitouch.md).

<a id="i3"></a>

## I3: Touch Bar display personality

Missing artifact or input.

the bridgeOS USB gadget/personality binary that selects and initializes configuration 2, plus its 856-byte HID descriptor or an already retained macOS descriptor capture. The named component and broad identity searches failed; live configuration switching remains controlled.

Read: [Touch Bar USB configuration and DRM binding](../input/touch-bar-usb-drm.md).

<a id="i4"></a>

## I4: Lid-angle sensor (LAS)

Runtime evidence needed.

any further work requires controlled stimulus-correlated report-1 sampling or a validated parser for other reports; do not send output report 6.

Read: [Lid-angle sensor (LAS)](../sensors/las-lid-angle.md).

<a id="i5"></a>

## I5: Camera controls, exposure, privacy, teardown, and reopen

Missing artifact or input.

the selector-7 dispatch-table edge into the recovered gated routine, the `AppleUVCCamera` policy-to-property-0 caller, and an identified privacy/LED controller or a trace establishing that relationship. `SEPCameraDisable` belongs to SEP metadata and does not prove camera privacy ownership; no XU request is valid because the bitmap enables none.

Read: [Camera ISP exposure and UVC controls](../camera/isp-exposure-and-uvc.md), [Linux compatibility map](linux-support.md#current-j152f-checkpoint).

<a id="i6"></a>

## I6: T2 media encoder

Bounded static analysis complete.

for retained static command `0x02` and callback `0x0b`. Further confidence requires board-scoped runtime qualification and negative/safety testing, not more corpus searching.

Read: [AVE video encoder transport](../media/ave-video-encoder.md).

<a id="i7"></a>

## I7: Wi-Fi

Runtime evidence needed.

require a board-bound firmware/NVRAM/control trace to move beyond symptom.

Read: [Linux compatibility map](linux-support.md#current-j152f-checkpoint).

<a id="i8"></a>

## I8: Bluetooth and AOP control

Runtime evidence needed.

non-disruptively confirm dynamic-service presence and correlate power requests with host HCI lifecycle before any reset hypothesis.

Read: [Bluetooth Marconi power control](../network/bluetooth-marconi.md), [Linux compatibility map](linux-support.md#current-j152f-checkpoint).

<a id="i9"></a>

## I9: USB-C and Thunderbolt

Physical qualification needed.

controlled devices and a recovery-aware hotplug/wake matrix after static review of the helper.

Read: [Linux compatibility map](linux-support.md#current-j152f-checkpoint), [Sleep, wake, and hibernate](../power/sleep-wake-and-hibernate.md#pcie-and-peripheral-lifecycle).

<a id="i10"></a>

## I10: Desktop Ethernet

Missing artifact or input.

the J185/J185f AOP-I2C application/service binary or typed message trace, and J160 register definitions if implementation proceeds. All-board and executable/class searches found topology but no AOP owner or declared user-client implementation.

Read: [Desktop Ethernet sideband management](../network/ethernet-sideband.md).

<a id="i11"></a>

## I11: RTC and persistent time

Missing artifact or input.

the host-side provider/helper implementation that defines transport, epoch/unit conversion, and alarms, or a typed comparator trace. DeviceTree, RTC-component, iBoot, and experimental-driver review found no such contract; no RTC write is justified.

Read: [RTC persistent offset and PMU policy](../sensors/rtc-persistent-offset.md).

<a id="i12"></a>

## I12: Physical xHCI outside BCE

Runtime evidence needed.

trace exact PCI/platform ordering only after a non-disruptive instrumentation plan.

Read: [Sleep, wake, and hibernate](../power/sleep-wake-and-hibernate.md#pcie-and-peripheral-lifecycle).

<a id="i13"></a>

## I13: Internal keyboard and backlight

Runtime evidence needed.

collect board-bound IDs and post-transition acceptance only when a safe platform transition exists.

Read: [Linux compatibility map](linux-support.md#current-j152f-checkpoint), [HID input, HIDSPI, and multitouch](../input/hid-multitouch.md).
