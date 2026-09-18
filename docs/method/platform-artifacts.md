# Platform artifacts and method

[Research map](../README.md) · [Evidence catalog](../../catalog/README.md)

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
| Universal-wrapped portable kernelcache | `0cccc368af062081eb63a04839a181bf99cc2e7ed4bb765af6b98e7cc2a0a081` | 40,058,908-byte retained loader input; the first `0x1c` bytes are a wrapper |
| `Firmware/AOP/aopfw-t8012aop.RELEASE.im4p` | `98fbbc65a9df38553642633ba61e10b8d47917b1a8796b310c53128efb7ca211` | 373,229-byte signed T2 AOP member |
| Extracted AOP payload | `94d0b05a0213d9445ebf7f7ea0d4f0cf1e21bdcab2bc7590666c403c2cf25211` | 373,204-byte payload used for bounded code and string analysis |
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

The three firmware-file hashes immediately above were checked again on
September 18, 2026. That check verifies the retained analysis inputs; it does
not repeat the whole extraction or establish filesystem-wide integrity.

The graphics, audio, SMC, and input findings use these additional inputs. The
embedded AFUs are decoded payloads from the InputDevice XML, not separate IPSW
members.

| Artifact | Bytes | SHA-256 | Role |
| --- | ---: | --- | --- |
| `Firmware/all_flash/LLB.j152f.RELEASE.im4p` | 1,240,242 | `7f6a257756930a671199a150d3dc9d538dc042bae4ae96a1bf3a286dd08dfd6f` | Signed `illb` early-boot role |
| `Firmware/all_flash/iBoot.j152f.RELEASE.im4p` | 1,240,242 | `299c24cb28084bf16340af493e2b4f81a59e0b60e6a954c777eb8fd92e2e6433` | Signed `ibot` role and recovered boot-policy graph |
| `Firmware/dfu/iBEC.j152f.RELEASE.im4p` | 1,240,242 | `0e012371eb7dd6e4a4952e021e59a242e6b3624d2f654fdf14ea8daed86f208f` | Signed `ibec` recovery role |
| `Firmware/dfu/iBSS.j152f.RELEASE.im4p` | 1,240,242 | `713f7f07601a72339744a34c6696a8ce5831efc15a642f91efb0e5e8ecb83832` | Signed `ibss` DFU role |
| Common decompressed early-boot payload | 1,518,696 | `006ce52352e99f478c0a6f4fd52e136e21e1bce82625fdea8a3c75cc1fb8317f` | Byte-identical payload carried under all four role tags |
| `094-92961-079.dmg` | 117,440,539 | `6860590952a17c0d955ebf36032a34c2cb5359182cc36448a5d671694faa4860` | Erase restore ramdisk |
| `094-92985-079.dmg` | 119,537,691 | `53aab6179ea7f623b9c7edc48ecbefd5e33faebd14c6494b81e520235a4a69a7` | Update restore ramdisk and transactional updater inputs |
| Update-ramdisk `restored_update` | 2,301,104 | `18479a1199a63384075101ebe1c9a0ac15bdeea4f24ae3b624231228e10fcc94` | Outer NAND, MacEFI, iBoot, FDR, and SEP checkpoint ordering |
| `Firmware/MacEFI/J152F.RELEASE.im4p` | 8,388,633 | `f2d6ae5542ef43d1b604a3b65726d334943f1f4de1a62b165df4281275216295` | Signed J152f MacEFI container |
| Extracted `J152F.RELEASE.bin` | 8,388,608 | `0ee39543933c42f20ccbe94c7f368a07e8fbffd6d460e86aac3ab00e52e42cb7` | UEFI image from which the graphics modules were split |
| MacEFI `CoffeelakeGraphics` PE32 module | 66,564 | `936c705317cf4da6b661540b1c1ab7f00e543f997b3b9672ed0d198956f078d1` | J152 profile selection and panel-sequencer programming |
| MacEFI `GMUXDriver` PE32 module | 21,508 | `bd0b9d509689ce07fb2f57adbba0b1d6c6d12b800a7d73a5a2f6d6c755536223` | Display, AUX, external-route, and power/control writes |
| Recorded J152f ACPI `VFCT` table | 61,060 | `f9257a4107be89ca0f55f5c86eb6d8c618b681720f64301313e97ce1c72d3b62` | Navi 14 display-object and power-policy tables |
| AMD ROM slice from `VFCT` offset `0x68` | 60,928 | `d74c0eedfa8c47a5ab00724b07cb4f7a090dfb2bfdc20aa822417d3e0ecc7eab` | Exact ATOM image parsed in place |
| bridgeOS `bridgeaudiod` | 349,728 | `78cd726b849cfdde75c4664d1ba9ff6f2dcf83be7ee3f36ffc3bcc08a67d34da` | Bridge-audio framing and timestamp semantics |
| bridgeOS `AppleAOPAudioPlugin` | 264,128 | `9cf600c3d92a4b7a633cd818a43d4dc37443546c9be5ef595685e2822abe042e` | AOP ring-buffer, clock, and voice-trigger comparator |
| Embedded `AppleAOPAudio` 540.1 kext | — | Covered by the exact portable and desktop kernelcache hashes above | Host controller and live/historic mailbox callbacks |
| `Firmware/J152F_InputDevice.im4p` | 676,764 | `f52ead1efb8c5497b1ddf7c40ebd8fccfe017794be12704c4ee08e862ace8424` | Signed `ipdf` member; 676,739-byte OCTET STRING |
| Embedded InputDevice ST AFU | 419,208 | `a363a20b89c92dc212fa9ef3ab7be6794ecb6d4c2224e1b7ed23d51139cc080e` | Multitouch lifecycle, force, calibration, and bounded response analysis |
| Embedded InputDevice MT AFU | 74,404 | `0366e2f861c95374f70101576be9bb16aa73f76d84cf566afc5409c091cc1581` | Finger- and palm/thumb-object analysis |
| Update-ramdisk `AppleM8CameraInterface` | 1,010,240 | `b9eee795369ff50e6d7bfce5634eab7cbf4e8082e6a1c78e08babd505b1a9048` | Symbolized camera property and ISP-command implementation |
| `Firmware/J152f_Multitouch.im4p` | 89,811 | `1ce8a0dfc9e611ac262a93435f1be96c8c2c006ddb2722c76280817a7dbfe15a` | Signed `mtfw` member; 89,786-byte OCTET STRING |
| `DeviceTree.j215ap.im4p` | 31,389 | `d3181dbcd9c10c327d3914744227e4855861e34de660054b8bf5dd5e93463a30` | Signed sibling-board confirmation of the `las` policy |
| Decompressed J215 DeviceTree payload | 161,492 | `69d691df7e7f5c42b5587000ea78b1f439ac69f25d978e0eeee5228b3ee8a478` | Parsed sibling-board tree |
| Recorded `05ac:8104` USB descriptor stream | 52 | `2395a4fa7ec1d9cd87c99a6ade7c635572494af9a56e51798c100d21c0ecaef5` | Device and sole configuration descriptors |
| Recorded `05ac:8104` HID report descriptor | 179 | `baec17e4024defa3a53850ba6058a6dad83efef7f8df073fdf89b51f866693c5` | Linux-visible lid-angle report contract |

