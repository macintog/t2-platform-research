# Board configurations

[Research map](../README.md#boards) · [Evidence catalog](../../catalog/README.md)

The bridgeOS `23P6068` restore contains 32 BuildManifest identities: erase and
update variants for 16 production boards. Each board's signed DeviceTree was
parsed separately. Product type, board ID, kernelcache selection, and policy
values come from the manifest and DeviceTree. Human-readable Mac model mappings
use [The Apple Wiki T2 matrix](https://theapplewiki.com/wiki/T2) as a secondary
cross-reference; firmware selection uses the manifest identity.

## Production matrix

| iBridge | Board / BDID | Mac cross-reference | KC | `min-sleep-state` | AOP child profile | SPI multitouch | Codec `PowerOffAtSleep` |
| --- | --- | --- | --- | ---: | --- | --- | --- |
| `iBridge2,1` | `J137AP` / `0x0A` | iMacPro1,1 | `ibridge2d` | 6 | base, no SMC control | no | no |
| `iBridge2,3` | `J680AP` / `0x0B` | MacBookPro15,1 | `ibridge2p` | 2 | base + SMC control | yes | yes |
| `iBridge2,4` | `J132AP` / `0x0C` | MacBookPro15,2 | `ibridge2p` | 1 | base + SMC control | yes | yes |
| `iBridge2,5` | `J174AP` / `0x0E` | Macmini8,1 | `ibridge2d` | 2 | base, no SMC control | no | yes |
| `iBridge2,6` | `J160AP` / `0x0F` | MacPro7,1 | `ibridge2d` | 2 | no published child services | no | no |
| `iBridge2,7` | `J780AP` / `0x07` | MacBookPro15,3 | `ibridge2p` | 2 | base + SMC control | yes | yes |
| `iBridge2,8` | `J140kAP` / `0x17` | MacBookAir8,1 | `ibridge2p` | 1 | base + SMC control | no | no |
| `iBridge2,10` | `J213AP` / `0x18` | MacBookPro15,4 | `ibridge2p` | 1 | base + SMC control | yes | yes |
| `iBridge2,12` | `J140aAP` / `0x37` | MacBookAir8,2 | `ibridge2p` | 1 | base + SMC control | no | no |
| `iBridge2,14` | `J152fAP` / `0x3A` | MacBookPro16,1 | `ibridge2p` | 1 | base + SMC control + LAS | yes | yes |
| `iBridge2,15` | `J230kAP` / `0x3F` | MacBookAir9,1 | `ibridge2p` | 1 | base + SMC control | no | no |
| `iBridge2,16` | `J214kAP` / `0x3E` | MacBookPro16,2 | `ibridge2p` | 1 | base + SMC control | yes | yes |
| `iBridge2,19` | `J185AP` / `0x22` | iMac20,1 | `ibridge2d` | 2 | base, no SMC control | no | no |
| `iBridge2,20` | `J185fAP` / `0x23` | iMac20,2 | `ibridge2d` | 2 | base, no SMC control | no | no |
| `iBridge2,21` | `J223AP` / `0x3B` | MacBookPro16,3 | `ibridge2p` | 1 | base + SMC control | yes | yes |
| `iBridge2,22` | `J215AP` / `0x38` | MacBookPro16,4 | `ibridge2p` | 1 | base + SMC control + LAS | yes | no |

“Base” means the published AOP children `accel`, `aop-audio`, `gyro`, and
`pressure`. LAS denotes the lid-angle sensor service. It is distinct from
always-listening voice trigger under `aop-audio`: nine boards advertise that
audio capability without a `las` child. An absent DeviceTree child establishes
a configuration difference, not the absence of a silicon block.

`min-sleep-state` is an internal bridgeOS policy enum. Values 1, 2, and 6 must
not be relabeled as ACPI sleep states or Linux `mem_sleep` modes. The matrix
also does not rank suspend reliability.

The same records and the additive family-wide RTC, lid-angle, and desktop
Ethernet topology summaries are available in [boards.json](../../catalog/boards.json).

## Shared topology and policy

All 16 DeviceTrees in this build specify:

- one `apcie-up,t8012` link with four active functions, generation 2, width x4,
  explicit PERST, and a 650 ms link timeout;
- ANS2, BCE, SEP, and audio functions with DART stream IDs 1, 0, 2, and 3;
- PMGR version-1 bridge counters, 17 bridges, a 50,000 µs CPU power-gate
  latency, and an idle workaround;
- byte-identical `ap-wake-sources`, `ap-wake-source-flags`, and `power-domains`
  arrays;
- ANS RTBuddy marked `power-managed` and `no-shutdown`;
- SMC RTBuddy marked `quiesced`, `user-power-managed`, and `no-shutdown`; and
- SEP self-power-gating with sleep-preparation and power-gate-wait functions.

All 16 also publish one primary `pmu,d2449` with RTC read/write helpers,
`rtc-offset-readonly`, `rtc-offset-use-nvram`, and `info-rtc = 9733`. The
matched provider moves a signed 64-bit clock offset and can persist it through
`IODTNVRAM` as `com.apple.System.rtc-offset`. The common policy does not prove
offset units, alarm behavior, or one Linux host transport across the family.

These are build-specific firmware properties. Host ACPI was examined only for
J152f; a shared T2 DeviceTree property does not prove identical host firmware.

## Desktop and portable inventories

Five desktop boards select `ibridge2d`; eleven portable boards select
`ibridge2p`. The bundle inventories contain 181 and 190 entries respectively,
with 178 in common. An earlier count of 182 portable executable sections used
a different denominator and must not be compared as a bundle count.

The desktop-only bundles are `AppleCS42L83SMCAudio`,
`AppleI2CEthernetAquantia`, and `AppleTAS5764Amp`. The portable-only bundles are:

- `AppleActuatorDriver`, `AppleHIDTransport`, `AppleHIDTransportSPI`,
  `AppleInputDeviceSupport`, and `AppleMultitouchDriver`;
- `AppleMobileDispM8`, `AppleSummitLCD`, and `AppleSynopsysMIPIDSI`; and
- `AppleT8010PCIe`, `AppleTopCaseActuatorHIDDriver`, `AppleTopCaseDriverV2`,
  and `AppleTopCaseHIDEventDriver`.

SMC, PMGR, RTBuddy, PCIe, ANS, SEP, BCE/VHCI, bridge audio, and watchdog
components occur in both inventories. Peripheral acceptance should follow each
board's devices: portable Touch Bar checks do not apply to desktops, and desktop
Ethernet and audio must not disappear from the test plan.

Desktop Ethernet sideband policy also differs. J160 publishes two direct
`aqc-i2c,aqc107` children used by an I2C/LOM management component. J185 and
J185f instead publish an untyped `aqc` child below `aop-i2c0`; J137 and J174
publish neither form. These records classify management ownership only. They
do not show that ordinary Ethernet packets traverse the T2.

## DeviceTree identities

These hashes identify the signed IM4P members, before decompression.

| iBridge / board | Bytes | DeviceTree IM4P SHA-256 |
| --- | ---: | --- |
| `iBridge2,1` / `J137AP` | 28,139 | `704b719cb7982709c3dc2cb13ec0c142094db6bcfb8d441e9026af6550ddc14d` |
| `iBridge2,3` / `J680AP` | 31,156 | `46191cea112f5c223e4b2b15bec3ac98bc997ea06e8a465c0ec2080a9af4a957` |
| `iBridge2,4` / `J132AP` | 31,061 | `e5cef81f84a654f9656381831c5bed5d2ec05bc8d61f1255d90df5fbd95a4c5d` |
| `iBridge2,5` / `J174AP` | 20,561 | `53bbc38338c58e11833fada054e547d39feb23d4c14824d96cda093f1ba7aece` |
| `iBridge2,6` / `J160AP` | 19,693 | `939c99c0a5c33d1780e2dee84f19080d06bd5a53d34f79c98f43aba38ce475be` |
| `iBridge2,7` / `J780AP` | 31,156 | `1dfa7c82373d2c108405c415b9f949152330b031c40dd41e73881e183798e52a` |
| `iBridge2,8` / `J140kAP` | 29,256 | `2b5fcc24ff71399d3025e18cdd35e1750a88931cb1529e23ae32c10339fc8291` |
| `iBridge2,10` / `J213AP` | 31,187 | `940be00a1ebc7d2368ad1ed031938cab2fae3bf4520748e2bf0cd3607943c05f` |
| `iBridge2,12` / `J140aAP` | 29,368 | `3caad7e26e408704d5fdc86868f05b9d76c5d4b0ac3772e04de55c94c8d22ca1` |
| `iBridge2,14` / `J152fAP` | 31,424 | `61500d42f0cc3bbe4a0b113f472500e28979dec8c6a1d1bc3a8b69f2356f7e69` |
| `iBridge2,15` / `J230kAP` | 29,742 | `a8867b53f8b042b3423a3f67c4ebb3ae4fd64121828916770b0cef1a2bbdf788` |
| `iBridge2,16` / `J214kAP` | 31,578 | `ae3ff30143606f84dbfd32bfc7c32e71157765b7aaf5066c444630a4b7efb1af` |
| `iBridge2,19` / `J185AP` | 28,956 | `cc45f81df9ad036c7f1b3e9cb9670eabc99553df09ae41aa85b27d3f7a1e6fbf` |
| `iBridge2,20` / `J185fAP` | 28,951 | `7bb61cdbdef968384d05f70f993298c9c12a68f803ca6d2c460d6398157a7fa0` |
| `iBridge2,21` / `J223AP` | 31,528 | `a67e71627db98f06ca9d11bdc2013e92f3896d48cd99bd4ce3547e39dfa08240` |
| `iBridge2,22` / `J215AP` | 31,389 | `d3181dbcd9c10c327d3914744227e4855861e34de660054b8bf5dd5e93463a30` |

See [Artifacts and method](../method/platform-artifacts.md#reproducing-the-inventory)
for extraction commands and [Host coordination](../graphics/acpi-and-gpu-ownership.md) for the
J152f host-side findings.
