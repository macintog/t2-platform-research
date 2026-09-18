# Touch Bar USB configuration and DRM binding

[Research map](../README.md#touch-bar) · [Evidence catalog](../../catalog/README.md)

The J152f Touch Bar exposes two USB configurations. Configuration 1 has one
`03/01/01` HID interface and wins Linux's generic chooser, so it binds through
`usbhid` to `hid_appletb_kbd`. Configuration 2 contains the class-`0x10` bulk
interface matched by `appletbdrm`, plus a second HID interface. The complete
109-byte USB descriptor stream has SHA-256
`d81d15934ed5bbaf9015f26ab897c821a50c72ec4775c1e9a62a8496968a98b5`.
This resolves the apparent modalias mismatch: the remaining problem is a safe,
reliable transition to configuration 2 and correct reprobe at boot and resume.
tiny-dfr's pinned rule performs the transition 1 to 0 to 2, while
`appletbdrm` itself does not call `usb_set_configuration()`.

## Evidence and scope

These findings retain the build and observation limits of the
[Linux compatibility inventory](../platform/linux-support.md). Exact source
revisions, module identities, and disassembly anchors are in
[Platform artifacts and method](../method/platform-artifacts.md).
