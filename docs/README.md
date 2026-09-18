# Research map

Find a topic by its Linux name, firmware component, device ID, or function.
This map is generated from [research-map.json](../catalog/research-map.json).
The [catalog guide](../catalog/README.md) describes machine lookups and the schema.

Use the [coverage map](platform/research-coverage.md) for the limits of each investigation.
A relationship below is qualified evidence, not a claim that a feature works.

## Topics

| Topic | Function |
| --- | --- |
| [SEP services and AKS identity](#sep) | Account creation, authorization, and secure service transport |
| [Touch ID and fingerprint persistence](#fingerprint) | Enrollment, matching, deletion, and cross-boot restoration |
| [ANS2 host storage and SEP persistence](#storage) | Root storage and persistent secure state |
| [Boot policy, firmware updates, and recovery](#boot) | Booting Linux and understanding recovery transactions |
| [Dual-GPU graphics and gmux](#graphics) | Panel routing, display initialization, GPU power, and switching |
| [BCE transport, VHCI, and DMA reset](#bce) | Internal peripheral transport and coordinated recovery |
| [Sleep, wake, and hibernate](#power) | System power transitions and wake attribution |
| [SMC, charging, and thermal control](#smc) | Battery state, charge policy, temperatures, fans, and notifications |
| [Bridge audio state and playback clock](#bridge-audio) | Playback, recording, timing, and endpoint state |
| [AOP audio and voice trigger](#aop-audio) | Low-power microphone services and retained audio |
| [AOP sensors and SPU time](#aop-sensors) | Motion and pressure samples, calibration, and timestamps |
| [Lid-angle sensor (LAS)](#las) | Lid-angle reporting |
| [Ambient light sensor](#als) | Ambient light and color measurements |
| [Trackpad, Force Touch, and HIDSPI](#multitouch) | Pointer input, pressure, palm handling, and input recovery |
| [Touch Bar USB and DRM](#touch-bar) | Touch Bar keys, display binding, and reprobe |
| [Camera, ISP, exposure, and privacy](#camera-isp) | Camera capture, exposure, privacy, and stream recovery |
| [AVE video encoder](#ave) | Hardware video encoding |
| [Wi-Fi and P2P](#wifi) | Wireless networking |
| [Bluetooth firmware and AOP power](#bluetooth) | Bluetooth setup and power lifecycle |
| [Thunderbolt and USB-C](#thunderbolt) | External devices, tunneled ports, and DMA policy |
| [Desktop Ethernet sideband](#ethernet) | Desktop Ethernet management |
| [RTC and persistent time](#rtc) | Clock offset persistence |
| [Diagnostics, watchdogs, and crash attribution](#diagnostics) | Distinguishing host failure, T2 panic, and IOP crashes |
| [Board configurations and platform topology](#boards) | Model-specific topology and policy |
| [Physical USB controllers outside BCE](#xhci) | External USB lifecycle |
| [Internal keyboard and backlight](#keyboard) | Keyboard input and illumination |

<a id="sep"></a>

## SEP services and AKS identity

Account creation, authorization, and secure service transport.

**Look up:** `Secure Enclave`, `AKS`, `AppleKeyStore`, `ACM`, `AppleCredentialManager`, `106b:1802`, `keybag`, `create-v4`, `create-v5`, `J214K`.

**Linux interfaces:** t2_sep_transport.

**Firmware/component names:** SEP, sks, AppleKeyStore, ACM, AppleSEPManager, AppleSEPCredentialManager, AppleSEPKeyStore, AppleSEPGenericTransfer, AppleAuthCP, CoreTrust, AMFI.

| Read | Reference |
| --- | --- |
| Start here | [SEP architecture](sep/services-and-mailboxes.md) |
| Related analysis | [Identity and authorization](sep/aks-identity-and-authorization.md) |
| Related analysis | [23P2048 identity-create version 4 layout](sep/aks-create-v4-j214k.md) |
| Related analysis | [Platform architecture](platform/pci-services-and-dma.md#compatibility-domains) |

**Findings:** [sep-routes](sep/services-and-mailboxes.md#host-routes-and-internal-services), [aks-framing](sep/services-and-mailboxes.md#mailbox-and-out-of-line-data), [create-export](sep/aks-identity-and-authorization.md#creation-layers-and-encoding), [create-v4-j214k](sep/aks-create-v4-j214k.md#evidence-boundaries-and-reported-hardware-qualification), [activation-input](sep/aks-identity-and-authorization.md#the-retained-creation-input), [authorization-lifetime](sep/aks-identity-and-authorization.md#the-retained-creation-input), [keybag-derivation](sep/aks-identity-and-authorization.md#inside-the-matched-sep-derivation-path), [primary-inventory](sep/aks-identity-and-authorization.md#inventory-and-ownership), [sep-quiesce](power/sleep-wake-and-hibernate.md#pmgr-and-rtbuddy).

**Examined areas:** [S3: SEP services beyond biometrics](platform/research-coverage.md#s3).

<a id="fingerprint"></a>

## Touch ID and fingerprint persistence

Enrollment, matching, deletion, and cross-boot restoration.

**Look up:** `biometric`, `fprintd`, `Catacomb`, `BioLockout`, `enrollment`, `PAM`.

**Linux interfaces:** fprintd, PAM.

**Firmware/component names:** BiometricKit, SEP, AppleBiometricSensor, AppleMesaSEPDriver, IOBiometricFamily, AppleBiometricServices.

| Read | Reference |
| --- | --- |
| Start here | [Fingerprint lifecycle](sep/fingerprint-lifecycle.md) |
| Related analysis | [Fingerprint integration contracts](sep/fingerprint-integration.md) |
| Related analysis | [Linux integration of SEP identity](sep/linux-integration.md) |
| Related analysis | [Platform architecture](platform/pci-services-and-dma.md#compatibility-domains) |

**Findings:** [first-catacomb](sep/fingerprint-lifecycle.md#constructing-the-first-catacomb), [restore-order](sep/fingerprint-lifecycle.md#restoring-on-another-boot), [native-lifecycle](sep/fingerprint-lifecycle.md#matching-adding-and-deleting), [mutable-identity-authority](sep/fingerprint-integration.md#account-authority-and-the-current-identity-set), [durable-identity-names](sep/fingerprint-integration.md#stable-names), [delete-forward-recovery](sep/fingerprint-integration.md#durable-completion-and-interrupted-deletion), [direct-client-lifecycle](sep/fingerprint-integration.md#client-and-service-ownership).

**Examined areas:** [S4: Touch ID lifecycle](platform/research-coverage.md#s4).

<a id="storage"></a>

## ANS2 host storage and SEP persistence

Root storage and persistent secure state.

**Look up:** `NVMe`, `ANS`, `ANS2`, `xART`, `gigalocker`, `106b:2005`, `106b:2002`, `APFS`, `PFK`.

**Linux interfaces:** nvme.

**Firmware/component names:** AppleANS, xART, embedded NVMe, IONVMeFamily, AppleANS2OOB, AppleNANDConfigAccess, AppleBCENORFlashDeviceEP, AppleEffaceableStorage, APFS.

| Read | Reference |
| --- | --- |
| Start here | [Boot and persistent storage](storage/sep-persistence-and-nvme.md) |
| Related analysis | [Sleep, wake, and hibernate](power/sleep-wake-and-hibernate.md#ans-ordinary-sleep-and-cancellation) |
| Related analysis | [Platform architecture](platform/pci-services-and-dma.md#compatibility-domains) |

**Findings:** [ans-sleep](power/sleep-wake-and-hibernate.md#ans-ordinary-sleep-and-cancellation), [storage-boundary](platform/pci-services-and-dma.md#storage-and-sep), [xart-record-path](storage/sep-persistence-and-nvme.md#xart-and-gigalocker), [xart-command8](storage/sep-persistence-and-nvme.md#why-host-endpoint-16-command-8-failed), [embedded-storage](storage/sep-persistence-and-nvme.md#embedded-nvme-is-separate-from-host-storage).

**Examined areas:** [S1: Host ANS2/root storage](platform/research-coverage.md#s1), [S2: BridgeOS internal ANS/NVMe and xART](platform/research-coverage.md#s2).

<a id="boot"></a>

## Boot policy, firmware updates, and recovery

Booting Linux and understanding recovery transactions.

**Look up:** `EFI`, `iBoot`, `LLB`, `iBEC`, `iBSS`, `MacEFI`, `DFU`, `restored_update`, `panicmedic`, `UKI`, `Limine`, `LUKS`.

**Linux interfaces:** boot loader, kernel updates.

**Firmware/component names:** iBoot, MacEFI, restored_update, seputil, AppleFirmwareUpdateKext, AppleEmbeddedPUPConfigMgmt, FirmwareService, MacEFIManager.

| Read | Reference |
| --- | --- |
| Start here | [iBoot policy, firmware update, and recovery](boot/iboot-firmware-update-and-recovery.md) |
| Related analysis | [Boot and distribution integration](boot/linux-boot-and-updates.md) |
| Related analysis | [Platform architecture](platform/pci-services-and-dma.md#compatibility-domains) |

**Findings:** [efi-boot-state](storage/sep-persistence-and-nvme.md#publishing-boot-state), [iboot-failure-policy](boot/iboot-firmware-update-and-recovery.md#iboot-failure-counters-and-fallback), [firmware-update-outer-order](boot/iboot-firmware-update-and-recovery.md#firmware-transaction-and-commit-order), [kernel-updates](boot/linux-boot-and-updates.md#keep-the-t2-kernel-attached-to-an-update-source).

**Examined areas:** [S5: Boot and EFI policy](platform/research-coverage.md#s5), [S6: Firmware update, erase, and device-mode recovery](platform/research-coverage.md#s6).

<a id="graphics"></a>

## Dual-GPU graphics and gmux

Panel routing, display initialization, GPU power, and switching.

**Look up:** `i915`, `amdgpu`, `apple-gmux`, `AppleMuxControl2`, `VFCT`, `VBT`, `EDID`, `eDP`, `HDA`, `PEG`, `force_igd`, `APP7777`.

**Linux interfaces:** DRM, i915, amdgpu, apple-gmux.

**Firmware/component names:** GMUXDriver, CoffeelakeGraphics, AppleMuxControl2, ACPI.

| Read | Reference |
| --- | --- |
| Start here | [Dual-GPU graphics: gmux, panel timing, and VFCT](graphics/gmux-panel-and-vfct.md) |
| Related analysis | [Host ACPI and graphics coordination](graphics/acpi-and-gpu-ownership.md) |

**Findings:** [host-acpi](graphics/acpi-and-gpu-ownership.md#j152f-acpi), [app7777](graphics/acpi-and-gpu-ownership.md#app7777-comparator), [mux-policy](graphics/gmux-panel-and-vfct.md#gmux-policy-and-switch-transactions), [gpu-policy](boot/linux-boot-and-updates.md#internal-panel-ownership-and-radeon-policy), [graphics-duplicate-panel](platform/linux-support.md#current-j152f-checkpoint), [j152-panel-sequencer](graphics/gmux-panel-and-vfct.md#intel-panel-sequencing), [gmux-route-contract](graphics/gmux-panel-and-vfct.md#gmux-policy-and-switch-transactions), [vfct-connector-topology](graphics/gmux-panel-and-vfct.md#amd-vfct-connector-topology).

**Examined areas:** [P2: J152f host boundary and APP7777 applicability](platform/research-coverage.md#p2), [G1: Intel panel, EDID, and MacEFI sequencing](platform/research-coverage.md#g1), [G2: gmux ownership and switch transaction](platform/research-coverage.md#g2), [G3: AMD/HDA/root-port power, reset, and runtime switch](platform/research-coverage.md#g3).

<a id="bce"></a>

## BCE transport, VHCI, and DMA reset

Internal peripheral transport and coordinated recovery.

**Look up:** `t2bce`, `BCE`, `VHCI`, `virtual USB`, `DART`, `PERST`, `106b:1801`, `IOBufferCopyController`.

**Linux interfaces:** t2bce_core, t2bce_vhci.

**Firmware/component names:** BCE, AppleT8015DART, AppleEmbeddedPCIeUpLinkMgmt, AppleEmbeddedPCIE, AppleT8010PCIe, AppleSART, IODARTFamily, AppleUSBVHCICommon, AppleUSBVHCICommonBCE, AppleUSBVHCIFirmware, AppleUSBVHCIFirmwareBCE.

| Read | Reference |
| --- | --- |
| Start here | [Platform architecture](platform/pci-services-and-dma.md#reset-and-queue-boundaries) |
| Related analysis | [Sleep, wake, and hibernate](power/sleep-wake-and-hibernate.md#bce-state-preservation) |
| Related analysis | [Platform architecture](platform/pci-services-and-dma.md#compatibility-domains) |

**Findings:** [bce-state](power/sleep-wake-and-hibernate.md#bce-state-preservation), [vhci-exception](power/sleep-wake-and-hibernate.md#vhci-exceptions-and-message-direction), [bce-platform-fabric](platform/linux-support.md#current-j152f-checkpoint), [dart-reset-boundary](platform/pci-services-and-dma.md#reset-and-queue-boundaries), [vhci-epoch-gap](platform/pci-services-and-dma.md#reset-and-queue-boundaries), [late-completion](power/linux-suspend-observations.md#a-delayed-vhci-completion).

**Examined areas:** [P4: Shared upstream PCIe and DART](platform/research-coverage.md#p4), [P8: BCE ordinary sleep selection](platform/research-coverage.md#p8), [P9: VHCI, internal USB, reset, and wake](platform/research-coverage.md#p9).

<a id="power"></a>

## Sleep, wake, and hibernate

System power transitions and wake attribution.

**Look up:** `suspend`, `resume`, `S3`, `S4`, `s2idle`, `hibernate`, `PMGR`, `RTBuddy`.

**Linux interfaces:** PCI power management, system sleep.

**Firmware/component names:** PMGR, RTBuddy, AppleSSM, ApplePMGR, AppleT8012PMGR, AppleARMPMU, AppleT8010CLPC, AppleT8010SOCTuner, AppleDialogPMU, AppleD2449PMU, AppleA7IOP, AppleT8012SmartIO.

| Read | Reference |
| --- | --- |
| Start here | [Sleep, wake, and hibernate](power/sleep-wake-and-hibernate.md) |
| Related analysis | [Suspend observations](power/linux-suspend-observations.md) |
| Related analysis | [Platform architecture](platform/pci-services-and-dma.md#compatibility-domains) |

**Findings:** [pmgr-records](power/sleep-wake-and-hibernate.md#pmgr-and-rtbuddy), [inactive-control](power/linux-suspend-observations.md#what-the-inactive-control-establishes), [hibernate-chain](method/investigation-guide.md#treat-hibernate-as-a-complete-chain).

**Examined areas:** [P7: AppleSMC and PMGR completion/wake fabric](platform/research-coverage.md#p7), [P8: BCE ordinary sleep selection](platform/research-coverage.md#p8), [P10: Hibernate as a whole chain](platform/research-coverage.md#p10), [S3: SEP services beyond biometrics](platform/research-coverage.md#s3).

<a id="smc"></a>

## SMC, charging, and thermal control

Battery state, charge policy, temperatures, fans, and notifications.

**Look up:** `AppleSMC`, `applesmc`, `BCLM`, `USB-PD`, `battery`, `hwmon`, `fan`, `thermal`, `NMSN`, `MBSE`.

**Linux interfaces:** applesmc, hwmon, ACPI Smart Battery.

**Firmware/component names:** AppleSMC, AppleSSM, AppleSmartBattery, IOAccessory.

| Read | Reference |
| --- | --- |
| Start here | [SMC notifications, charging, and USB-PD](smc/notifications-and-usb-pd.md) |
| Related analysis | [Sleep, wake, and hibernate](power/sleep-wake-and-hibernate.md#wake-aggregation-and-smc) |

**Findings:** [smc-wake](power/sleep-wake-and-hibernate.md#wake-aggregation-and-smc), [smc-order](graphics/acpi-and-gpu-ownership.md#smc-platform-actions), [smc-live-inventory](platform/linux-support.md#current-j152f-checkpoint), [smc-inbound-envelope](smc/notifications-and-usb-pd.md#smc-notification-envelope), [smc-usbpd-key-layouts](smc/notifications-and-usb-pd.md#usb-pd-current-and-voltage-layouts).

**Examined areas:** [P7: AppleSMC and PMGR completion/wake fabric](platform/research-coverage.md#p7), [G7: AppleSMC charging and thermal policy](platform/research-coverage.md#g7), [G8: Battery/charging symptom](platform/research-coverage.md#g8).

<a id="bridge-audio"></a>

## Bridge audio state and playback clock

Playback, recording, timing, and endpoint state.

**Look up:** `ALSA`, `PipeWire`, `t2bce_audio`, `bridgeaudiod`, `sampleTime`, `GPR`, `106b:1803`, `speaker`, `headphone`.

**Linux interfaces:** ALSA, PipeWire, t2bce_audio.

**Firmware/component names:** bridgeaudiod, AppleBridgeAudio, AppleBridgeAudioPCIEP, BridgeAudioCommunication.

| Read | Reference |
| --- | --- |
| Start here | [Bridge audio: endpoint state and playback clock](audio/bridge-audio-state-and-clock.md) |
| Related analysis | [Platform architecture](platform/pci-services-and-dma.md#compatibility-domains) |

**Findings:** [bridge-audio-gpr-restore](audio/bridge-audio-state-and-clock.md#endpoint-gpr-ownership-and-lifetime), [bridge-audio-clock-feedback](audio/bridge-audio-state-and-clock.md#playback-sampletime-feedback).

**Examined areas:** [G4: Bridge-audio endpoint state and PM revalidation](platform/research-coverage.md#g4), [G5: Playback clock, codec, DSP, jack, and speaker protection](platform/research-coverage.md#g5).

<a id="aop-audio"></a>

## AOP audio and voice trigger

Low-power microphone services and retained audio.

**Look up:** `AOP`, `AppleAOPAudio`, `voice trigger`, `historic audio`, `SpuMCAPacket`, `SubPacket`, `microphone`.

**Linux interfaces:** No retained Linux AOP-audio owner.

**Firmware/component names:** AOP, AppleAOPAudio, AppleAOPVoiceTrigger, AppleARMIISAudio.

| Read | Reference |
| --- | --- |
| Start here | [AOP audio and voice trigger](audio/aop-voice-trigger.md) |
| Related analysis | [Platform architecture](platform/pci-services-and-dma.md#compatibility-domains) |

**Findings:** [aop-audio-control-contract](audio/aop-voice-trigger.md), [aop-audio-data-envelope](audio/aop-voice-trigger.md).

**Examined areas:** [G6: AOP audio and voice trigger](platform/research-coverage.md#g6).

<a id="aop-sensors"></a>

## AOP sensors and SPU time

Motion and pressure samples, calibration, and timestamps.

**Look up:** `AOP`, `SPU`, `AppleSPUHIDDriver`, `IIO`, `accelerometer`, `gyro`, `pressure`, `timesync`, `calibration`.

**Linux interfaces:** HID, IIO.

**Firmware/component names:** AppleSPU, AppleSPUHIDDriver.

| Read | Reference |
| --- | --- |
| Start here | [AOP and SPU sensor properties and time](sensors/aop-spu-samples-and-time.md) |
| Related analysis | [Sleep, wake, and hibernate](power/sleep-wake-and-hibernate.md#aop-sensor-time-and-retention) |

**Findings:** [aop-sensor-host-properties](sensors/aop-spu-samples-and-time.md).

**Examined areas:** [G9: AOP sensors and timesync](platform/research-coverage.md#g9).

<a id="las"></a>

## Lid-angle sensor (LAS)

Lid-angle reporting.

**Look up:** `LAS`, `lid angle`, `lid-angle sensor`, `05ac:8104`, `hid-sensor-rotation`, `HIDIOCGFEATURE`, `MA781`, `MagAlpha`.

**Linux interfaces:** hidraw, HID sensors.

**Firmware/component names:** las, HID relay.

| Read | Reference |
| --- | --- |
| Start here | [Lid-angle sensor (LAS)](sensors/las-lid-angle.md) |

**Findings:** [hid-sensor-export-gap](sensors/las-lid-angle.md).

**Examined areas:** [I4: Lid-angle sensor (LAS)](platform/research-coverage.md#i4).

<a id="als"></a>

## Ambient light sensor

Ambient light and color measurements.

**Look up:** `ALS`, `ambient light`, `illuminance`, `color`, `05ac:8262`.

**Linux interfaces:** HID sensors, IIO.

**Firmware/component names:** USB HID sensor.

| Read | Reference |
| --- | --- |
| Start here | [Linux compatibility map](platform/linux-support.md#current-j152f-checkpoint) |

**Findings:** [bce-platform-fabric](platform/linux-support.md#current-j152f-checkpoint).

<a id="multitouch"></a>

## Trackpad, Force Touch, and HIDSPI

Pointer input, pressure, palm handling, and input recovery.

**Look up:** `multitouch`, `Force Touch`, `palm`, `HIDSPI`, `AFU`, `AppleMultitouchDriver`, `MultitouchHID.plugin`, `trackpad`, `0x7e`.

**Linux interfaces:** HID, raw user client.

**Firmware/component names:** InputDevice, Multitouch, ST AFU, AppleHIDTransport, AppleHIDTransportSPI, AppleInputDeviceSupport, AppleTopCaseHIDEventDriver.

| Read | Reference |
| --- | --- |
| Start here | [HID input, HIDSPI, and multitouch](input/hid-multitouch.md) |
| Related analysis | [Platform architecture](platform/pci-services-and-dma.md#compatibility-domains) |

**Findings:** [multitouch-report-gate](input/hid-multitouch.md#multitouch-report-gate-and-afu-boundary), [multitouch-afu-path-response](input/hid-multitouch.md#multitouch-report-gate-and-afu-boundary).

**Examined areas:** [I1: HIDSPI updater, reset policy, and report 0x7e](platform/research-coverage.md#i1), [I2: Multitouch, Force Touch, palm, and report bodies](platform/research-coverage.md#i2).

<a id="touch-bar"></a>

## Touch Bar USB and DRM

Touch Bar keys, display binding, and reprobe.

**Look up:** `Touch Bar`, `TouchBar`, `05ac:8302`, `appletbdrm`, `hid_appletb_kbd`, `tiny-dfr`.

**Linux interfaces:** USB, HID, DRM.

**Firmware/component names:** USB configurations 1 and 2.

| Read | Reference |
| --- | --- |
| Start here | [Touch Bar USB configuration and DRM binding](input/touch-bar-usb-drm.md) |

**Findings:** [touchbar-binding-question](input/touch-bar-usb-drm.md).

**Examined areas:** [I3: Touch Bar display personality](platform/research-coverage.md#i3).

<a id="camera-isp"></a>

## Camera, ISP, exposure, and privacy

Camera capture, exposure, privacy, and stream recovery.

**Look up:** `ISP`, `UVC`, `webcam`, `AppleM8`, `AppleM8CameraInterface`, `AppleH9CameraInterface`, `AppleUVCCamera`, `exposure`, `privacy LED`, `selector 7`, `0x0204`.

**Linux interfaces:** uvcvideo, V4L2.

**Firmware/component names:** AppleM8CameraInterface, AppleH9CameraInterface, AppleUVCCamera.

| Read | Reference |
| --- | --- |
| Start here | [Camera ISP exposure and UVC controls](camera/isp-exposure-and-uvc.md) |
| Related analysis | [Linux compatibility map](platform/linux-support.md#current-j152f-checkpoint) |

**Findings:** [camera-native-baseline](platform/linux-support.md#current-j152f-checkpoint), [camera-xu-negative](camera/isp-exposure-and-uvc.md), [camera-internal-exposure-path](camera/isp-exposure-and-uvc.md).

**Examined areas:** [I5: Camera controls, exposure, privacy, teardown, and reopen](platform/research-coverage.md#i5).

<a id="ave"></a>

## AVE video encoder

Hardware video encoding.

**Look up:** `AVE`, `AppleAVEBridge`, `AppleAVE2`, `aveserverd`, `H9`, `HEVC`, `H.264`, `video encoder`, `t2bce_ave`.

**Linux interfaces:** V4L2 mem2mem, t2bce_ave.

**Firmware/component names:** AppleAVEBridge, aveserverd, H9.videoencoder, AppleAVE2Driver.

| Read | Reference |
| --- | --- |
| Start here | [AVE video encoder transport](media/ave-video-encoder.md) |

**Findings:** [ave-owner-transport-boundary](media/ave-video-encoder.md).

**Examined areas:** [I6: T2 media encoder](platform/research-coverage.md#i6).

<a id="wifi"></a>

## Wi-Fi and P2P

Wireless networking.

**Look up:** `Wi-Fi`, `wifi`, `WLAN`, `BCM4364`, `brcmfmac`, `P2P`, `NVRAM`.

**Linux interfaces:** brcmfmac.

**Firmware/component names:** Broadcom firmware.

| Read | Reference |
| --- | --- |
| Start here | [Linux compatibility map](platform/linux-support.md#current-j152f-checkpoint) |

**Findings:** [wifi-p2p-gap](platform/linux-support.md#current-j152f-checkpoint).

**Examined areas:** [I7: Wi-Fi](platform/research-coverage.md#i7).

<a id="bluetooth"></a>

## Bluetooth firmware and AOP power

Bluetooth setup and power lifecycle.

**Look up:** `Bluetooth`, `BT`, `HCI`, `BCM.hcd`, `Marconi`, `AppleSPUMarconiControl`.

**Linux interfaces:** Bluetooth HCI.

**Firmware/component names:** Broadcom controller, AppleSPUMarconiControl.

| Read | Reference |
| --- | --- |
| Start here | [Bluetooth Marconi power control](network/bluetooth-marconi.md) |
| Related analysis | [Linux compatibility map](platform/linux-support.md#current-j152f-checkpoint) |

**Findings:** [bluetooth-firmware-selection](platform/linux-support.md#current-j152f-checkpoint), [marconi-power-control](network/bluetooth-marconi.md).

**Examined areas:** [I8: Bluetooth and AOP control](platform/research-coverage.md#i8).

<a id="thunderbolt"></a>

## Thunderbolt and USB-C

External devices, tunneled ports, and DMA policy.

**Look up:** `Thunderbolt`, `USB-C`, `Titan Ridge`, `hotplug`, `IOMMU`, `tunneled-native-port`.

**Linux interfaces:** thunderbolt.

**Firmware/component names:** Host Thunderbolt controllers.

| Read | Reference |
| --- | --- |
| Start here | [Linux compatibility map](platform/linux-support.md#current-j152f-checkpoint) |
| Related analysis | [Sleep, wake, and hibernate](power/sleep-wake-and-hibernate.md#pcie-and-peripheral-lifecycle) |

**Findings:** [thunderbolt-integration-gap](platform/linux-support.md#current-j152f-checkpoint).

**Examined areas:** [I9: USB-C and Thunderbolt](platform/research-coverage.md#i9).

<a id="ethernet"></a>

## Desktop Ethernet sideband

Desktop Ethernet management.

**Look up:** `Ethernet`, `Aquantia`, `AQC`, `aqc107`, `aqc-i2c`, `LOM`, `J160`, `J185`, `J185f`.

**Linux interfaces:** Ethernet.

**Firmware/component names:** Aquantia sideband, AOP-I2C.

| Read | Reference |
| --- | --- |
| Start here | [Desktop Ethernet sideband management](network/ethernet-sideband.md) |

**Findings:** [desktop-ethernet-sideband](network/ethernet-sideband.md).

**Examined areas:** [I10: Desktop Ethernet](platform/research-coverage.md#i10).

<a id="rtc"></a>

## RTC and persistent time

Clock offset persistence.

**Look up:** `RTC`, `real-time clock`, `pmu,d2449`, `AppleD2449PMURTC`, `rtc-offset`.

**Linux interfaces:** RTC.

**Firmware/component names:** AppleD2449PMURTC, iBoot.

| Read | Reference |
| --- | --- |
| Start here | [RTC persistent offset and PMU policy](sensors/rtc-persistent-offset.md) |

**Findings:** [rtc-offset-contract](sensors/rtc-persistent-offset.md).

**Examined areas:** [I11: RTC and persistent time](platform/research-coverage.md#i11).

<a id="diagnostics"></a>

## Diagnostics, watchdogs, and crash attribution

Distinguishing host failure, T2 panic, and IOP crashes.

**Look up:** `RemoteXPC`, `BridgeXPC`, `watchdog`, `panic`, `crash`, `diagnostics`.

**Linux interfaces:** kernel logs.

**Firmware/component names:** bridgeOS diagnostics, watchdog, AppleARMWatchdogTimer.

| Read | Reference |
| --- | --- |
| Start here | [Investigation guide](method/investigation-guide.md#correlate-bridgeos-postmortems) |
| Related analysis | [Platform architecture](platform/pci-services-and-dma.md#peripherals-and-diagnostics) |
| Related analysis | [Platform architecture](platform/pci-services-and-dma.md#compatibility-domains) |

**Examined areas:** [P5: Remote diagnostics and paired attribution](platform/research-coverage.md#p5), [P6: Watchdog, panic, and crash recovery](platform/research-coverage.md#p6).

<a id="boards"></a>

## Board configurations and platform topology

Model-specific topology and policy.

**Look up:** `iBridge2`, `DeviceTree`, `J152f`, `MacBookPro16,1`, `board matrix`.

**Linux interfaces:** PCI, ACPI.

**Firmware/component names:** DeviceTree, portable and desktop kernelcaches.

| Read | Reference |
| --- | --- |
| Start here | [Board configurations](platform/board-configurations.md) |
| Related analysis | [Platform architecture](platform/pci-services-and-dma.md) |

**Findings:** [family-link](platform/board-configurations.md#shared-topology-and-policy), [board-policy](platform/board-configurations.md#production-matrix).

**Examined areas:** [P1: Sixteen-board BridgeOS policy](platform/research-coverage.md#p1), [P2: J152f host boundary and APP7777 applicability](platform/research-coverage.md#p2), [P3: Host boundary on the other 15 boards](platform/research-coverage.md#p3).

<a id="xhci"></a>

## Physical USB controllers outside BCE

External USB lifecycle.

**Look up:** `xHCI`, `physical USB`.

**Linux interfaces:** xhci_hcd.

**Firmware/component names:** Host USB controllers.

| Read | Reference |
| --- | --- |
| Start here | [Sleep, wake, and hibernate](power/sleep-wake-and-hibernate.md#pcie-and-peripheral-lifecycle) |

**Examined areas:** [I12: Physical xHCI outside BCE](platform/research-coverage.md#i12).

<a id="keyboard"></a>

## Internal keyboard and backlight

Keyboard input and illumination.

**Look up:** `keyboard`, `backlight`, `hid-apple`.

**Linux interfaces:** HID.

**Firmware/component names:** Internal input and backlight devices, AppleHIDKeyboard.

| Read | Reference |
| --- | --- |
| Start here | [Linux compatibility map](platform/linux-support.md#current-j152f-checkpoint) |
| Related analysis | [HID input, HIDSPI, and multitouch](input/hid-multitouch.md) |
| Related analysis | [Platform architecture](platform/pci-services-and-dma.md#compatibility-domains) |

**Findings:** [bce-platform-fabric](platform/linux-support.md#current-j152f-checkpoint).

**Examined areas:** [I13: Internal keyboard and backlight](platform/research-coverage.md#i13).

## Interface routes

This partial interface map records the inspected host routes. A USB parent
identifies its host transport; it does not prove the embedded firmware owner.

| Interface | Parent route | Identity | PCI function / DART stream | Scope and evidence |
| --- | --- | --- | --- | --- |
| `t2-pcie` (PCIe link) | Host PCIe | `apcie-up,t8012; x4 Gen2` | — | [Production DeviceTrees in bridgeOS 23P6068.](platform/pci-services-and-dma.md#host-and-firmware-boundaries) (recovered) |
| `ans2` (PCI function) | t2-pcie | `106b:2005` | 0 / 1 | [Function/DART assignment from bridgeOS 23P6068; PCI ID observed on J152f.](platform/pci-services-and-dma.md#host-and-firmware-boundaries) (recovered-and-observed) |
| `bce` (PCI function) | t2-pcie | `106b:1801` | 1 / 0 | [Function/DART assignment from bridgeOS 23P6068; PCI ID observed on J152f.](platform/pci-services-and-dma.md#host-and-firmware-boundaries) (recovered-and-observed) |
| `sep` (PCI function) | t2-pcie | `106b:1802` | 2 / 2 | [Function/DART assignment from bridgeOS 23P6068; PCI ID observed on J152f.](platform/pci-services-and-dma.md#host-and-firmware-boundaries) (recovered-and-observed) |
| `bridge-audio` (PCI function) | t2-pcie | `106b:1803` | 3 / 3 | [Function/DART assignment from bridgeOS 23P6068; PCI ID observed on J152f.](platform/pci-services-and-dma.md#host-and-firmware-boundaries) (recovered-and-observed) |
| `las-usb` (USB device via BCE/VHCI) | bce | `05ac:8104` | — | [J152f inventory on 2026-09-18; does not establish the embedded firmware owner.](sensors/las-lid-angle.md) (observed) |
| `touch-bar-usb` (USB device via BCE/VHCI) | bce | `05ac:8302` | — | [J152f inventory on 2026-09-18; does not establish the embedded firmware owner.](input/touch-bar-usb-drm.md) (observed) |
| `als-usb` (USB device via BCE/VHCI) | bce | `05ac:8262` | — | [J152f inventory on 2026-09-18; does not establish the embedded firmware owner.](platform/linux-support.md#current-j152f-checkpoint) (observed) |

## Relationships and evidence limits

These edges connect investigated services and functions. Inferred and unresolved
edges remain visibly distinct from recovered contracts and observations.

| From → to | Relationship | Evidence | Interpretation and source |
| --- | --- | --- | --- |
| [bce](#bce) → [camera-isp](#camera-isp) | transport | observed | [BCE/VHCI exposes the UVC camera.](platform/pci-services-and-dma.md#peripherals-and-diagnostics) |
| [bce](#bce) → [touch-bar](#touch-bar) | transport | observed | [BCE/VHCI exposes the Touch Bar USB configurations.](platform/linux-support.md#current-j152f-checkpoint) |
| [bce](#bce) → [las](#las) | transport | observed | [BCE/VHCI exposes the lid-angle sensor as USB 05ac:8104.](sensors/las-lid-angle.md) |
| [bce](#bce) → [keyboard](#keyboard) | transport | observed | [Internal keyboard and backlight enumerate through BCE/VHCI.](platform/linux-support.md#current-j152f-checkpoint) |
| [bce](#bce) → [als](#als) | transport | observed | [BCE/VHCI exposes the ambient-light sensor.](platform/linux-support.md#current-j152f-checkpoint) |
| [bce](#bce) → [multitouch](#multitouch) | transport | observed | [The internal trackpad is a BCE/VHCI child in the inventory.](platform/linux-support.md#current-j152f-checkpoint) |
| [fingerprint](#fingerprint) → [sep](#sep) | service-dependency | recovered | [Biometric operations depend on SEP identity and authorization services.](sep/fingerprint-lifecycle.md#from-an-activated-account-to-a-fingerprint) |
| [sep](#sep) → [storage](#storage) | persistence-dependency | recovered | [SEP persistence crosses xART and embedded storage boundaries.](storage/sep-persistence-and-nvme.md#xart-and-gigalocker) |
| [power](#power) → [graphics](#graphics) | coordination | recovered | [Graphics transitions coordinate GPU, HDA, root port, and mux state.](graphics/gmux-panel-and-vfct.md) |
| [power](#power) → [smc](#smc) | coordination | recovered | [Wake and completion notifications involve the SMC fabric.](power/sleep-wake-and-hibernate.md#wake-aggregation-and-smc) |
| [aop-sensors](#aop-sensors) → [las](#las) | possible-owner | inferred | [AOP LAS naming suggests ownership; a direct host relay route is not proven.](platform/board-configurations.md#shared-topology-and-policy) |
| [aop-audio](#aop-audio) → [bridge-audio](#bridge-audio) | distinct-subsystem | recovered | [AOP voice-trigger services are separate from host-visible bridge audio.](audio/aop-voice-trigger.md) |
| [bluetooth](#bluetooth) → [aop-sensors](#aop-sensors) | control-comparator | unresolved | [Marconi control uses AppleSPU; its relation to host HCI symptoms is unproven.](network/bluetooth-marconi.md) |
| [camera-isp](#camera-isp) → [ave](#ave) | distinct-subsystem | recovered | [Camera controls and AVE encoding have separate recovered owners and interfaces.](media/ave-video-encoder.md) |

## Complete chapter inventory

| Chapter | Topics |
| --- | --- |
| [AOP audio and voice trigger](audio/aop-voice-trigger.md) | [aop-audio](#aop-audio) |
| [Bridge audio: endpoint state and playback clock](audio/bridge-audio-state-and-clock.md) | [bridge-audio](#bridge-audio) |
| [iBoot policy, firmware update, and recovery](boot/iboot-firmware-update-and-recovery.md) | [boot](#boot) |
| [Boot and distribution integration](boot/linux-boot-and-updates.md) | [boot](#boot) |
| [Camera ISP exposure and UVC controls](camera/isp-exposure-and-uvc.md) | [camera-isp](#camera-isp) |
| [Host ACPI and graphics coordination](graphics/acpi-and-gpu-ownership.md) | [graphics](#graphics) |
| [Dual-GPU graphics: gmux, panel timing, and VFCT](graphics/gmux-panel-and-vfct.md) | [graphics](#graphics) |
| [HID input, HIDSPI, and multitouch](input/hid-multitouch.md) | [multitouch](#multitouch), [keyboard](#keyboard) |
| [Touch Bar USB configuration and DRM binding](input/touch-bar-usb-drm.md) | [touch-bar](#touch-bar) |
| [AVE video encoder transport](media/ave-video-encoder.md) | [ave](#ave) |
| [Investigation guide](method/investigation-guide.md) | [diagnostics](#diagnostics) |
| [Platform artifacts and method](method/platform-artifacts.md) | Cross-cutting method |
| [SEP artifacts and method](method/sep-artifacts.md) | [sep](#sep), [fingerprint](#fingerprint) |
| [Bluetooth Marconi power control](network/bluetooth-marconi.md) | [bluetooth](#bluetooth) |
| [Desktop Ethernet sideband management](network/ethernet-sideband.md) | [ethernet](#ethernet) |
| [Board configurations](platform/board-configurations.md) | [boards](#boards) |
| [Linux compatibility map](platform/linux-support.md) | [als](#als), [camera-isp](#camera-isp), [wifi](#wifi), [bluetooth](#bluetooth), [thunderbolt](#thunderbolt), [keyboard](#keyboard) |
| [Platform architecture](platform/pci-services-and-dma.md) | Cross-cutting reference |
| [Suspend observations](power/linux-suspend-observations.md) | [power](#power) |
| [Sleep, wake, and hibernate](power/sleep-wake-and-hibernate.md) | [storage](#storage), [bce](#bce), [power](#power), [smc](#smc), [aop-sensors](#aop-sensors), [thunderbolt](#thunderbolt), [xhci](#xhci) |
| [AOP and SPU sensor properties and time](sensors/aop-spu-samples-and-time.md) | [aop-sensors](#aop-sensors) |
| [Lid-angle sensor (LAS)](sensors/las-lid-angle.md) | [las](#las) |
| [RTC persistent offset and PMU policy](sensors/rtc-persistent-offset.md) | [rtc](#rtc) |
| [T2 SEP and Touch ID research](sep/README.md) | [sep](#sep), [fingerprint](#fingerprint) |
| [23P2048 identity-create version 4 layout](sep/aks-create-v4-j214k.md) | [sep](#sep) |
| [Identity and authorization](sep/aks-identity-and-authorization.md) | [sep](#sep) |
| [Fingerprint integration contracts](sep/fingerprint-integration.md) | [fingerprint](#fingerprint) |
| [Fingerprint lifecycle](sep/fingerprint-lifecycle.md) | [fingerprint](#fingerprint) |
| [Linux integration of SEP identity](sep/linux-integration.md) | [fingerprint](#fingerprint) |
| [SEP architecture](sep/services-and-mailboxes.md) | [sep](#sep) |
| [SMC notifications, charging, and USB-PD](smc/notifications-and-usb-pd.md) | [smc](#smc) |
| [Boot and persistent storage](storage/sep-persistence-and-nvme.md) | [storage](#storage) |