The signed kernelcaches also contain `AppleAVEBridge` 6.1/35 and `AppleAVE2`
9000.1.1. In the portable cache their executable text begins at VMs
`0xfffffff0065f3000` and `0xfffffff0069db000`; desktop equivalents begin at
`0xfffffff006617000` and `0xfffffff006b49000`. The bridge owns the exact four
parameter/callback queue names used by pinned KAiT2EN revision
`c38320d41f67e84f936dabe978cc4f8611587c24`. Build-matched `aveserverd` is
76,320 bytes with SHA-256
`6ef551a59fe9dc98b836a883a31c4ce0e738df363361c518438bb46ce06569df`;
`processData` at `0x1000035c8`, `processEncodeFrame` at `0x1000026ac`, and
`emitEncodedFrame` at `0x100001e74` bind command `0x02` and callback `0x0b` to
the public offsets. Retained `H9.videoencoder` is 1,032,192 bytes with SHA-256
`a36dfcf436a10bf13f32124819a9542b8f3aacbb235f8898ab114ff795f9070a` and
verifies exact `AppleAVE2Driver` before user-client access.

The retained diagnostic binaries identify the post-event observability path.
They are named here by binary and digest so that another researcher can
extract them from the same signed restore without redistributing Apple code.

| Binary or cache input | Bytes | SHA-256 | Decisive static anchor |
| --- | ---: | --- | --- |
| Update-ramdisk `RemoteXPC` | 236,896 | `153b8a7e73bbac4147c7cbfef952b428d7eff030f2c4fb06052df0c83e880eca` | Wire header strings at `0x20148`-`0x202e5` |
| dyld shared-cache main file | 81,920 | `3fb74aa24721529424ed405624b0b37ccac8ec8465743f3715cf0a29897c141c` | BridgeXPC symbols are virtual addresses in the complete split cache |
| `sysdiagnosed` | 648,080 | `3ca509c24c213897e913c1a0f3707bbb51054e8b5280e04553cedbf0b600e5a7` | Panic/stackshot strings at `0x5b2e0`-`0x5b37e`; watchdog tailspins at `0x5e042`-`0x5e0aa` |
| `diagnosticd` | 97,552 | `e6b3c7833fc4bf0a44d1a7b275921ed92622b2673321a2bef4c96383b6b64422` | `/dev/oslog_stream` at `0x562a`; `mach_timebase_info` import |
| `watchdogd` | 175,872 | `c94062edb8c82e60f467c933bc196f422cc9ca1c73684b2b8ed42f19ad18cd2e` | IOWatchdog connection/check-in/test strings from `0xdedc` |
| `DumpPanic` | 354,144 | `dc96979cbe2565201dbab448b666b41cd0140794d32ee36043d8c579a5e3902f` | Embedded panic headers, boot faults, and panic/stackshot length checks |
| `ReportCrash` | 370,784 | `5e1e5b50c19d3c7df8e38ac6f0e6e4a995404037a00eba653356dd2af816422f` | Watchdog-reason decoding, stackshot acquisition, and per-boot crash history |

