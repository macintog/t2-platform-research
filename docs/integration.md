# Integrating native T2 adoption

The useful discovery is how to retain the credential needed to activate a
Linux-created T2 identity after a restart. Creating and saving a keybag alone is
not enough: the working sequence also preserves a 16-byte creation-time secret.

These notes describe the sequence used in the T2 proof of concept. The modules
here implement the request bodies and local storage. Your application supplies
the Secure Enclave transport and the rest of the biometric workflow.

The [research reference](research/README.md) covers the internal SEP services,
wire formats, and experiments behind this sequence.

## Create and preserve the identity

1. Create an Apple Credential Manager (ACM) context for the selected user, install
   the creation credential, and obtain its 16-byte external form.
2. Save those exact 16 bytes before sending the identity-create request. In the
   tested creation path, they become the input from which the Secure Enclave
   derives the identity verifier.
3. Send AppleKeyStore (AKS) operation `0x01`, version `5`, with original flags `6`
   and the creation-time external form in `item1`.
4. Use the returned live handle to export the saved keybag with operation `0x02`.
5. Commit the saved keybag and creation-time secret together. Keep the account
   UUID and keybag UUID associated with this generation.

The extra material returned by operation `0x01` is not the saved keybag. The
reloadable object comes from the separate export request.

`AKSIdentityCreateV5Request` represents the creation body.
`AKSIdentityCopyKeybagV1Request` represents the export body. Their response classes
check lengths, versions, alignment, and trailing bytes. The codecs leave field
selection and transport to the caller; the example's synthetic values are for
learning the format.

## Activate after a restart

Load the saved keybag and establish its live handle and user alias through your
transport. Then create a fresh ACM input context and install the saved 16-byte
secret as its type-5 credential data.

Obtain the new input context's external form. Operation `0x21` with option `0x100`
uses that live reference to extract the saved secret and verify the identity.
When enrollment authorization is needed, create a separate target context for
`TouchIdEnrollment` and keep both contexts alive.

The working T2 sequence verifies and authorizes with `0x21`, then sends `0x18`
using the original input context's external form as the login credential. The
authorized target remains alive while this happens. Substituting the target
reference for the input reference changes the credential being supplied.

The complete AKS/ACM activation request codecs and context management belong to
the integrating implementation. These modules do not implement `0x21` or `0x18`.

## Store the activation generation

`ActivationBundleStore` takes an existing private directory, an operation UUID,
an account UUID, and a Linux UID. The directory must belong to the process user
and have mode `0700`.

Call `stage(secret)` with a mutable 16-byte buffer before identity creation.
It writes a pending secret and returns its digest. After export, call `commit()`
with the saved keybag, its digest, the secret digest, and the bag UUID. The store
writes mode-`0600` files and publishes the generation by renaming its directory.
The caller's secret and keybag buffers are wiped when these methods return.

`staged_secret()` reads the pending secret for the creation transaction.
`activation_secret()` reads a committed secret within a context manager and wipes
the returned buffer when the context exits. The checksums detect mismatched files;
they do not encrypt the secret. Treat the stored secret as a credential.

The store can complete partial local writes and reconcile an already-published
generation. Your application still needs to reconcile any interrupted hardware
operation before deciding whether another request is appropriate.

## Connect the remaining pieces

An integration needs:

- Endpoint-7 AKS framing and transport, including device status handling.
- ACM context creation, credential installation, externalization, and cleanup.
- Keybag loading, UUID checks, alias binding, and the `0x21`/`0x18` activation path.
- Fingerprint enrollment, matching, and biometric-state persistence.
- User selection and the connection to the receiving project's authentication UI.

The replacement codec contains UUID-based open and delete bodies. Opening an
existing identity by UUID is distinct from loading an exported keybag, even
though both use AKS operation `0x03` in their respective request forms.

The underlying research used an Intel T2 Mac identified as J152f and bridgeOS
`23P6068`. The Mac still uses Apple's bridgeOS and Secure Enclave firmware. The
contribution concerns creating and managing the user identity from Linux.
