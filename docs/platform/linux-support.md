# Linux compatibility map

[Research map](../README.md) · [Evidence catalog](../../catalog/README.md)

Linux can use much of an Apple T2 Mac, but support is split among mainline
drivers, the t2linux patch stack, staging modules, distribution firmware, and
userspace policy. A device working on one installation does not mean that its
driver is upstream, complete across models, or ready for suspend and recovery.

This map records the public state on September 18, 2026. It uses the
[t2linux state page](https://github.com/t2linux/wiki/blob/5e79e6ed1481571df10d86c13ee35d5cbf5ef1ec/docs/state.md),
[t2linux patch stack](https://github.com/t2linux/linux-t2-patches/tree/794069f7015e25d62da420e2748daaac0813cedc),
and [t2bce](https://github.com/deqrocks/t2bce/tree/a973d53c8278e9db5ff8314b816d6880309ed39e)
at the linked revisions. The J152f observations below come from one
MacBookPro16,1 running kernel `7.2.6-arch2-Watanare-T2-2-t2`. They are a
board-specific checkpoint, not a family-wide qualification. Sanitized capture
`j152f-platform-inventory-20260918` is retained privately; raw host identifiers
and journals are not part of the public evidence.

The current-source classification was refreshed against
[upstream Linux `5dd1818`](https://github.com/torvalds/linux/tree/5dd1818b15d98d4a20806cd00b1b40320b06004f),
[KAiT2EN `c38320d`](https://github.com/kaiT2en/KaiT2en-Fedora/tree/c38320d41f67e84f936dabe978cc4f8611587c24),
and [tiny-dfr `eb711c8`](https://github.com/AsahiLinux/tiny-dfr/tree/eb711c87fcbddda67be3fd5ff45385b139e8fb34)
on the same date. Experimental forks are named as such; their existence does
not establish mainline acceptance or qualification across the T2 family.

## How to read the map

The T2 relationship matters when choosing what to reverse engineer:

- **Direct** means the host-visible device or service terminates in the T2,
  its firmware, or its internal peripheral fabric.
- **Shared** means the T2 participates in policy, reset, power, or routing with
  a host controller.
- **Adjacent** means the device is primarily host-side. T2 artifacts can still
  explain boot or power policy, but they are not the device firmware.
- **Unproven** means the public and retained evidence does not yet establish a
  T2 role. The gap may still be real, but T2 reverse engineering is not yet the
  justified first step.

"Working" below means that a useful path exists. It does not imply upstream
support, full feature parity, reliable recovery, or coverage of all 16 boards.

## Support and gap summary

| Surface | Current Linux path | Main gap | T2 relationship |
| --- | --- | --- | --- |
| Board identity and policy | Installers and the t2linux patch stack carry model-specific choices | The maintained board matrix records firmware differences across 16 production boards, but they are not yet joined to per-surface Linux feature, suspend, and recovery qualification | Direct and shared |
| Boot and EFI | Linux boots after the Startup Security Utility permits it; T2 distributions carry model-specific kernel and installer work | Apple Secure Boot does not accept the ordinary shim path; generic installers and EFI runtime behavior remain fragile | Shared |
| Host storage | ANS2 uses the mainline NVMe driver and provides normal root-disk I/O | Apple health, admin, firmware-update, error, and hibernate-restoration contracts remain incomplete; APFS/PFK is a separate filesystem and key-management boundary | Direct and shared |
| BCE and VHCI | `t2bce_core`, DMA, and VHCI expose the T2 peripheral fabric | The replacement stack is not in mainline; system events, reset recovery, queue generations, and upstreamable interfaces remain incomplete | Direct |
| Keyboard and backlight | Internal input works through BCE/VHCI and t2linux HID patches | Alternate device IDs still appear by model; one current report covers `05ac:0277` on J223 | Direct |
| Trackpad and Force Touch | Multitouch input works with the t2linux HID patches | Force Touch, palm rejection, pressure semantics, and actuator behavior are not implemented as a complete protocol | Direct |
| Touch Bar | Keyboard, backlight, and display drivers are mainline; tiny-dfr is a maintained renderer that switches the device from configuration 1 through 0 to 2 | BCE remains out of tree, and configuration switching plus boot/resume reprobe remain fragile on reported systems | Direct |
| Camera and ISP | The UVC camera runs through BCE/VHCI; the live J152f device advertises NV12 and YUYV at 1280x720 and 640x480 | Transport is not in mainline; the descriptor exposes no standard CT/PU controls and enables no XU selector, so AppleM8/ISP policy, startup exposure, privacy LED ownership, and recovery need protocol work | Direct |
| Audio, microphones, and amps | `t2bce_audio`, ALSA UCM, and distribution profiles expose speakers, headphones, and microphones | The driver is not in mainline; playback clock feedback, DSP, beamforming, calibration, jack policy, board topology, and amp/speaker-protection policy remain incomplete or unqualified | Direct |
| T2 media encoder | An experimental out-of-tree `t2bce_ave` V4L2 mem2mem driver and userspace service exist; one command/callback path now matches build-matched bridgeOS queue, daemon, H9, and AppleAVE2 owners | Other commands, codec/format coverage, malformed-buffer safety, board qualification, recovery, and upstream API status remain unqualified | Direct |
| Touch ID and biometric lifecycle | Current public KAiT2EN support matches identities enrolled by macOS and explicitly does not enroll; this project's separate private evidence demonstrates native creation, enrollment, matching, deletion, and persistence on two configurations | Public native enrollment/deletion and packaging remain incomplete; protocol versions, sensor power, AOP dependencies, recovery, and policy still vary by board and bridgeOS build | Direct |
| SMC, fans, and thermals | The t2linux AppleSMC series and KAiT2EN's narrower experimental `t2smc` expose overlapping telemetry and controls | Both remain out of tree; key types, permissions, failsafes, thermal zones, notification contracts, and a stable family-wide ABI remain incomplete | Direct |
| Battery and charging | ACPI Smart Battery exposes battery telemetry; AppleSMC exposes a charge-limit control | A current A2141 / 16-inch 2019 report describes AC-present discharge until cable replug; charger, SMC, and USB-PD ownership are not yet separated | Shared |
| AOP sensors and AOP audio | Ambient light is usable through BCE/VHCI; signed firmware separately exposes AOP accelerometer, gyroscope, pressure, and AOP-audio/voice-trigger services, with no Linux owner for those AOP services | Sensor calibration, timestamps, wake behavior, and the distinct low-power microphone, retained-history, and control contracts lack public Linux protocols; a live USB HID sensor must not be assumed to be the AOP host route | Direct for the signed AOP services; the live USB path is separately established |
| Wi-Fi | `brcmfmac` works after installing Apple firmware and board data | Firmware extraction and NVRAM selection remain distribution work; the current J152f observation also has a P2P creation failure | Adjacent |
| Bluetooth | The Broadcom HCI path exists with Apple firmware and a t2linux advertising-bit quirk | Firmware-name selection, baud-rate setup, reset behavior, and Wi-Fi coexistence remain unreliable on some configurations | Adjacent or shared; exact reset ownership is open |
| GPU, display, backlight, and gmux | Intel display and gmux backlight can work; t2linux carries quirks and KAiT2EN has experimental `t2gmux`/`t2bdrm` forks | KAiT2EN's runtime-PM application is MacBookPro15,1-only, not J152f qualification; cold boot, switching, AMD reset/power, ownership, HDA/root-port coupling, and AppleMuxControl2 sequencing remain incomplete | Shared and adjacent |
| USB, USB-C, and Thunderbolt | Ordinary paths use host controllers and mainline drivers; experimental `t2thunderbolt` adds device links for PM ordering | The helper does not qualify orientation, DisplayPort alternate mode, hotplug, native-port tunneling, DMA protection, or wake | Adjacent or shared |
| T2 internal USB and device modes | BCE/VHCI carries internal USB-class peripherals; Apple restore and diagnostics also use device-mode USB services | PHY and port power, role switching, charger interest, remote wake, recovery enumeration, and failure behavior lack a public end-to-end Linux contract | Direct |
| DMA isolation and DART policy | Linux uses host IOMMU facilities where exposed; the T2 firmware assigns separate DART streams to its four PCI functions | The relationship among T2-side DART policy, host DMA protection, recovery, and function reset is not documented as a Linux contract | Direct and shared |
| Desktop Ethernet | Host-visible packet traffic uses ordinary drivers; J160 additionally has a recovered T2-side I²C/LOM management path | J160 register semantics and suspend/wake remain unqualified; J185/J185f instead use an unresolved AOP-I²C owner | Adjacent or shared; packet traversal through T2 is unproven |
| RTC and persistent time | An experimental out-of-tree SMC-key RTC exists; all 16 retained board trees share a `pmu,d2449` RTC-offset policy | Host helper transport, units and epoch, alarms, safe NVRAM persistence, and Linux board coverage remain unqualified | Direct policy; host ABI unresolved |
| SEP services beyond biometrics | KAiT2EN carries an experimental `t2sep` transport that is explicitly non-shipped, manual, and has no autoload/device table; this project documents several routes and storage clients | General AKS, xART, gigalocker, attestation, reset, persistence, and ownership are not stable Linux APIs | Direct |
| Diagnostics, RemoteXPC, and BridgeXPC | Retained research maps read-only routes, and KAiT2EN's experimental maintained `t2-journal` collects BridgeOS logs | There is no integrated stable layer for paired-clock health, wake causes, panic/crash attribution, subsystem readiness, or recovery | Direct |
| Watchdog, panic, and crash recovery | Linux receives ordinary host watchdog and panic information, while the retained firmware exposes additional AP, system, userspace, and SMC panic paths | Timeout ownership, panic-doorbell handling, coredump retrieval, crash recovery, and safe forced-reset boundaries are not integrated | Direct and shared |
| Firmware update and recovery | Linux installations depend on preserving Apple firmware and recovery state and document manual ESP and partition precautions | Board selection, boot-policy publication, signed update state, diagnostics, and safe failure recovery lack a public end-to-end contract | Direct and shared |

The table deliberately separates poor Linux support from T2 ownership. Ordinary
Wi-Fi, GPU, and Thunderbolt data paths are not proven to traverse the T2. Their
useful T2 questions concern reset, power, boot, or board policy unless new
evidence establishes a stronger relationship.

## Current J152f checkpoint

The live MacBookPro16,1 shows how much of the machine depends on code that is
not upstream or not feature-complete:

| Observation | What it establishes | What it does not establish |
| --- | --- | --- |
| ANS2 `106b:2005` binds to the generic NVMe driver | Ordinary host storage is usable through the mainline NVMe path | Apple admin commands, health telemetry, firmware update, APFS/PFK, or hibernate restoration |
| BCE `106b:1801` uses `t2bce_core` 0.07 with DMA and VHCI | The non-mainline BCE stack is the active internal-peripheral transport | Upstream readiness or complete event/recovery semantics |
| SEP `106b:1802` uses `t2_sep_transport` from DKMS package `t2-sep-transport/0.1.0` | A Linux transport reaches the SEP function | A general supported SEP API or safe lifecycle for every service |
| Audio `106b:1803` uses `t2bce_audio` 0.02 | Speakers and an internal microphone are exposed to PipeWire | Playback, recording, DSP, jack, multichannel, or recovery quality; no stream was started during this inventory |
| BCE/VHCI enumerates camera, ALS, headset, keyboard, trackpad, Touch Bar, backlight, and sensor `05ac:8104` | BCE is a platform peripheral fabric, not a biometric-only transport | That every child is feature-complete or independently recoverable |
| The UVC camera advertises NV12 and YUYV at 1280x720 and 640x480 up to 30 fps | The device and media graph enumerate with those advertised modes | Image quality, privacy LED behavior, stream recovery, or current capture success; this inventory did not open a stream |
| ALS `05ac:8262` exports illuminance and color channels; lid-angle sensor `05ac:8104` exposes a 179-byte Sensors descriptor whose report 1 is Input, while two macOS clients and one bounded Linux observation successfully request Feature report 1 | One sensor path is usable; `8104` accepts a GET-only Feature query but still fails the generic rotation probe because its semantics differ, not because its descriptor or module is absent | Live update behavior, the other report IDs, and a safe Linux lid-angle ABI; no direct AOP route is established |
| The AppleSMC driver reports 1,164 keys, two fans, and 50 temperature entries and exposes fan, temperature, and charge-limit interfaces; ACPI Smart Battery separately exposes battery state | The T2 holds a rich platform-management interface | Stable names, types, permissions, thermal policy, or an upstream hwmon ABI |
| Wi-Fi carries the control connection, while P2P device creation fails with `-52` | Station mode works on this configuration and P2P does not initialize cleanly | A family-wide firmware or NVRAM cause |
| Bluetooth reaches a Broadcom controller but logs baud-rate failure and cannot find `brcm/BCM.hcd` | Firmware selection and setup are concrete investigation targets | That Bluetooth is universally unusable; the controller was soft-blocked during inventory |
| Intel owns the 3072x1920 internal panel; AMD exposes a duplicate panel without EDID or modes and lacks runtime PM | The known-good Intel-panel policy works while the AMD path retains visible defects | A complete gmux or AppleMuxControl2 chronology |
| Two Titan Ridge domains report user security, no IOMMU DMA protection, and missing tunneled-native-port links | The host exposes concrete Thunderbolt integration warnings | Hotplug, networking, display, or wake behavior; no device was attached during inventory |

A separate retained camera baseline, tagged `linux-baseline-20260915` at
source commit `07200dd1ed6b5725fad2afa26702d115cab5408e`, ran on J152f with
kernel `7.2.4-arch1-Watanare-T2-3-t2` and `t2bce_vhci` 0.02. NV12 and
YUYV at 1280x720 and 640x480 each delivered 120 of 120 frames with no short
frames or sequence gaps. All four runs took about 1.6 seconds to produce the
first frame and began with an almost-black frame before exposure settled. The
raw image bundle remains private; this summary preserves the reviewed
measurements without publishing image content or device metadata.

For descriptor details, see [Touch Bar USB configuration](../input/touch-bar-usb-drm.md)
and [Lid-angle sensor (LAS) reports](../sensors/las-lid-angle.md).

## Input, camera, and media protocols

- [HID input, HIDSPI, and multitouch](../input/hid-multitouch.md)
- [Camera ISP exposure and UVC controls](../camera/isp-exposure-and-uvc.md)
- [AVE video encoder transport](../media/ave-video-encoder.md)

## Audio, sensors, and SMC protocols

- [Bridge audio: endpoint state and playback clock](../audio/bridge-audio-state-and-clock.md)
- [AOP audio and voice trigger](../audio/aop-voice-trigger.md)
- [AOP and SPU sensor properties and time](../sensors/aop-spu-samples-and-time.md)
- [SMC notifications, charging, and USB-PD](../smc/notifications-and-usb-pd.md)

## Graphics and firmware boot policy

- [Dual-GPU graphics: gmux, panel timing, and VFCT](../graphics/gmux-panel-and-vfct.md)
- [iBoot policy, firmware update, and recovery](../boot/iboot-firmware-update-and-recovery.md)

## RTC and network control

- [RTC persistent offset and PMU policy](../sensors/rtc-persistent-offset.md)
- [Desktop Ethernet sideband management](../network/ethernet-sideband.md)
- [Bluetooth Marconi power control](../network/bluetooth-marconi.md)

## Retained firmware inputs

The signed bridgeOS 10.6 `23P6068` restore already used by this project
contains the principal inputs for several new investigations. These identifiers
let another researcher reproduce the work without redistributing Apple
firmware.

| Artifact | Bytes | SHA-256 | Best-supported next use |
| --- | ---: | --- | --- |
| `Firmware/AOP/aopfw-t8012aop.RELEASE.im4p` | 373,229 | `98fbbc65a9df38553642633ba61e10b8d47917b1a8796b310c53128efb7ca211` | Sensor services, timestamps, calibration, lid-angle service, distinct low-power/voice-trigger audio, and wake messages |
| `Firmware/J152F_InputDevice.im4p` | 676,764 | `f52ead1efb8c5497b1ddf7c40ebd8fccfe017794be12704c4ee08e862ace8424` | Determine which top-case, keyboard, and Touch Bar identities, reports, reset, recovery, and version paths it owns |
| `Firmware/J152f_Multitouch.im4p` | 89,811 | `1ce8a0dfc9e611ac262a93435f1be96c8c2c006ddb2722c76280817a7dbfe15a` | Pressure, palm, report, reset, and recovery semantics; correlate actuator behavior separately |
| `Firmware/MacEFI/J152F.RELEASE.im4p` | 8,388,633 | `f2d6ae5542ef43d1b604a3b65726d334943f1f4de1a62b165df4281275216295` | Boot policy, board selection, VBT provenance, EFI compatibility, and recovery handoff |
| `Firmware/all_flash/LLB.j152f.RELEASE.im4p` | 1,240,242 | `7f6a257756930a671199a150d3dc9d538dc042bae4ae96a1bf3a286dd08dfd6f` | Early boot, board policy, manifest validation, and recovery-state transitions |
| `Firmware/all_flash/iBoot.j152f.RELEASE.im4p` | 1,240,242 | `299c24cb28084bf16340af493e2b4f81a59e0b60e6a954c777eb8fd92e2e6433` | Host/T2 boot handoff, policy publication, diagnostics, and recovery paths |
| `Firmware/dfu/iBEC.j152f.RELEASE.im4p` | 1,240,242 | `0e012371eb7dd6e4a4952e021e59a242e6b3624d2f654fdf14ea8daed86f208f` | DFU/recovery state machine and board-specific bring-up |
| `Firmware/dfu/iBSS.j152f.RELEASE.im4p` | 1,240,242 | `713f7f07601a72339744a34c6696a8ce5831efc15a642f91efb0e5e8ecb83832` | DFU entry, manifest checks, and recovery sequencing |
| `094-92961-079.dmg` | 117,440,539 | `6860590952a17c0d955ebf36032a34c2cb5359182cc36448a5d671694faa4860` | Erase-time provisioning, diagnostics, and failure recovery |
| `094-92985-079.dmg` | 119,537,691 | `53aab6179ea7f623b9c7edc48ecbefd5e33faebd14c6494b81e520235a4a69a7` | Update-time firmware ownership, provisioning, and recovery services |
| `Firmware/all_flash/sep-firmware.j152f.RELEASE.im4p` | 4,182,270 | `bc21098b1c4fa98d20974e55ebeebdf219294caf07db3ab3af3db7882b60be92` | Non-biometric SEP routes, reset, persistence, xART shutdown, and hibernate boot |

The already documented system image, portable and desktop kernelcaches,
RecoveryOS kernel collections, `IOBufferCopyController`, `AppleMuxControl2`,
and `AppleEmbeddedOSSupportHost` remain useful inputs. The retained extraction
also contains `AppleUVCCamera`, `UVCCamera.framework`, `bridgeaudiod`,
`BridgeAudioConfig.plist`, `AppleM8CameraInterface`, `smcDiagnose`, AppleSMC,
and ANS/NVMe update code. Their presence establishes available comparator
implementations, not that a Linux path should copy their policy verbatim.

## Research and contribution order

The best next contributions are the ones with a concrete Linux symptom and a
matching retained comparator. The first two lanes are enabling work: they make
later protocol findings observable and keep board-specific policy out of
supposedly generic fixes.

1. **Sanitized diagnostics and wake/crash attribution.** Turn the retained
   RemoteXPC, BridgeXPC, SMC wake, watchdog, and crash-reporting knowledge into
   bounded read-only observability. This should distinguish a host timeout,
   T2 panic, IOP crash, and ordinary driver failure without requiring firmware
   redistribution.
2. **Board-policy matrix.** Keep the 16 signed production configurations tied
   to their kernelcache class, AOP children, input path, codec policy, display
   hardware, and power policy so that later fixes state their actual scope.
3. **Dual-GPU graphics, panel ownership, and gmux.** Treat graphics as an
   independent compatibility program, not only a suspend dependency. Reconcile
   ACPI, VFCT, MacEFI, VBT, AppleMuxControl2, Intel and AMD connector exposure,
   cold-boot initialization, switching, reset/reprobe, runtime power, and the
   coupled HDA/root-port sequence. Begin with a route-aware connector prototype
   and a control-flow reconstruction of the transition handlers around the
   decoded Config3 parser before attempting GPU power-off.
4. **Audio clock, endpoint state, and DSP.** Consume the recovered `sampleTime`
   playback feedback; prove endpoint allocation lifetime, then add read-only
   word-2/shared-structure revalidation and safe rebind rather than host GPR
   replay. Consume the recovered live/historic `SpuMCAPacket` framing and
   establish its producer-side timestamp unit before exposing timing; the
   controller range `0xc3000000`-`0xc3000007` and property `0xc9` are also
   bounded. Map codec topology, calibration, and jack behavior separately.
5. **AppleSMC, charging, and thermal policy.** Turn the large untyped key set
   into a board-scoped dictionary, recover notification selectors and payloads,
   define safe read/write policy, separate the ACPI battery and USB-PD paths,
   and modernize hwmon integration.
6. **AOP services.** Decode the signed `accel`, `gyro`, `pressure`, audio,
   lid-angle, calibration, timestamp, and wake contracts without conflating
   them with the distinct voice-trigger audio service or assuming that every
   live USB HID sensor is an AOP host route.
7. **Camera and VHCI lifecycle.** Extend the retained capture baseline with
   the recovered internal exposure-bias command, resolve its connections to caller
   policy and selector-7 dispatch, and recover privacy LED ownership. Qualify
   startup exposure, cancellation, reset, and model descriptors separately;
   do not invent a UVC selector where the bitmap enables none.
8. **T2 media encoding.** Use the recovered `AppleAVEBridge` queue ownership
   plus build-matched `aveserverd` command `0x02`, callback `0x0b`, H9, and
   `AppleAVE2` path as a bounded implementation contract. Qualify other
   commands, codecs, formats, malformed buffers, boards, and recovery
   separately before support claims.
9. **Bluetooth firmware selection and setup.** Treat this as a host/platform-
   adjacent investigation until reset ownership is proven. Explain the
   requested firmware name, board-specific blobs, baud-rate transition, and
   reset owner without disturbing working Wi-Fi station mode.
10. **Touch Bar configuration and reprobe.** Configuration 2 and its class-`0x10`
   bulk interface are confirmed by the descriptor. Qualify the userspace
   1-to-0-to-2 transition, DRM bind, and boot/resume reprobe as one bounded lifecycle.
11. **Lid-angle sensor (LAS).** USB `05ac:8104` identifies the device.
    The 52-byte USB and 179-byte HID descriptors are retained and hashed.
    The descriptor declares report 1 as
    Input, but two clients and one bounded Linux query prove Feature-report
    raw-degree decoding. Recover why the relay accepts the undeclared query,
    then qualify live update/error behavior and any output-report role before
    designing a lid-angle ABI. Do not force it through Linux's incompatible
    quaternion rotation path or assume an AOP relationship.
12. **Thunderbolt native-port and DMA policy.** Treat this as host/platform-
   adjacent unless a stronger T2 role is proven. Explain the missing device
   links and absent IOMMU protection before controlled hotplug qualification.
13. **ANS2 advanced functions.** Separate generic NVMe success from Apple admin,
    SMART, error, firmware, effaceable-storage, and hibernate paths. Treat
    APFS/PFK as a separate filesystem and key-management boundary.
14. **Boot, firmware update, and recovery.** Preserve the recovered packed
    failure counters, five-event recovery thresholds, one-time-command
    consumption, fallback commit order, and signed updater stages. Resolve the
    remaining stripped selector and predicate meanings only from a symbolized
    sibling or an authorized trace; do not infer them from names.
15. **Internal USB, DART, and reset boundaries.** Recover T2-side USB role and
    PHY transitions, per-function stream policy, and the distinction among a
    child reset, function reset, shared-link reset, and destructive recovery.

The [public audio clock report](https://github.com/t2linux/kernel/issues/28),
[audio open regression](https://github.com/t2linux/kernel/issues/20),
[charging report](https://github.com/t2linux/kernel/issues/26),
[alternate input-ID report](https://github.com/t2linux/kernel/issues/25), and
[Bluetooth report](https://github.com/t2linux/kernel/issues/23) are useful
starting symptoms. The separate
[Touch Bar boot-probe timeout](https://github.com/t2linux/wiki/issues/729)
also shows why initial enumeration, reconfiguration, and recovery need to be
treated as different lifecycle states. These remain configuration-specific
reports, not maintainer-confirmed root causes.

For audio, issue 20's reported null dereference on 7.1.5/7.1.6 was reported
fixed by affected users on 7.1.8 configurations; its separate transition
observations remain historical evidence. Issue 28 is the current MacBookPro16,1
and 16,2 playback-quality report. Neither issue proves the recovered
`sampleTime` omission is its cause.

Graphics has similarly distinct failure classes. The
[MacBookPro16,1 AMD resume report](https://github.com/t2linux/kernel/issues/21)
is a power-transition case, while the
[iMac20,2 SMU initialization report](https://github.com/t2linux/kernel/issues/27)
is a cold-boot case. They support keeping initialization, ownership,
switching, runtime power, and resume as separate acceptance dimensions.

Analysis identifies specific firmware components for RTC and desktop Ethernet.
The family-wide PMU RTC contract uses a signed 64-bit persistent offset, while
J160's Aquantia component is an I2C/LOM sideband controller and J185/J185f use
a distinct AOP-I2C topology. Neither result alone defines a safe Linux ABI or
proves that ordinary Ethernet packets traverse the T2.

## Publication boundary

Publish build identities, hashes, offsets, schemas, pseudocode, sanitized
descriptors, and reproducible extraction commands. Do not publish Apple
firmware payloads, raw camera frames, machine identifiers, serial numbers,
network addresses, or unreviewed journals. Keep static firmware conclusions,
live observations, and causal inferences visibly separate.

The retained camera runs contain image content and device, udev, and boot
metadata. Keep that bundle private; publish only reviewed measurements and
sanitized descriptors.

For new hardware reports, follow the [investigation guide](../method/investigation-guide.md)
and record a usable end-to-end result rather than one successful driver
callback. For artifact provenance and the existing hashes, see
[Artifacts and method](../method/platform-artifacts.md).
