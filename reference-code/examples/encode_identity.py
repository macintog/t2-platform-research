# SPDX-License-Identifier: MIT
"""Round-trip both known identity-create bodies with synthetic data."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from t2_aks_identity_create import AKSIdentityCreateV4Request, AKSIdentityCreateV5Request


common = {
    "session": 1,
    "internal_flags": 0x4100,
    "effective_bag_handle": -1,
    "item1": bytes(range(1, 17)),
    "item2": b"",
    "account_uuid": bytes(range(17, 33)),
    "item3": b"",
    "original_flags": 6,
}
requests = (
    AKSIdentityCreateV4Request(**common),
    AKSIdentityCreateV5Request(**common, scalar2=0),
)
for request in requests:
    encoded = request.encode()
    restored = type(request).decode(encoded)
    print(
        f"v{encoded[0]} request: {len(encoded)} bytes; "
        f"round trip: {'OK' if restored == request else 'FAILED'}"
    )
