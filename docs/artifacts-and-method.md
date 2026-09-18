# Artifacts and method

The research combines signed firmware analysis, Apple host-driver comparison,
Linux source inspection, and hardware observations. Each supports a different
claim. A method name or string shows an implementation exists; a recovered
branch explains a mechanism; a trace shows that a path ran under stated
conditions. Cross-source agreement supports an inference, not an unobserved
hardware result.

## Firmware identities

The bridgeOS input is the 742,609,165-byte multi-product restore image for
bridgeOS 10.6 build `23P6068`. Its manifest contains 32 erase/update identities
for 16 production boards, all chip `0x8012`.

| Artifact | SHA-256 | Role |
| --- | --- | --- |
| BridgeOS 10.6 `23P6068` IPSW | `da1ce0198ee23d38a6d065e296fed3f302ff79b196c14107ab59ea191028206a` | Signed multi-board source |
| `BuildManifest.plist` | `8c9b5d0a2440dd6794bde7bd65303ec9a53093dd44a809684e1a90162f3f64e3` | Contains 32 erase/update identities for 16 production boards, all chip `0x8012` |
| Signed `kernelcache.release.ibridge2d` member | `06c8c0c67fa8e17c30436e941a1eebdc6af5db51e1a84bb87ef704dea723d4c6` | 13,626,330-byte desktop IM4P member |
| Signed `kernelcache.release.ibridge2p` member | `c773c9274c148ddec9f8361760ffbec42008f04054c67225c3ad10182d1430f9` | 14,113,607-byte portable IM4P member |
| Decompressed desktop kernelcache | `983a6886e8ae62af74e9e01e257b74aef2c4b1f3b69ff62c01a3b0f1a7299247` | 38,338,560 bytes; 181 bundle entries |
| Decompressed portable kernelcache | `578530d4a6c57861de55320ff5ec5e11b14bf3f4b8e4eaa31cbcb76660bda2e9` | 40,058,880 bytes; 190 bundle entries |
| `DeviceTree.j152fap.im4p` | `61500d42f0cc3bbe4a0b113f472500e28979dec8c6a1d1bc3a8b69f2356f7e69` | Exact model power/topology policy |
| Decompressed J152f DeviceTree payload | `21de7760beea1b85ae625e10a22527fc02cc8479e1732646b66234350b059002` | 161,608-byte parsed tree |

The APFS system-image member `094-92905-079.dmg` has SHA-256
`bc75d2db33c4a04e56076418b3b172533217206f174cece6aa9e340c34781777`.
Direct extraction from the IPSW and then the DMG reproduced the analyzed
firmware files:

| Binary | Bytes | SHA-256 |
| --- | ---: | --- |
| `AppleUSBVHCIFirmwareBCE` | 111,120 | `b6e0a057b48beac2d5d3fc9b932c3992420afd0fd1fe7a4f966be810629bbabc` |
| `AppleUSBVHCIFirmware` | 450,432 | `3e3f0ec25dffa6aa54e2017d2286ba34ce977efdf5beac6973f86d0f3d8e1db4` |
| BridgeOS `powerd` | 487,952 | `a200cde55ea269f2f4be6bd3b84eb6c2c4580637b928f2acaeb8844dfcb6aa3e` |

The three extracted-file hashes were checked again on September 18, 2026 and
matched this table. That check verifies the retained analysis inputs; it does
not repeat the whole extraction or establish filesystem-wide integrity.

For SEP application reconstruction, split-data handling, and protocol-specific
experiments, see [SEP artifacts and method](research/artifacts-and-method.md).

## Apple host comparator

The host comparison uses RecoveryOS 26.6.2 build `25G83`, whose kernel
collection reports Darwin 25.6.0 / xnu-12377.161.14~5.

| Artifact | SHA-256 |
| --- | --- |
| `BootKernelExtensions.kc` | `c80161fa3065883753fc285339281361a8469cbb6fb27653c88e2a22eb4807a4` |
| `BaseSystemKernelExtensions.kc` | `60d3f43f1a23847aa8b60b7c57153fd93d20d0653c116d14da4875f09e5d2f04` |
| `AppleEmbeddedOSSupportHost` | `feb208e39508270e34515be0d53efe4f31a470c29dcc7dd2c7d7dcd3ff87fac3` |
| `IOBufferCopyController` | `f140cbfa8d032469c18362158de49d3a53e017a6f828908dc9ffe9015a6a5fd0` |
| `AppleMuxControl2` | `6d3c84a94625a20f8f97cc1b854a7c9880907386d112519ed7f37fd1c5dfaed5` |

`AppleEmbeddedOSSupportHost` is 60,256 bytes, `IOBufferCopyController` is
74,576 bytes, and `AppleMuxControl2` is 123,080 bytes. These host inputs differ
from the macOS 15.7.9 / `24G830` artifacts used in parts of the related Touch ID
research. They also differ from bridgeOS itself.

## Reproducing the inventory

Obtain the matching Apple restore image and verify its size and SHA-256 before
comparing offsets. Read its `BuildManifest.plist` to select the board identity,
DeviceTree member, and kernelcache class. Parse each production board rather
than extrapolating from J152f.

