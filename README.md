# T2 platform research

MIT-licensed technical references and reference code for Linux support on Apple
T2 Macs. The collection covers SEP and Touch ID protocols, persistent storage,
platform topology, firmware power management, and suspend/hibernate behavior.
It extends the project previously called t2touch-mini.

## Read the research

| Start here | What it answers |
| --- | --- |
| [Platform architecture](docs/platform-architecture.md) | How host PCI functions, firmware services, storage, and peripherals fit together. |
| [Board configurations](docs/board-configurations.md) | Shared topology and policy differences across 16 production iBridge2 configurations. |
| [SEP and Touch ID](docs/research/README.md) | Service routing, AKS/ACM authorization, identity creation, and the fingerprint lifecycle. |
| [Boot and persistent storage](docs/research/boot-and-storage.md) | EFI startup, xART, gigalocker, and embedded NVMe namespaces. |
| [Power management](docs/power-management.md) | Recovered BCE, SMC, ANS, SEP, and PMGR behavior. |
| [Host coordination](docs/host-coordination.md) | J152f ACPI, graphics ordering, and the APP7777 comparator. |
| [Suspend observations](docs/suspend-observations.md) | Linux experiments and the causal explanations they support. |
| [Boot and distribution integration](docs/boot-and-distribution.md) | Configuration-specific lessons from boot, graphics, and kernel updates. |
| [Artifacts and method](docs/artifacts-and-method.md) | Platform firmware identities, analysis anchors, and reproduction steps. |
| [Investigation guide](docs/investigation-guide.md) | Useful next measurements and how to report them. |
| [Findings index](findings.json) | One machine-readable index of the protocol and platform findings. |

The platform inventory covers all 16 production configurations in bridgeOS
`23P6068`. Host ACPI and the principal runtime experiments cover
MacBookPro16,1 / J152fAP. The SEP reference also documents identity-create-v4
on MacBookPro16,2 / J214K with bridgeOS `23P2048`. Each chapter distinguishes
static analysis, observed behavior, and inference. A firmware inventory does
not establish working suspend or fingerprint integration on every model.

## Use the reference code

The Python modules encode AppleKeyStore identity creation, export, replacement,
and open requests, and provide crash-safe activation-bundle storage. Their
existing module names and interfaces are retained.

| Module | Purpose |
| --- | --- |
| [Identity creation](src/t2_aks_identity_create.py) | Encode v4/v5 creation and export requests; decode responses. |
| [Identity replacement](src/t2_aks_identity_replacement.py) | Encode deletion and UUID-based open requests; decode responses. |
| [Activation storage](src/t2_activation_bundle.py) | Store the creation input and saved keybag with interrupted-write recovery. |

Python 3.10 or newer is sufficient; the package uses the standard library.

```sh
python3 -m unittest discover -s tests -v
python3 examples/encode_identity.py
python3 scripts/verify.py
```

The example uses synthetic data and does not contact hardware. The
[integration guide](docs/integration.md) defines the transport and lifecycle
contracts an adopter must supply. The modules do not run fprintd or enable
fingerprint login by themselves.

## Relationship to t2touch

[t2touch](https://github.com/macintog/t2touch) supplies the installable Touch ID
implementation and its authentication, recovery, and desktop documentation.
This project is the maintained home for reusable research and reference code.
Product documentation links to a specific research revision so its explanations
remain tied to the version being described.

## Reuse and contributions

The original explanations, reference modules, and tools use the
[MIT license](LICENSE). [Credits](CREDITS.md) distinguish upstream foundations,
protocol contributions, analysis tools, and external reports.
[Contributing](CONTRIBUTING.md) describes how to submit corrections and
configuration-specific evidence.
