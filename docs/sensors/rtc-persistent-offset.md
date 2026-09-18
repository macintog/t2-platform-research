# RTC persistent offset and PMU policy

[Research map](../README.md#rtc) · [Evidence catalog](../../catalog/README.md)

Every retained production DeviceTree exposes one primary `pmu,d2449` with RTC
read/write helpers, read-only and NVRAM-use policy flags, and `info-rtc = 9733`.
`AppleD2449PMURTC` reads and writes a signed 64-bit offset and can persist it as
`com.apple.System.rtc-offset`; J152f iBoot accepts that name through a generic
38-entry environment/NVRAM allowlist. This proves a family-wide T2 policy and
persistence owner in build `23P6068`, but not the offset unit/epoch, alarm
contract, or Linux host transport. An experimental SMC-key RTC can now be
compared against that owner instead of treated as the specification.

## Evidence and scope

These findings retain the build and observation limits of the
[Linux compatibility inventory](../platform/linux-support.md). Exact source
revisions, module identities, and disassembly anchors are in
[Platform artifacts and method](../method/platform-artifacts.md).
