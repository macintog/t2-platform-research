# AKS identity and persistence reference code

These offline Python examples express recovered AppleKeyStore request formats
and local activation-bundle persistence. They support the
[SEP identity research](../docs/sep/aks-identity-and-authorization.md) and
[Linux integration contracts](../docs/sep/linux-integration.md).

They are implementation references for someone building a Linux integration.
They do not maintain the research catalog; the [catalog scripts](../catalog/README.md#optional-scripts)
handle lookup and document checks.

| Module | Contract illustrated |
| --- | --- |
| [t2_aks_identity_create.py](t2_aks_identity_create.py) | Version-4/version-5 identity creation and export requests and responses. |
| [t2_aks_identity_replacement.py](t2_aks_identity_replacement.py) | Identity deletion and UUID-based open requests and responses. |
| [t2_activation_bundle.py](t2_activation_bundle.py) | Activation-input and keybag storage, with interrupted-write recovery. |

These modules do not supply a hardware transport, authentication service, or
working fingerprint login. Adopters must implement and qualify the surrounding
lifecycle.

## Validation

Python 3.10 or newer and its standard library are sufficient. From the
repository root:

```sh
python3 -m unittest discover -s reference-code/tests -v
python3 reference-code/examples/encode_identity.py
```

The example uses synthetic data and does not contact hardware. Tests check
encoding bounds, mutable-buffer ownership, and persistence failure/retry
behavior; they do not prove firmware compatibility or power-loss safety on
every filesystem.