The analysis used [ipsw](https://github.com/blacktop/ipsw) revision
`cdbc3a57114b5b240d23b00aa29cfad4d1f1d3fd`. The following command forms recover
the DeviceTree and kernelcache inventory; supply the selected board and local
artifact paths:

```text
ipsw dtree -j -f <board-config> <23P6068.ipsw>
ipsw extract --kernel -o <output-directory> <23P6068.ipsw>
ipsw kernel kexts -j <decompressed-kernelcache>
```

Compare signed IM4P hashes before decompression and payload hashes afterward.
The [board table](board-configurations.md#devicetree-identities) and
[machine-readable records](../data/boards.json) give each DeviceTree member's
size and digest. Keep the bundle-inventory denominator separate from the
number of executable sections.

For userspace firmware, extract `094-92905-079.dmg` from the IPSW, then use
7-Zip's APFS extraction to recover:

```text
System/Library/Extensions/IOUSBDeviceFamily.kext/PlugIns/AppleUSBVHCIFirmwareBCE.kext/AppleUSBVHCIFirmwareBCE
System/Library/Extensions/IOUSBDeviceFamily.kext/PlugIns/AppleUSBVHCIFirmware.kext/AppleUSBVHCIFirmware
System/Library/CoreServices/powerd.bundle/powerd
```

Match the hashes above before disassembly. Exported C++ symbols in the VHCI
binaries provide entry points for radare2 inspection. Start with
`processInterrupts`, `hardwareException`, `smcNotification`,
`sendSystemMessage`, and `setPowerStateGated`. Follow both callers and callees,
and identify the side of the link that sends and receives each message.

## Disassembly anchors

The following offsets apply to the decompressed portable kernelcache hash
above. File offsets and virtual addresses are different coordinate systems.

| Path | File offset | Virtual address |
| --- | ---: | ---: |
| PMGR `ap-wake-sources` record loop | `0x0128483c` | `0xfffffff00602483c` |
| PMGR `ap-wake-source-flags` parser | `0x0128493c` | `0xfffffff00602493c` |
| PMGR `power-domains` record loop | `0x012878c0` | `0xfffffff0060278c0` |
| NVMe `systemPowerChange` | `0x01df7460` | `0xfffffff006b97460` |
| NVMe `SendSleepNotificationToANS` | `0x01df75b8` | `0xfffffff006b975b8` |

In the separate `AppleUSBVHCIFirmwareBCE` Mach-O, the recorded offsets are
`smcNotification` at `0x4948`, `sendSystemMessage` at `0x4dc8`,
`reportSystemWakeEvents` at `0x4e24`, and `smcNotifier` at `0x4e94`.
In `AppleUSBVHCIFirmware`, `setPowerState` is at `0x15d70`, the gated routine
at `0x15db0`, and base `sendSystemMessage` at `0x1bdb4`.

Host comparator anchors for `AppleEmbeddedOSSupportHost` are virtual addresses:
`start` at `0x6f5a04`, `sleepWakeHandler` at `0x6f6082`, `notifyRemoteNode` at
`0x6f6b08`, `m8QuiesceCheck` at `0x6f71ce`, and `m8FailureHandler` at
`0x6f5e72`. Reconstruct the kernel-collection mapping before using them with an
extracted file.

The recovered host BCE policy is anchored by `IOBufferCopyController`'s
`sendSleepMessage` and wake path; host graphics policy by the J152f `Config3`
personality in `AppleMuxControl2`. These are build-bound analysis anchors,
not callable interfaces or stable ABI addresses.

## Linux comparison

The September 18 source check resolved upstream
[t2bce](https://github.com/deqrocks/t2bce/tree/a973d53c8278e9db5ff8314b816d6880309ed39e)
to `a973d53c8278e9db5ff8314b816d6880309ed39e`. The inspected
`bce_vhci_handle_system_event()` has no dedicated `0x50` case.
Historical `apple-bce-drv` limitations do not describe this replacement stack;
comparisons must name the implementation and revision.

Installed-module identity and package inputs were retained separately in the
original experiments. The [case study](suspend-observations.md) identifies the
versions and explains its evidentiary limits. It does not claim that every
function in the research checkout was the exact installed implementation.

## Corrected interpretations

| Earlier interpretation | Evidence that changes it | Supported conclusion |
| --- | --- | --- |
| ANS sleep opcode remains unknown | ARM64 branch and command-object analysis | `0x309` negotiates ordinary sleep; `0x30a` reports cancellation; S4 chronology remains open |
| APP7777 coordination applies to J152f | Provider requirement and examined ACPI namespace | Keep it as a separate comparator |
| Event `0x50` directly explains Linux desynchronization | Firmware and host receive paths have different directions | An exception-path lead exists; wire equivalence and corrective recovery remain unproved |
| BCE status 0 means the machine resumed | Host failures and a delayed VHCI completion after successful BCE transactions | Component success is narrower than usable wake |
| PMGR records differ by board | Byte comparison across the 16 DeviceTrees | These arrays match in `23P6068`; other policies differ |

## Limits of reproduction

Static findings can be checked against the named artifacts. Runtime conclusions
remain scoped to recorded experiments. There is no paired Apple-host/bridgeOS
trace for a failed Linux transition, no host ACPI survey of the other 15 boards,
and no established successful MacBookPro16,1 hibernate baseline in this work.
The public XNU sources explain constants and ordering mechanisms; they are not
an exact source reconstruction of the analyzed proprietary binaries.
