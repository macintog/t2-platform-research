# Suspend observations

On one MacBookPro16,1 configuration, successful BCE state restoration occurred
alongside failures in AMD, gmux, or physical xHCI. A control with Touch ID
services and SEP transport inactive reproduced the leading deep-suspend
failure and a later s2idle hang. These observations narrow attribution without
identifying one universal cause.

## Configuration and evidence

The September 2026 experiments used Omarchy with T2 kernels in the 7.2.4 and
7.2.6 series. The detailed retained snapshot was
`7.2.6-arch2-Watanare-T2-2-t2`, with `pm_async=off` and
`mem_sleep_default=deep`. The analyzed bridgeOS build was `23P6068`.

Recorded package inputs were `linux-t2-arch` commit
`7b97124fa886ed5abbf5a35022fe70d4661a76e8` (package `7.2.6.arch2-2`) and
`linux-t2-patches` commit `794069f7015e25d62da420e2748daaac0813cedc`.
The t2bce research revision was
`a973d53c8278e9db5ff8314b816d6880309ed39e`. Package inputs and installed module
identities were recorded separately; a nearby research checkout alone is not
proof of installed source.

The package included T2 BCE support, an `apple-gmux force_igd`/probe-order
patch, Radeon Pro 5300 SMU feature-mask changes derived from Apple data, and
an early-secondary-CPU-offlining change. The CPU change's recorded test models
did not include MacBookPro16,1. These are material conditions for interpreting
platform/noirq failures.

The table summarizes retained journals and experiment notes. The complete
raw logs are not part of this case study; the observations are not a new
independent replication. `pm_test` stages exercise selected portions of the
suspend path. Returning from the devices stage does not demonstrate real sleep.

## Experiment matrix

| Experiment | Returned? | T2 BCE observation | Other decisive observation |
| --- | --- | --- | --- |
| Three deliberate s2idle tests on 7.2.4 | No | Not sufficient to recover host | Wake hard-failed even after Touch ID work was quiesced |
| 7.2.6-2 lid-close s2idle | No | Last durable line only identified entry | `PM: suspend entry (s2idle)`; no exit, panic, or OOM |
| `pm_test=freezer` | Yes | Device PM not entered | Confirms user-space freeze is not the boundary |
| `pm_test=devices`, manually powered-off AMD | Yes | Stateful BCE success | `apple_gmux` timeout remained |
| `pm_test=platform`, manually powered-off AMD | No durable return | Not enough to localize | PM_TRACE hash collision made attribution unsafe |
| `pm_test=devices`, normally initialized AMD | Yes | Stateful BCE success | AMD resume failed `-62`; no real sleep occurred |
| `pm_test=devices`, `amdgpu` blacklisted | Yes | Stateful BCE success | Zero PM counters; gmux timeout disappeared |
| `pm_test=platform`, `amdgpu` blacklisted | Kernel/post-hook returned, machine unusable | BCE success | Physical xHCI `09:00.0` and `7f:00.0` failed `-19`; host controller died; no ping |
| Deep devices stage, T2Touch inactive | Yes | Stateful BCE success | Stock package AppleSMC, no SEP transport/device, all T2Touch services inactive |
| Deep platform stage, T2Touch inactive | Unwound | BCE not leading failure | AMD `pci_pm_suspend_noirq` failed `-110`; mode1 reset failed |
| Subsequent s2idle fallback, T2Touch inactive | No | Active T2Touch absent | Forced shutdown required |

“Returned” describes the stated stage, not a fully usable laptop. In particular,
a post-hook returning while display or network remains unavailable is a failed
end-to-end result.

## A delayed VHCI completion

One retained kernel log contained this driver message:

```text
t2bce_vhci: [01] data URB unexpected completion state=7 status=0 size=316
```

It appeared about 70 seconds after a devices-stage suspend exit and immediately
before another deep attempt. In that attempt the recorded T2 and storage
callbacks succeeded, then AMD failed `pci_pm_suspend_noirq` with `-110` after a
failed mode-1 reset. Linux unwound and BCE restored state. The subsequent
s2idle fallback entered without a durable exit record.

The delayed completion is a residual queue/state-accounting lead. It does not
show that VHCI caused the later AMD failure. A clean mailbox completion is
insufficient evidence that all higher-level work drained.

## What the inactive control establishes

The control used stock package AppleSMC, no active `t2_sep_transport` module or
device, and inactive Touch ID services while retaining identity data. The
leading AMD/deep failure and later s2idle hang did not require those active
components.

This does not emulate a machine on which the software was never installed,
exclude every Touch ID-specific bug, or establish which remaining component
caused the hang. It is strong evidence against making active SEP transport the
necessary cause of these particular failures.

## Separate transition types

Deep sleep can fail in a device/noirq callback before platform entry. An s2idle
attempt can enter without a durable exit. Hibernate adds image discovery,
storage restoration, and reconstruction of firmware/peripheral state. Results
from one path do not qualify another.

In the retained snapshot, the kernel advertised `disk` but there was no
`resume=` argument and system policy disabled routine sleep/hibernate. Earlier
Btrfs resume setup had delayed ordinary boots without an image. No complete
hibernate chain was qualified in these experiments.

## External reports

These reports independently describe related symptom classes. They are field
reports for their stated configurations, not controlled replications or
maintainer-confirmed root causes.

| Model | Report | Relevance |
| --- | --- | --- |
| MacBookPro15,1 | [AMD-active deep resume reboots](https://github.com/t2linux/T2-Ubuntu/issues/195) | Host GPU failure class |
| MacBookPro15,2 | [S4 BCE/VHCI restoration failure](https://github.com/t2linux/kernel/issues/22); [Touch Bar loss after resume](https://github.com/t2linux/fedora/issues/52) | Hibernate restoration and peripheral acceptance differ |
| MacBookPro15,3 | [S3 versus S4 input behavior](https://github.com/t2linux/kernel/issues/17) | Ordinary sleep can differ from hibernate on one board |
| MacBookPro16,1 | [AMD PSP/SMU failure](https://github.com/t2linux/kernel/issues/21) | Matches the leading model-specific host failure class |
| MacBookAir9,1 | [Event 0x50 and VHCI desynchronization](https://github.com/t2linux/kernel/issues/24) | T2 restoration can fail after initial resume |

The original survey found specific reports for these five configurations.
The absence of reports for the other eleven in that survey is a coverage gap,
not evidence of reliable suspend.

## Causal assessment

Host-platform ordering and recovery are the strongest next investigation for
the observed MacBookPro16,1 failures. AMD/gmux and physical xHCI have direct
failure evidence. CPU/ACPI interactions and firmware behavior remain viable;
the last durable log line is not uniquely causal.

Incomplete T2 state coordination could produce additional failures after a
host-platform blocker is removed. The firmware analysis identifies mechanisms
to examine, but does not prove that a static difference caused a retained hang.
No known-good suspend/hibernate configuration for this reference system was
established by the experiments.
