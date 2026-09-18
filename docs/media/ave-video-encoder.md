# AVE video encoder transport

[Research map](../README.md#ave) · [Evidence catalog](../../catalog/README.md)

Analysis traces one command and callback through the signed media components.
`AppleAVEBridge` 6.1/35 owns the same four parameter/callback queues as the
pinned public driver, while `AppleAVE2` 9000.1.1 owns the H.264/HEVC engine.
Public command `0x02` uses a 4 KiB command followed by Y and UV DMA buffers, a
parameter reply, callback metadata/payload, and metadata echo. Analysis of
build-matched `aveserverd` confirms the public command `0x02` offsets. The
daemon constructs an IOSurface-backed pixel buffer and invokes the retained H9
encoder, which checks for `AppleAVE2Driver` before opening its user client.
Callback `0x0b` serializes the public metadata and payload length before the
queue-2 echo. This establishes the path for that command and callback; other
commands, codecs, formats, malformed-buffer safety, boards, recovery, and API
stability remain unqualified.

## Evidence and scope

These findings retain the build and observation limits of the
[Linux compatibility inventory](../platform/linux-support.md). Exact source
revisions, module identities, and disassembly anchors are in
[Platform artifacts and method](../method/platform-artifacts.md).
