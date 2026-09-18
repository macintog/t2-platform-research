# Platform architecture

The T2 combines host-facing PCI devices with an embedded operating system,
coprocessors, storage, and peripheral controllers. Linux sees several device
functions; bridgeOS coordinates a larger set of power and reset dependencies.

## Host and firmware boundaries

```text
Intel host: ACPI / PCI / GPU / physical USB / system power management
    |
    +-- T2 upstream PCIe link
            +-- function 0: ANS2 host storage
            +-- function 1: BCE transport and virtual USB
            +-- function 2: SEP transport
            +-- function 3: bridge audio

T2 firmware: AppleSMC system-state notifications
    +-- PMGR power domains and wake sources
    +-- RTBuddy-managed coprocessors
    +-- ANS internal storage and SEP/xART clients
    +-- BCE/VHCI, input, audio, camera, sensors, USB and watchdogs
```

The diagram shows relationships, not a measured execution order. The shared
PCIe link has reset and power constraints below the four host functions.
Successful per-function callbacks cannot establish that the complete platform
entered or left sleep coherently.

The [board matrix](board-configurations.md) describes all 16 configurations in
`23P6068`. The [host coordination reference](host-coordination.md) establishes
only the J152f host boundary and a separate Apple coordinator specimen.

## Compatibility domains

| Domain | Representative embedded components | Compatibility questions |
| --- | --- | --- |
| Platform power and clocks | ApplePMGR, AppleT8012PMGR, AppleARMPMU, AppleT8010CLPC, AppleT8010SOCTuner, AppleDialogPMU, AppleD2449PMU | Power domains, wake masks, thermal/battery vetoes, latency, panic/restart policy |
| T2 system state and IOPs | AppleSMC, RTBuddy, AppleA7IOP, AppleT8012SmartIO, AppleARMWatchdogTimer | Host-state transaction, coprocessor survival, acknowledgement, watchdog recovery |
| Host bridge and PCIe | AppleEmbeddedPCIeUpLinkMgmt, AppleEmbeddedPCIE, AppleT8010PCIe, AppleSART, IODARTFamily | Shared-link quiesce, PERST/LTSSM, DMA isolation, reset ordering |
| BCE and virtual USB | AppleUSBVHCICommon, AppleUSBVHCICommonBCE, AppleUSBVHCIFirmware, AppleUSBVHCIFirmwareBCE | Host input/peripheral transport, wake events, queue restoration, desync recovery |
| Storage and persistence | IONVMeFamily, AppleANS2OOB, AppleNANDConfigAccess, AppleBCENORFlashDeviceEP, AppleEffaceableStorage, APFS | Host versus embedded namespaces, orderly power-off, panic logs, firmware/xART state |
| SEP and security | AppleSEPManager, AppleSEPCredentialManager, AppleSEPKeyStore, AppleSEPGenericTransfer, AppleAuthCP, CoreTrust, AMFI | Endpoint lifecycle, hibernate boot, keybag continuity, xART shutdown, authentication |
| Biometric | AppleBiometricSensor, AppleMesaSEPDriver, IOBiometricFamily, AppleBiometricServices | Sensor power, AOP dependency, enrollment/match continuity, post-wake authorization |
| Input and Touch Bar | AppleHIDTransport, AppleHIDTransportSPI, AppleInputDeviceSupport, AppleMultitouchDriver, AppleTopCaseHIDEventDriver, AppleHIDKeyboard | Device reset/power sequence, auto-suspend, re-enumeration, visible recovery |
| Audio and AOP | AppleBridgeAudio, AppleBridgeAudioPCIEP, BridgeAudioCommunication, AppleAOPAudio, AppleAOPVoiceTrigger, AppleARMIISAudio, codec drivers | Separate PCI function, low-power microphone, register restore, codec shutdown |
| Camera, display, and media | AppleH9CameraInterface, ISP, IOMobileGraphicsFamily, AppleSynopsysMIPIDSI, AppleSummitLCD, AppleAVE/AVE2, AppleJPEGDriver, scaler | Gated media domains, late completions, high-bandwidth VHCI use, panel/Touch Bar output |
| USB, accessories, and networking | AppleEmbeddedUSB, AppleSynopsysOTGDevice, IOUSBHost/Device families, AppleUSBDeviceNCM/Mux, AppleUSBEthernetDevice, AppleBCMWLANUart, accessory families | PHY power, USB role, CDC-NCM diagnostics, restore/recovery transport |
| Firmware/update/recovery support | AppleFirmwareUpdateKext, AppleEmbeddedPUPConfigMgmt/FirmwareService, MacEFIManager, DiskImages families | Signed update state, recovery transitions, firmware ownership, failure recovery |

Presence in a kernelcache establishes an available implementation. It does
not establish that a component ran during a particular failed transition.

## Storage and SEP

Host-visible ANS2 (`106b:2005`) and bridgeOS's internal NVMe controller
(`106b:2002`) belong to different interfaces. Reading the host root disk cannot
stand in for inspecting embedded namespaces. Namespace type and namespace ID
also have different meanings; the type field is at Identify Namespace offset
`0x180` in the analyzed embedded-storage ABI.

SEP owns services whose persistent state involves xART and gigalocker backing.
Those clients participate in shutdown and power coordination. Platform work
therefore needs to account for endpoint lifetime and storage acknowledgements,
even when fingerprint authentication is outside the task.

Detailed [SEP routing](research/sep-architecture.md)
and [embedded storage](research/boot-and-storage.md)
are maintained with the Touch ID research. The power-specific additions are
in [Power management](power-management.md#sep-and-persistent-clients).

## Peripherals and diagnostics

Input, Touch Bar, camera, and other devices depend on BCE/VHCI restoration.
Bridge audio has a separate PCI function and power driver. AOP exposes sensors
and low-power audio policy; portable and desktop configurations differ in
which children and codecs they publish.

BridgeOS userspace includes Remote Service Discovery, BridgeXPC, sysdiagnose,
restore/update services, and xART storage management. Diagnostic transport can
help correlate host and T2 events, but a normal-boot log is not evidence of the
firmware half of a failed Linux sleep cycle. The available boot/revive logs
showed SMC state traffic; no paired host/bridgeOS sleep trace was established.

Recovery and firmware update are distinct lifecycle transitions. Their service
presence does not establish a safe recovery operation for a hung Linux driver.