For SEP application reconstruction, split-data handling, and protocol-specific
experiments, see [SEP artifacts and method](sep-artifacts.md).

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
| `AppleBridgeAudioController` | `33421fdd5c570f329c816baf31ba98c1c601112c2c325237aef959786a3f9a14` |
| `AppleMultitouchDriver` | `e35077ebe8c4abb26a6b32225afc423dbf87a85a18978a82282a86cb553559dc` |

`AppleEmbeddedOSSupportHost` is 60,256 bytes, `IOBufferCopyController` is
74,576 bytes, `AppleMuxControl2` is 123,080 bytes,
`AppleBridgeAudioController` version 650.1 is 114,824 bytes, and
`AppleMultitouchDriver` project `MultitouchSoftware-9460.1` is 256,896 bytes.
These host inputs differ from the macOS 15.7.9 / `24G830` artifacts used in
parts of the related Touch ID research. They also differ from bridgeOS itself.

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
The [board table](../platform/board-configurations.md#devicetree-identities) and
[machine-readable records](../../catalog/boards.json) give each DeviceTree member's
size and digest. Keep the bundle-inventory denominator separate from the
number of executable sections.

The J152f LLB, iBoot, iBEC, and iBSS containers each carry the same
LZFSE-compressed payload. Analyze the decompressed result as raw ARM64 with a
zero image base rather than trusting COFF autodetection. In that coordinate
system, selector-3 counter access is at `0x37080`-`0x373dc`, `/chosen`
publication at `0x27624`-`0x2767c`, the panic threshold at
`0x2300`-`0x23ec`, and the boot/panicmedic threshold at
`0x48250`-`0x48494`. Direct-branch scanning over the entire image confirms the
enumerated producer, getter, writer, and clear call sites; stripped helper
predicates and the selector backend remain unnamed.

The portable kernelcache is a universal-wrapped prelinked kernel, not an
`MH_FILESET`. Removing its `0x1c`-byte wrapper produces the 40,058,880-byte
payload hash in the firmware table. The kernelcache file offsets below use the
wrapped 40,058,908-byte input; virtual addresses use the loader mapping. AOP
offsets use the signed IM4P stream and are therefore `0x19` bytes after the
corresponding raw-payload offsets. Dyld addresses are virtual addresses in the
complete split cache, not offsets into its 81,920-byte main file.

For userspace firmware, extract `094-92905-079.dmg` from the IPSW, then use
7-Zip's APFS extraction to recover:

```text
System/Library/Extensions/IOUSBDeviceFamily.kext/PlugIns/AppleUSBVHCIFirmwareBCE.kext/AppleUSBVHCIFirmwareBCE
System/Library/Extensions/IOUSBDeviceFamily.kext/PlugIns/AppleUSBVHCIFirmware.kext/AppleUSBVHCIFirmware
System/Library/CoreServices/powerd.bundle/powerd
```

The same APFS extraction supplied `bridgeaudiod` and
`AppleAOPAudioPlugin`; identify the executables by name and require the sizes
and hashes above before analysis. For host comparators, extract the named
bundle executables from the matching RecoveryOS kernel collection and preserve
the kernel-collection mapping used for virtual addresses. A same-named binary
from another macOS or RecoveryOS build is not interchangeable.

Match the hashes above before disassembly. Exported C++ symbols in the VHCI
binaries provide entry points for radare2 inspection. Start with
`processInterrupts`, `hardwareException`, `smcNotification`,
`sendSystemMessage`, and `setPowerStateGated`. Follow both callers and callees,
and identify the side of the link that sends and receives each message.

For the MacEFI input, extract the signed `J152F.RELEASE.im4p` member, decompress
its LZFSE payload, and split the resulting UEFI image into modules. Match both
the whole-image and module hashes before using module-relative offsets. The
MacEFI image has no literal `$VBT`, `VFCT`, `ATOM`, or `AMD ATOMBIOS`
signature; this negative scan does not exclude encoded, compressed, generated,
or externally supplied data.

For the input packages, stream the two signed members from the IPSW and parse
their DER OCTET STRINGs. Each OCTET STRING is XML followed by one NUL byte.
Remove only that final byte for XML parsing and resolve each document's `ID`
and `IDREF` links. Base64-decode the two AFUs referenced by the InputDevice
document and match the signed-member and decoded-AFU hashes before following
offsets. The InputDevice XML supplies the updater operations, HIDSPI policy,
and report `0x7e`; the AFU offsets do not describe host HID reports.

The recorded VFCT and HID descriptor inputs are hardware observations rather
than restore members. Read the raw ACPI table or descriptor bytes without
changing device configuration, record the actual byte count returned, and
hash those bytes before parsing. The ATOM ROM begins at VFCT offset `0x68` in
the recorded J152f table. Descriptor hashes bind the documented observation;
they do not establish identical bytes on another board or firmware build.

## Disassembly anchors

The table's file offsets apply to the 40,058,908-byte universal-wrapped input,
SHA-256 `0cccc368af062081eb63a04839a181bf99cc2e7ed4bb765af6b98e7cc2a0a081`;
subtract `0x1c` to address the corresponding bytes in the 40,058,880-byte body,
SHA-256 `578530d4a6c57861de55320ff5ec5e11b14bf3f4b8e4eaa31cbcb76660bda2e9`.
Virtual addresses use the loader mapping and do not receive that adjustment.
Within the wrapped input, `AppleT8015DART` maps `__TEXT.__cstring` at file offset
`0x010b80c0` for `0xec6` bytes and `__TEXT_EXEC.__text` at virtual address
`0xfffffff006bd1000` for `0x5010` bytes. Use those section bounds before
following the stripped DART call graph.

| Path | Wrapped file offset (`0cccc…`) | Virtual address |
| --- | ---: | ---: |
| PMGR `ap-wake-sources` record loop | `0x0128483c` | `0xfffffff00602483c` |
| PMGR `ap-wake-source-flags` parser | `0x0128493c` | `0xfffffff00602493c` |
| PMGR `power-domains` record loop | `0x012878c0` | `0xfffffff0060278c0` |
| NVMe `systemPowerChange` | `0x01df7460` | `0xfffffff006b97460` |
| NVMe `SendSleepNotificationToANS` | `0x01df75b8` | `0xfffffff006b975b8` |
| DART `reloadConfiguration` string | `0x010b8ef8` | `0xfffffff005e58ef8` |
| DART outstanding-request warning | `0x010b8eaa` | `0xfffffff005e58eaa` |
| DART busy-timeout string | `0x010b932d` | `0xfffffff005e5932d` |
| DART outer reload/client callback | n/a | `0xfffffff006bd3c8c` |
| DART whole-controller reload body | n/a | `0xfffffff006bd3d5c` |
| VHCI `exception reported by host` string | `0x00c3b2b6` | `0xfffffff0059db2b6` |
| Watchdog external SMC-doorbell panic | `0x01101e36` | n/a |
| Watchdog extended IOKit-quiesce timeout | `0x01101d91` | n/a |
| Watchdog userspace timeout | `0x01102749` | n/a |

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

The graphics anchors use module-relative coordinates. In
`CoffeelakeGraphics`, the J152 profile is at file offset `0xf060`; the platform
ID selector is at `0x1744`-`0x1769`; and the direct PCH panel-sequencer writes
are at `0x2f85`-`0x2feb`. The five conditional `AAPL00,Panel*` publications
are at `0x2ed0`-`0x2f48`. In `GMUXDriver`, dispatch RVA `0x13a1` writes the
IGD route `(0x10,0x28,0x40)=(2,1,2)`, the DIS route `(3,2,3)`, and the
additional `0x50`/`0x58` control paths. This dispatch is a write primitive;
it has no semantic route readback, mux-interrupt wait, or rollback.

Within `AppleMuxControl2`, Config3 parsing is anchored by `S0iControl` at file
offset `0x12101`, `PowerUpDownSequence` at `0x1213f`, `SaveRootPort` at
`0x12167`, and `GPUMinimumOffTime` at `0x1218e`. The HDA/G3D save and restore
diagnostics span `0x10884`-`0x109c8`, while the switch gates, aborts, retries,
and timeouts span `0x11780`-`0x11b22`. These offsets reproduce the coupled
state-machine evidence, but the property values and private state numbers are
not a Linux ABI.

The hash-bound VFCT ROM has its ATOM ROM header at slice offset `0x2b6` and
master data table at `0x92ba`. `LCD_Info` begins at `0xc5ea`,
`DisplayObjectInfo` at `0xc6da`, and `PowerPlayInfo` at `0xcd4a`. Parse the
table revision and declared length before interpreting a body. These anchors
establish one eDP and four DP topology records and absent panel timing/link
fields in this image; they do not establish current gmux ownership.

The bridge-audio endpoint in the portable kernelcache has `saveGPRs()` at
`0xfffffff0064012a0`, `restoreGPRs()` at `0xfffffff006401338`, and
`setPowerState()` at `0xfffffff0064013fc`. Endpoint initialization writes the
five-word aperture at `0xfffffff006400c0c`-`0xfffffff006400d04`; the restore
loop write is at `0xfffffff006401394`. In the host comparator,
`BridgeAudioPCI::initWithBaseAddresses` is at `0x00b8b2ca`, buffer remapping at
`0x00b8cc60`, and the sole recovered host `gprWrite32` call at `0x00b8cdba`.
Together these sites distinguish endpoint-owned words 0-3 from the host-owned
word-4 sleep cookie; they do not prove allocation lifetime across a Linux
power transition.

In `bridgeaudiod`, the receive path at VM address `0x10001b6a4` bounds the
13-byte outer envelope. `BridgeAudioMessageUpdateTimestamp` parses its three
eight-byte fields at `0x100012384` and serializes them at `0x100012508`; the
callback that advances or resets binary64 `sampleTime` is at `0x1000085a4`.
The complete command is 45 bytes. These anchors establish the accumulated
frame-position field, not the device timestamp's unit or a present audible
failure.

The AOP channel-control result uses raw-payload coordinates. Property selector
`0xc9` is bounded by its getter at `0x1b7c4`-`0x1b7e6` and setter at
`0x1b946`-`0x1b966`; both require at least 16 bytes. The four named 32-bit
masks are supported, enabled, voice-trigger, and history channels. Add `0x19`
to convert these raw-payload offsets to signed-IM4P offsets.

The bounded controller dispatcher at raw offset `0x1b0d8` has its common
return at `0x1b410`, out-of-line errors through `0x1b694`, and literal pool
through `0x1b710`. Outer command `0x20` accepts a control `SubPacket` of at
least 36 bytes. Its type is the 32-bit word at `+0x04`, its declared length is
at `+0x1c`, inline command data begins at `+0x24`, and its accepted types are
the contiguous range `0xc3000000` through `0xc3000007`. Commands `0x25` and
`0x26` accept 40-byte client-power and 32-byte haptic requests. This controller
function reads no timestamp. In the rehydrated portable `AppleAOPAudio` text,
`historicalDataCallback` is at `0xfffffff006c7e170` and `serviceCallback` at
`0xfffffff006c7e3dc`; desktop equivalents are `0xfffffff0068a5170` and
`0xfffffff0068a53dc`. Both recover packed `SpuMCAPacket` as a 20-byte header:
`u64 timestamp`, `u64 byteCount`, `u32 totalSize`, then payload. Service type 1
carries live data; type 5 nests this packet after the 36-byte `SubPacket`.
These callbacks prove framing and bounds, not the timestamp's producer-side
unit.

The AppleSMC notification analysis uses the same portable-kernelcache mapping.
Its `__TEXT.__cstring` region begins at wrapped file offset `0x00c13768`
(`0x00c1374c` in the unwrapped body) and is `0x7437` bytes long. The queue drain
at `0xfffffff0061dbaa8` calls the dispatcher at
`0xfffffff0061dc90c`; the latter reads only message bytes 4-7. The system-state
name table is consumed at `0xfffffff0061f2748`, and the power-state and system-
control pointer tables are at `0xfffffff006e29b78` and
`0xfffffff006e29c28`. The quiesce path constructs the four-byte `MBSE` read at
`0xfffffff0061e67c0` and the one-byte `NTAP` write at `0xfffffff0061e6880`;
the one-byte `BNOC` read/write pair is at `0xfffffff0061ee1a8` and
`0xfffffff0061ee244`. AppleSSM event processing at
`0xfffffff006c9dbe4` binds byte 6 as selector and byte 5 as the target-state
index for `system-state-change`. IOAccessory accessors at
`0xfffffff0061266ec` and `0xfffffff0061266f4` name resolved current and
voltage; their serializer labels mA/mV. The `D%dSC` constructor at
`0xfffffff0061efeb8`-`0xfffffff0061eff48` emits seven four-byte
current/voltage PDO records, and `D%dos` is assembled at
`0xfffffff0061f034c`-`0xfffffff0061f038c`. The charger retrieves declared key
types only through a runtime key-info vmethod and does not retain that field.

The embedded portable `AppleSPU` Mach-O begins at unwrapped kernelcache offset
`0x00c44fc0`. Its `__TEXT_EXEC.__text` is at VM
`0xfffffff0062aa000`, size `0x2cdd0`, offset `0x0150a000`. Accelerometer
property setup is at `0xfffffff0062cfc84`-`0xfffffff0062cfcd8`; the bounded
generic property packet callback is `0xfffffff0062d5820`. The timesync callback
at `0xfffffff0062b87e0` accepts message `0xe3ff8100` and exactly 24 bytes;
worker `0xfffffff0062b8864` produces report ID `0xb0` plus two `u64` values.
These anchors establish host selectors, widths, and framing, not the dynamic
endpoint assignment or producer-side sample/time units.

Both kernelcaches contain `AppleH9CameraInterface` 7.8.0; desktop executable
text begins at VM `0xfffffff006097000`. In the symbolized ramdisk framework,
`SetCameraProperty` is at `0x18a4`, `SetExposureBias` at `0x6db4`, and
`ISP_SendCommand` at `0x24c8`. For command conversion, property 0 substitutes
`0.0` for inputs outside inclusive `[-3,3]`, computes `exp2` of the working
value, and encodes it as 16-bit Q8 in a 20-byte opcode-`0x0204` command sent
through IOKit selector 7; on success, `SetCameraProperty` caches the original
input. The bounded desktop kernel gate at
`0xfffffff0060a2c40` is identified independently; the selector-7 dispatch-table
edge remains unproven. These anchors establish an internal userspace command
path and a separate kernel gate, not a host-callable UVC selector or
privacy-LED owner.

The input anchors use two coordinate systems. In the host comparator,
`AppleMultitouchHIDEventDriverV2::handleInterruptReport` is at
`0xffffff8001bd0b78`, the raw touch-frame path is at
`0xffffff8001bc41de`/`0xffffff8001bc4226`, report `0x50` handling is at
`0xffffff8001bc728c`, and report `0x60` status handling is at
`0xffffff8001bc6f76`; availability gating is at `0xffffff8001bd0d3c`.
In the decoded ST AFU, the bounded `eb`/`e1`/`ea` path-response helper begins
at VM address `0x08020d40` (raw offset `0x20d40`). Its three direct calls are
at `0x080221ea`, `0x08022462`, and `0x08024bfc`; the normal and recovery paths
independently seed `0x6d9` as caller capacity. The inner header begins at
buffer `+5`, the accepted payload is moved back to the buffer base, and the
returned length is the inner length minus its two checksum bytes. In the
decoded MT AFU, `FingerCluster` is at
string offset `0xd784`, `PalmThumbCluster` at `0xdb20`, and the recovered
record comparison spans `0xd7b2`-`0xd85c` with a `0x130`-byte internal stride.
The host addresses bound report admission and lifecycle handling; the AFU
offsets are internal firmware structures and must not be reused as the opaque
144-byte contact-report layout.

The declarative input anchors do not require disassembly. In the InputDevice
XML, reports `0xb0`-`0xb3` define initialization, chunk transfer, commit/status,
and reset. The exact fixed payloads are aggregate initialization `b0 c3 bc`,
per-target initialization `b0 62 72`, target commit `b2 00`, status query
`b2 a1`, aggregate commit `b2 c3 bc`, and reset `b3`. Interface 2 declares
report `0x7e` as 65 bytes: one report-ID byte followed by sixteen four-byte
counters at offsets 1 through 61. In the J152f and J215 DeviceTrees,
`/arm-io/aop/iop-aop-nub/las` carries
`device_type = "las"`, `hidrelay-enable = 1`, and
`lid-angle-sensor-calibration = "syscfg/LASC"`. The signed AOP member places
`MA781.cpp`, `MagAlpha`, and `ma781` at signed-member offsets `0x34a47`,
`0x34aa4`, and `0x34aad`, immediately before the LAS-calibration diagnostic at
`0x34ab3`. The 179-byte HID descriptor independently declares report 1 as a
9-bit Input value with logical and physical range 0-360. A bounded J152f
observation then opened the current hidraw node read-only and issued one
GET-only `HIDIOCGFEATURE(8)` for report ID 1; it returned length 3 and
`01 6d 00`, or 109 whole degrees. This proves that the current Linux personality
accepts Feature GET without stimulus or state change. The static sources still
do not explain why that transaction is accepted despite the Input declaration.

The stripped DART call graph is bounded by the two virtual addresses in the
table. The outer function conditionally calls the reload body, marks the
controller state field at object offset `+0xc24`, then invokes each registered
client through vtable offset `+0xb0`. The reload body iterates the controller
count at object offset `+0x1148`, the SMMU count at `+0xf88`, compares active
stream state across two
SMMUs through helper `0xfffffff006bd5758`, and finishes each SMMU through
helpers `0xfffffff006bd5ab0` and `0xfffffff006bd57b0`. These observations prove
controller-wide iteration and client notification. They do not justify naming
the stripped helpers as individual invalidate or enable operations.

The diagnostic framing anchors use two layers. `RemoteXPC` names
`remote_wire_header` at string offset `0x20148`, its four fields at
`0x2017b`-`0x201a3`, and `REMOTE_WIRE_MAGIC` at `0x201ae`. In the complete
split dyld cache, `+[BridgeXPCConnection HELOMessage]` is at `0x186fc6d50`,
`-[BridgeXPCConnection readMessage]` at `0x186fc7bd0`,
`-[BridgeXPCConnection processIncomingMessage:]` at `0x186fc8404`, and
`-[BridgeXPCConnection writeHeader:message:]` at `0x186fc8f70`. Short-header,
magic, version, size, short-body, and deserialization failures are separately
rejected at cache addresses `0x186fcc563` through `0x186fcc878`.

The retained remote sysdiagnose contract advertises
`com.apple.sysdiagnose.remote` and its trusted variant. A request uses
`MSG_TYPE=1` and `REQUEST_TYPE=1`; success uses `MSG_TYPE=2` and
`RESPONSE_TYPE=1`, while failure uses `RESPONSE_TYPE=2`. The service announces
the file on stream 1, duplicates the requested reply on stream 3, and sends the
payload on stream 2. A 24-byte RemoteXPC wrapper precedes the gzip stream, but
the announced `FILE_TX` length counts only the archive. Preserve those layers
when validating a capture.

The signed AOP IM4P provides bounded sensor anchors without establishing a
wire ABI: `AppleImuSensor.cpp` at `0x34db6`, versioned `calibration3` at
`0x34dc9`, endpoint enable/routing at `0x34e03`-`0x34e22`, missing `systick`
handling at `0x34e83`, timestamp/sample tracking at `0x34ea4`, historical
delivery at `0x34f13`, property get/set rejection at `0x35170`-`0x351c5`, and
the `accel`, `gyro`, and `systick` service registry at `0x356d6`-`0x35734`.
Those are signed-IM4P offsets under the coordinate rule above.

## Linux comparison

The September 18 source check resolved upstream
[t2bce](https://github.com/deqrocks/t2bce/tree/a973d53c8278e9db5ff8314b816d6880309ed39e)
to `a973d53c8278e9db5ff8314b816d6880309ed39e`. The inspected
`bce_vhci_handle_system_event()` has no dedicated `0x50` case.
Historical `apple-bce-drv` limitations do not describe this replacement stack;
comparisons must name the implementation and revision.

The lifecycle review used these exact files at that revision:

| Source file | SHA-256 | Decisive bounds |
| --- | --- | --- |
| `t2bce_dma/queue.c` | `358824a708bc6ec4cac0fcb39aafc0523411ef6473e5787a69e1b0d1dcc3bbfd` | management opcode `0x50` at line 42; completion-index handling at lines 101-149; slot generations and timeout retirement at 313-403 |
| `t2bce_vhci/queue.c` | `81c0ff9a38bf7c5dd90ee472a14fa73ac5c61fa805a9fd7d5a799b111f4fb5cb` | command matching, cancellation, and timeout at lines 211-265 |
| `t2bce_vhci/queue.h` | `c33ac9119503c605edbab28ff9b33245de7c7b6131894a7697b8b4c5ca64c370` | 16-byte VHCI message and queue depths at lines 7-29 |
| `t2bce_vhci/vhci.c` | `fad23faeb8159c2546e62c2ca94957b53c1eb833570b923d91d344c9fdf6f801` | virtual-device reset at lines 570-617; no-state resume at 734-773; queue registration at 946-990; event dispatch at 1004-1188 |
| `t2bce_vhci/transfer.c` | `4c6ec4d63d1f7bd8f9bdcdb721022ba7de81a3c15f1ef5177e56e1180306f53c` | deferred events and completion accounting at lines 216-343; endpoint reset at 560-599 |

The retained `drivers/iommu/apple-dart.c` comparator came from a preserved
Linux 7.2.4 source tree and has SHA-256
`c8ef00b55aeb66eb27176f234a89e3b322bb19235bdb6ae8dba1ae28a99eaad6`.
`apple_dart_hw_reset()` is at lines 465-494, mapping setup at 570-585, and
resume restoration at 1327-1361. Its match table covers `t8103`,
`t8103-usb4`, `t8110`, and `t6000`, not bridgeOS `dart,t8015`; it is an
ordering comparator, not the x86 T2 DART owner. The experiment package inputs
remain separately pinned to `linux-t2-arch`
`7b97124fa886ed5abbf5a35022fe70d4661a76e8` and `linux-t2-patches`
`794069f7015e25d62da420e2748daaac0813cedc`.

Installed-module identity and package inputs were retained separately in the
original experiments. The [case study](../power/linux-suspend-observations.md) identifies the
versions and explains its evidentiary limits. It does not claim that every
function in the research checkout was the exact installed implementation.

## Corrected interpretations

| Earlier interpretation | Evidence that changes it | Supported conclusion |
| --- | --- | --- |
| ANS sleep opcode remains unknown | ARM64 branch and command-object analysis | `0x309` negotiates ordinary sleep; `0x30a` reports cancellation; S4 chronology remains open |
| APP7777 coordination applies to J152f | Provider requirement and examined ACPI namespace | Keep it as a separate comparator |
| Event `0x50` directly explains Linux desynchronization | Apple consumes a host-reported VHCI exception; Linux separately reserves an unused BCE management opcode `0x50`; the retained incoming event lacks its outer queue record | Numeric equality is not wire equivalence; the producer and corrective recovery remain unproven |
| BCE status 0 means the machine resumed | Host failures and a delayed VHCI completion after successful BCE transactions | Component success is narrower than usable wake |
| PMGR records differ by board | Byte comparison across the 16 DeviceTrees | These arrays match in `23P6068`; other policies differ |

## Limits of reproduction

Static findings can be checked against the named artifacts. Runtime conclusions
remain scoped to recorded experiments. There is no paired Apple-host/bridgeOS
trace for a failed Linux transition, no host ACPI survey of the other 15 boards,
and no established successful MacBookPro16,1 hibernate baseline in this work.
The public XNU sources explain constants and ordering mechanisms; they are not
an exact source reconstruction of the analyzed proprietary binaries. Printable
firmware strings establish code and failure vocabulary, not numeric endpoint
IDs, property selectors, report layouts, timestamp units, or proof that a path
ran on J152f. Reproduce offsets only against the exact hashes and coordinate
systems above.
