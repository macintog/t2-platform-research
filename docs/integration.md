# Integrating native T2 adoption

The useful discovery is how to retain the credential needed to activate a
Linux-created T2 identity through a fresh transport owner. Creating and saving
a keybag alone is not enough: the working sequence also preserves a 16-byte
creation-time secret.

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
3. Send AppleKeyStore (AKS) operation `0x01` with the creation-time external
   form in `item1` and original flags `6`. Explicitly select the recovered
   identity-create layout required by the target firmware: v4 was observed
   with bridgeOS `23P2048`, while v5 was observed with `23P6068`. Changing only
   the version word is invalid because the scalar tail differs.
4. Use the returned live handle to export the saved keybag with operation `0x02`.
5. Commit the saved keybag and creation-time secret together. Keep the account
   UUID and keybag UUID associated with this generation.

The extra material returned by operation `0x01` is not the saved keybag. The
reloadable object comes from the separate export request.

`AKSIdentityCreateV4Request` and `AKSIdentityCreateV5Request` represent the two
known creation bodies.
`AKSIdentityCopyKeybagV1Request` represents the export body. Their response classes
check lengths, versions, alignment, and trailing bytes. The codecs leave field
selection and transport to the caller; the example's synthetic values are for
learning the format.

## Activate through a fresh owner

Load the saved keybag and establish its live handle and user alias through your
transport after the create/export owner has closed and released its temporary
handle. This can happen immediately in the same running system; it does not
require a reboot. Then create a fresh ACM input context and install the saved
16-byte secret as its type-5 credential data.

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

Publishing this directory is not proof that provisioning, live-handle cleanup,
or first-fingerprint persistence has completed. Track those milestones
explicitly. A fresh exclusive owner must reload and verify the exact saved
identity before enabling it; neither a newer mapping schema nor the presence of
a bundle means the hardware transaction is finished. Do not repeat identity
creation to complete a host-side publication or cleanup step.

## Keep account authority separate from fingerprint state

The first enrollment's fresh-owner verification establishes native account
authority. Later additions and deletions change the current fingerprint set,
while the original account evidence remains valid. Requiring the first
fingerprint to remain enrolled would prevent further additions after deleting it.

Before a mutation, reconcile the current user/master Catacomb generation, live
identity inventory, and completed mutation history against the same account,
keybag, and mapping. An addition must produce exactly the prior set plus its new
identity, and match that new identity specifically. Do not hardcode a one-print
baseline. An unfinished mutation must be reconciled before another starts.

Expose exactly five neutral slots, `Finger 1` through `Finger 5`, backed by
private identity UUIDs. Deleting one identity must not renumber any survivor;
the next successful enrollment takes the lowest vacant slot. A slot label stays
with its identity while that identity exists, but does not establish which
physical finger the person used.

The [integration contracts](research/integration-contracts.md) describe
deletion recovery and client lifecycle. These responsibilities
belong to your adapter; the three reference modules here do not implement them.

## Preserve authentication fallback

Biometric readiness and the fprint service must converge whenever the product
starts or upgrades, but they must not become the only way to authenticate. Keep
a tested password path and a recoverable PAM configuration. Test fingerprint
success separately from password fallback while the fingerprint service is
unavailable. Preserve rollback copies when installing any PAM change.

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

## Graphical readiness and performance

A placement prompt must follow actual sensor readiness, not merely the start of
an asynchronous verification task. Keep preparation and retry messages visible,
and run optional sounds outside the authentication path. In t2touch, the
`match_armed` event supplies the readiness signal; UI feedback never authorizes
a match.

Avoid collecting the same presentation inventory repeatedly within one client's
list/verify sequence. A single-use projection may reduce that work, and concurrent
requests may share a running read, while native matching still reconciles current
private authority and attests the result afterward. Never turn this optimization
into a cached match verdict, credential, or stale cross-client authority.

Authorize a fingerprint deletion before acquiring the reader or its global
operation lock. Otherwise the authorization dialog can wait for a reader already
held by the operation it is trying to approve.

Test the whole graphical transition: authentication must return to a responsive
desktop, and failure must leave password fallback and recovery usable. Device
selection must follow connected displays and explicit user configuration, not
fixed card numbers or a preferred GPU vendor. These are integration duties;
the three mini codecs/storage modules implement none of this desktop policy.
