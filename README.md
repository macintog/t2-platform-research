# t2touch-mini

Protocol documentation and reference code for Linux-native T2 Touch ID adoption.

This project shares the account-creation and persistence pieces behind setting up
Touch ID from Linux without importing a macOS user account or fingerprint data.
It is for developers who want to bring that capability to another project.

The modules encode AppleKeyStore requests and keep the creation-time secret with
its saved keybag. They do not communicate with a fingerprint reader or enable
fingerprint login. An integrating project supplies the hardware transport,
enrollment, matching, and desktop authentication.

## Try the reference code

Use Python 3.10 or newer on Linux or macOS. Everything here uses the standard
library. From the repository root, run:

```sh
python3 -m unittest discover -s tests -v
python3 examples/encode_identity.py
```

The example encodes and decodes a request using synthetic data. It prints the
request length and a round-trip result without contacting hardware.

## What is included

| Module | Purpose |
| --- | --- |
| [Identity creation](src/t2_aks_identity_create.py) | Encode creation/export requests and decode their responses. |
| [Identity replacement](src/t2_aks_identity_replacement.py) | Encode deletion and UUID-based open requests; decode their responses. |
| [Activation storage](src/t2_activation_bundle.py) | Store the creation-time secret and saved keybag together, with recovery after an interrupted file write. |

Read the [integration guide](docs/integration.md) for the adoption sequence and
what your implementation needs to supply. [Credits](CREDITS.md) describe the
research foundation.

## Community use

This proof of concept is shared under the [MIT license](LICENSE), so anyone can
study it, adapt it, and help bring Linux-native T2 Touch ID support to more people.
