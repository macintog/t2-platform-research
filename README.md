# t2touch-mini

A small, MIT-licensed protocol reference for Linux-native Touch ID adoption on
Intel Macs with Apple’s T2 chip.

t2touch-mini is for developers. It encodes the AppleKeyStore identity creation
and replacement requests and provides crash-safe activation-bundle storage. It
does not communicate with the fingerprint reader, run fprintd, modify PAM, or
enable fingerprint login by itself.

For the installable Omarchy proof of concept, use
[t2touch](https://github.com/macintog/t2touch).

## Run the reference

Python 3.10 or newer is sufficient; the package uses only the standard library.

```bash
python3 -m unittest discover -s tests -v
python3 examples/encode_identity.py
```

The example uses synthetic data and does not contact hardware.

## Modules

| Module | Purpose |
| --- | --- |
| [Identity creation](src/t2_aks_identity_create.py) | Encode creation/export requests and decode their responses. |
| [Identity replacement](src/t2_aks_identity_replacement.py) | Encode deletion and UUID-based open requests; decode their responses. |
| [Activation storage](src/t2_activation_bundle.py) | Store the creation-time secret and saved keybag together, with interrupted-write recovery. |

The [integration guide](docs/integration.md) defines the transport and lifecycle
contracts an integrating project must supply. The
[research reference](docs/research/README.md) documents the underlying SEP,
AKS, ACM, storage, and biometric findings. [Credits](CREDITS.md) describe the
research foundation.

## Relationship to t2touch

The full t2touch integration has demonstrated Linux-owned authority creation,
first and additional enrollment, any-enrolled-finger matching, neutral
`Finger N` naming, reconciled named deletion through a clean empty inventory,
standard fprintd clients, sudo, graphical PolicyKit, the Omarchy lock screen,
and password fallback on its MacBookPro16,1 reference system. Later validation
corrected lock/display recovery and readiness feedback, and reduced measured
reader preparation from about 7.3 to 3.8 seconds. Permission-dialog touches still
needed retries; this is not a universal login-latency or hardware-support claim.
The [integration follow-up](docs/research/integration-followup.md#graphical-integration-and-measured-readiness)
records the evidence and limits.

Those results validate the protocol represented here, but they do not turn
t2touch-mini into an end-user driver. An adopter must still provide the kernel
and Bridge transports, authorization boundary, fingerprint lifecycle, fprintd
service, and desktop integration.

## License

t2touch-mini is available under the [MIT license](LICENSE).
