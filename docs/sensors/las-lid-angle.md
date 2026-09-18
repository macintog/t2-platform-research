# Lid-angle sensor (LAS)

[Research map](../README.md#las) · [Evidence catalog](../../catalog/README.md)

The lid-angle sensor (LAS) enumerates as USB `05ac:8104`. Its 52-byte USB
descriptor stream has SHA-256
`2395a4fa7ec1d9cd87c99a6ade7c635572494af9a56e51798c100d21c0ecaef5`; its
179-byte HID descriptor has SHA-256
`baec17e4024defa3a53850ba6058a6dad83efef7f8df073fdf89b51f866693c5` and exposes
Sensors page `0x20`, Device Orientation usage `0x8a`. The Linux-visible
descriptor declares report 1 as a 9-bit Input value with logical range 0
through 360. Two pinned macOS implementations instead request Feature report
ID 1 with an 8-byte buffer, require at least three returned bytes, and decode
bytes 1–2 as an unsigned little-endian degree value. Their code applies no
centidegree scaling, so a README's `0.01`-degree claim is not used here. The
verified J152f host also accepted one GET-only `HIDIOCGFEATURE(8)` request and
returned length 3 with bytes `01 6d 00`, a raw angle of 109 degrees. This
proves that the current Linux personality accepts Feature GET despite
declaring report 1 as Input; it does not explain the descriptor mismatch.
Linux's rotation driver separately requires common power/report features and a
quaternion usage `0x200483`, which this descriptor does not supply. The
observation used a read-only device descriptor and made no output, stimulus,
reset, rebind, configuration, suspend, or reboot change.

## Evidence and scope

These findings retain the build and observation limits of the
[Linux compatibility inventory](../platform/linux-support.md). Exact source
revisions, module identities, and disassembly anchors are in
[Platform artifacts and method](../method/platform-artifacts.md).
