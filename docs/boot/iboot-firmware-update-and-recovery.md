# iBoot policy, firmware update, and recovery

[Research map](../README.md#boot) · [Evidence catalog](../../catalog/README.md)

## iBoot failure counters and fallback

The signed J152f LLB, iBoot, iBEC, and iBSS containers use distinct role tags
but decompress to one byte-identical executable payload in build `23P6068`.
Erase and update identities share that early chain and diverge at the restore
ramdisk. The shared payload stores boot and panic failures as the low and high
nibbles of one persistent byte, publishes nonzero values separately in
`/chosen`, and increments one while preserving the other. Both direct limits
are five failed events (`count > 4`): the panic branch enters recovery-image
handling, while the boot branch clears the packed counter and commits
`recovery-boot-mode=panicmedic`. One-time boot command resolution precedes the
durable command; consuming the one-time value deletes and commits it. Upgrade
failure records the OTA result and reason, transfers any configured fallback
command, clears retry state, and commits before continuing. Selector meanings
and three stripped predicates still require symbols or a runtime trace, but
the retained writer, threshold, and direct fallback graph is complete.

## Firmware transaction and commit order

The update path then uses prepared headers or slots, explicit
verification, commit, failure counting, and rollback across MacEFI, ANS boot
firmware, boot blocks, and SEP hashes. This is a staged transaction model, not
four unrelated firmware files or a blind flash operation.

The recovered SPI-writer sequence writes payload first, then a prepared header
whose valid bit is clear, and commits by rewriting the header with validity
set. It verifies generation and payload and can try the alternate header within
a bounded retry; a preparation-only mode deliberately leaves the uncommitted
header. The NVMe updater separates optional section-0 and PHY1/PHY2 transfers
from activation and version checks, with distinct invalid, erase-required, and
retry outcomes. SEP update tooling likewise separates preflight, boot check,
slot selection, hash verification, and commit. These contracts support a
transactional updater design, not unsupervised Linux flashing.

The outer `restored_update` caller makes the failure policy asymmetric. NAND
firmware alone maps one retry-class result to exactly one outer retry; terminal
NAND or SEP-load failure stops later work. MacEFI boot and update-wait failures
are explicitly logged and tolerated. `update_iBoot` has no generic retry and
sets `shouldCommit:YES`; on Sandcat it commits the boot header before the AP
hash, then stages optional SEP firmware. A later AP-hash failure can therefore
leave a valid boot header while the outer step reports failure. FDR checks and
the still-later SEP-hash commit gate protected-filesystem creation.

Although `seputil` exposes preflight, boot-check, and provisional-slot
commands, this retained caller invokes only restore/load, ping, AP-hash commit,
SEP-hash commit, and erase. Generic failure cleanup is recovered, but exact
selection among return-to-original, fail-forward, and recovery mode depends on
persisted checkpoint/NVRAM point-of-no-return state and requires a matched
snapshot or authorized trace.

## Evidence and scope

These findings retain the build and observation limits of the
[Linux compatibility inventory](../platform/linux-support.md). Exact source
revisions, module identities, and disassembly anchors are in
[Platform artifacts and method](../method/platform-artifacts.md).
