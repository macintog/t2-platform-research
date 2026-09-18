# Boot and distribution integration

These are configuration-specific lessons from Omarchy on MacBookPro16,1.
They describe observed behavior and useful checks; they do not establish a
universal T2 boot configuration.

## Separate encrypted-root entry from display handoff

On an Omarchy 4.0.1 installation, boot could reach LUKS unlock and text output
but fail to produce a usable internal-panel desktop. Recovery through an
installer and the installed root made those stages distinguishable.

The incident record attributes a display-handoff crash to Plymouth 24.004.60
and records an early-mount race with asynchronous initramfs unpacking on kernel
7.1. Disabling Plymouth and adding `initramfs_async=0` were part of the retained
working configuration. The evidence summarized here does not independently
isolate the effect of each change or establish that later kernels need them.
A separate transient device-mapper message after unlock was not diagnosed.

For a new report, record which stage failed, the kernel/initramfs/bootloader
versions, and whether a console or authenticated remote session remained
available. Compare the generated boot entry with the intended configuration.

## Internal-panel ownership and Radeon policy

One working configuration used `apple-gmux force_igd=1` so Intel drove the
internal panel. A guarded service checked Intel boot-display and eDP ownership
before setting Radeon DPM to `low`. AMD remained initialized; runtime PM was
reported unavailable. This is a low-DPM policy, not a powered-off GPU.

Several subsequent boots reached the GUI. The guard added roughly nine seconds
to measured boot time. No instrumented power comparison was established for
that configuration, so there is no wattage reduction to report.

An [Omarchy GPU account](https://blog.codewithdan.com/how-i-cut-gpu-power-from-18-w-to-4-w-on-an-omarchy-macbook-pro-with-github-copilot-cli/)
informed the direction of the experiment. Its measurements are not measurements
of this configuration. The [t2linux hybrid graphics guide](https://wiki.t2linux.org/guides/hybrid-graphics/)
provides broader context; model, patch set, panel owner, and external-display
requirements determine whether any policy applies.

## Keep the T2 kernel attached to an update source

On one installation, an installer-supplied `linux-t2` remained installed but
was absent from all configured repositories. Ordinary updates could not
advance it. A second installation also used a different Omarchy channel.
Matching distribution version labels had concealed both differences.

Useful read-only checks are:

```sh
pacman-conf --repo-list
pacman -Q omarchy omarchy-settings linux-t2 linux-t2-headers
pacman -Si linux-t2 linux-t2-headers
uname -r
```

In the recorded repair, Omarchy's Pacman refresh replaced `pacman.conf`.
The supported `pre-refresh-pacman` custom-repository hook preserved the
`arch-mact2` include. Kernel and headers then advanced from `7.1.8.arch1-3` to
`7.2.4.arch1-3`, and the generated UKI/Limine entry booted successfully.
The repository configuration used `SigLevel = Never`, so Pacman did not
cryptographically authenticate that source. That historical setting is not a
security recommendation or a claim about today's repository policy.

An update check should compare the running kernel, installed packages,
repository candidates, and generated boot entry. Those are separate states.

## Remote updates and recovery

In Omarchy 4.0.3, `omarchy-update -y` still displayed a reboot confirmation.
Terminating that prompt did not decline the reboot: a reboot followed.
Automation must use the updater's actual interface rather than assume that a
yes flag or process termination controls reboot behavior.

Encrypted-root recovery required local unlock before ordinary remote access
returned. Wi-Fi provided the routine SSH path. Direct Thunderbolt ingress was
useful during recovery but did not establish a reliable Thunderbolt Ethernet
configuration.

WayVNC 0.10.1 on Hyprland interoperated with macOS Screen Sharing through a
loopback listener carried over SSH. This is a remote-observation technique,
not a T2 firmware finding. Keeping recovery access independent of the display
made subsequent diagnosis more practical.
