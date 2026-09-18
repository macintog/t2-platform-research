# Platform architecture

[Research map](../README.md#bce) · [Evidence catalog](../../catalog/README.md)

The T2 combines host-facing PCI devices with an embedded operating system,
coprocessors, storage, and peripheral controllers. Linux sees several device
functions; bridgeOS coordinates a larger set of power and reset dependencies.

## Host and firmware boundaries

```text
Intel host: ACPI / PCI / GPU / physical USB / system power management
    |
    +-- T2 upstream PCIe link
            +-- function 0: ANS2 host storage      (DART stream 1)
            +-- function 1: BCE and virtual USB    (DART stream 0)
            +-- function 2: SEP transport          (DART stream 2)
            +-- function 3: bridge audio           (DART stream 3)

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

The signed DeviceTrees place all four functions on one `apcie-up,t8012` x4
Gen2 link with explicit PERST. BridgeOS `AppleT8015DART` has a
controller-wide reload path: it visits every controller and SMMU instance,
compares active stream state across paired SMMUs, then invokes each registered
client. The Linux host therefore has two distinct recovery boundaries. It can
rebuild BCE function state while the link and stream 0 remain valid, or a
platform owner can coordinate the shared link, all four clients, and streams
`1/0/2/3`. A VHCI-local error handler cannot safely infer the second boundary.

The [board matrix](board-configurations.md) describes all 16 configurations in
`23P6068`. The [host coordination reference](../graphics/acpi-and-gpu-ownership.md) establishes
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
| Audio and AOP | AppleBridgeAudio, AppleBridgeAudioPCIEP, BridgeAudioCommunication, AppleAOPAudio, AppleAOPVoiceTrigger, AppleARMIISAudio, codec drivers | Separate PCI function, low-power microphone, endpoint-owned GPR restore, host-side mapping revalidation, codec shutdown |
| Camera, display, and media | AppleH9CameraInterface, ISP, IOMobileGraphicsFamily, AppleSynopsysMIPIDSI, AppleSummitLCD, AppleAVE/AVE2, AppleJPEGDriver, scaler | Gated media domains, late completions, high-bandwidth VHCI use, panel/Touch Bar output |
| USB, accessories, and networking | AppleEmbeddedUSB, AppleSynopsysOTGDevice, IOUSBHost/Device families, AppleUSBDeviceNCM/Mux, AppleUSBEthernetDevice, AppleBCMWLANUart, accessory families | PHY power, USB role, CDC-NCM diagnostics, restore/recovery transport |
| Firmware/update/recovery support | AppleFirmwareUpdateKext, AppleEmbeddedPUPConfigMgmt/FirmwareService, MacEFIManager, DiskImages families | Signed update state, recovery transitions, firmware ownership, failure recovery |

Presence in a kernelcache establishes an available implementation. It does
not establish that a component ran during a particular failed transition.

## Reset and queue boundaries

BCE/VHCI uses several reset scopes. They solve different failures and should
not be treated as interchangeable recovery calls.

| Scope | Existing Linux operation | Boundary |
| --- | --- | --- |
| Endpoint | Flushes one endpoint's transfer queues, resets it, and clears stall | Does not rebuild system or command event queues |
| Virtual USB child or port | Destroys and recreates one device and its endpoint queues around a port reset | Leaves controller-wide message and event queues intact |
| HCD no-state resume | Forgets children, restarts the controller, cycles virtual-port power, and reports root-hub lost power | Retains the allocated host message/event queue graph |
| BCE PCI function | Full teardown and reprobe reconstructs BCE command, VHCI message/event, and transfer queues | Assumes the shared link and DART stream 0 are valid |
| Shared T2 link | Coordinated PERST and DART reload | Affects ANS2, BCE, SEP, audio, and streams `1/0/2/3` |

The low-level BCE management command queue protects timed-out slots with a
per-slot generation. The 16-byte VHCI messages, command waiter, deferred USB
events, and transfer completions have no corresponding epoch. A late reply can
therefore match a later command with the same 16-bit command number. A bounded
local recovery design needs a VHCI epoch, function quarantine, complete queue
rebuild, and one explicit escalation point to the platform-level owner. It
should not loop queue registration or jump directly from an endpoint fault to
shared PERST.

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

Detailed [SEP routing](../sep/services-and-mailboxes.md)
and [embedded storage](../storage/sep-persistence-and-nvme.md)
are maintained with the Touch ID research. The power-specific additions are
in [Power management](../power/sleep-wake-and-hibernate.md#sep-and-persistent-clients).

## Peripherals and diagnostics

Input, Touch Bar, camera, and other devices depend on BCE/VHCI restoration.
Bridge audio has a separate PCI function and power driver. AOP exposes sensor
services and a distinct low-power microphone/history subsystem. J152f and J215
also publish a `las` child with HID relay and `LASC` calibration policy; the
signed AOP image groups LAS calibration with MA781/MagAlpha code. Together
with the matching public and Linux `05ac:8104` observations, this strongly
infers the lid-angle route, but DeviceTree does not encode the USB product ID
and the owning relay parser is not retained. This lid-angle evidence does not
define the accel/gyro/pressure ABI.

BridgeOS userspace includes Remote Service Discovery, BridgeXPC, sysdiagnose,
restore/update services, and xART storage management. Diagnostic transport can
request a constrained sysdiagnose containing unified logs, panics, stackshots,
watchdog tailspins, and crash reports. That makes it a post-event attribution
path. It is not synchronous recovery: if the shared PCIe or CDC path is down,
collection must wait for transport to return. A normal-boot log is not evidence
of the firmware half of a failed Linux sleep cycle. The available boot/revive
logs showed SMC state traffic; no clock-correlated host/bridgeOS transition has
yet been captured.

Recovery and firmware update are distinct lifecycle transitions. Their service
presence does not establish a safe recovery operation for a hung Linux driver.
