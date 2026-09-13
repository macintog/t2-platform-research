# SPDX-License-Identifier: MIT
"""Round-trip an identity-create body with synthetic data and no hardware."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from t2_aks_identity_create import AKSIdentityCreateV5Request

request = AKSIdentityCreateV5Request(
    session=1,
    internal_flags=0x24000,
    effective_bag_handle=-1,
    item1=bytes(range(1, 17)),
    item2=b"",
    account_uuid=bytes(range(17, 33)),
    item3=b"",
    original_flags=6,
    scalar2=0,
)
encoded = request.encode()
restored = AKSIdentityCreateV5Request.decode(encoded)
print(f"Encoded request: {len(encoded)} bytes")
print(f"Round trip: {'OK' if restored == request else 'FAILED'}")
