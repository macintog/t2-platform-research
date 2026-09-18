# Desktop Ethernet sideband management

[Research map](../README.md#ethernet) · [Evidence catalog](../../catalog/README.md)

Desktop Ethernet is not one T2 topology. J160 has two direct
`aqc-i2c,aqc107` children and a privileged `setProperties` path for LOM and
external-LOM state, SMBus-style block transfers, interrupts, and bounded
polling. Its declared user-client class is absent from the executable. J185
and J185f instead put an untyped `aqc` child below `aop-i2c0`; J137 and J174
publish neither form. The recovered J160 component is sideband management, not
evidence that ordinary Ethernet packets traverse the T2.

## Evidence and scope

These findings retain the build and observation limits of the
[Linux compatibility inventory](../platform/linux-support.md). Exact source
revisions, module identities, and disassembly anchors are in
[Platform artifacts and method](../method/platform-artifacts.md).
