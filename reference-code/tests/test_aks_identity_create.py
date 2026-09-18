# SPDX-License-Identifier: MIT
import dataclasses
import struct
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parents[1]))
import t2_aks_identity_create as codec


def request(**changes):
    value = codec.AKSIdentityCreateV5Request(
        session=0x0102030405060708,
        internal_flags=0x24000,
        effective_bag_handle=-1,
        item1=b"primary",
        item2=b"two",
        account_uuid=bytes(range(16)),
        item3=b"item-three",
        original_flags=5,
        scalar2=9,
        optional_data=b"optional",
    )
    return dataclasses.replace(value, **changes)


class AKSIdentityCreateCodecTests(unittest.TestCase):
    def test_constants_name_the_wire_layer(self):
        self.assertEqual((codec.ENDPOINT, codec.OPERATION, codec.VERSION), (7, 1, 5))

    def test_round_trip_preserves_explicit_fields(self):
        value = request()
        self.assertEqual(codec.AKSIdentityCreateV5Request.decode(value.encode()), value)

    def test_encoding_uses_little_endian_fixed_prefix(self):
        encoded = request().encode()
        self.assertEqual(
            encoded[:20],
            struct.pack("<IQIi", 5, 0x0102030405060708, 0x24000, -1),
        )

    def test_blobs_have_zero_four_byte_alignment_padding(self):
        encoded = request(item1=b"x").encode()
        self.assertEqual(encoded[20:28], b"\x01\0\0\0x\0\0\0")

    def test_empty_optional_blob_is_still_length_prefixed(self):
        self.assertTrue(request(optional_data=b"").encode().endswith(bytes(4)))

    def test_rejects_uuid_with_wrong_size(self):
        with self.assertRaisesRegex(codec.AKSIdentityCreateCodecError, "UUID"):
            request(account_uuid=b"short").encode()

    def test_rejects_bool_as_integer(self):
        with self.assertRaisesRegex(codec.AKSIdentityCreateCodecError, "session"):
            request(session=True).encode()

    def test_rejects_out_of_range_handle(self):
        with self.assertRaisesRegex(codec.AKSIdentityCreateCodecError, "handle"):
            request(effective_bag_handle=1 << 31).encode()

    def test_rejects_oversize_request(self):
        with self.assertRaisesRegex(codec.AKSIdentityCreateCodecError, "endpoint body"):
            request(item1=b"x" * codec.MAX_BODY_BYTES).encode()

    def test_rejects_wrong_version(self):
        encoded = bytearray(request().encode())
        encoded[:4] = struct.pack("<I", 4)
        with self.assertRaisesRegex(codec.AKSIdentityCreateCodecError, "version"):
            codec.AKSIdentityCreateV5Request.decode(bytes(encoded))

    def test_rejects_truncated_blob(self):
        with self.assertRaisesRegex(codec.AKSIdentityCreateCodecError, "truncated"):
            codec.AKSIdentityCreateV5Request.decode(request().encode()[:-1])

    def test_rejects_nonzero_blob_padding(self):
        encoded = bytearray(request(item1=b"x").encode())
        encoded[25] = 1
        with self.assertRaisesRegex(codec.AKSIdentityCreateCodecError, "padding"):
            codec.AKSIdentityCreateV5Request.decode(bytes(encoded))

    def test_rejects_request_trailing_bytes(self):
        with self.assertRaisesRegex(codec.AKSIdentityCreateCodecError, "trailing"):
            codec.AKSIdentityCreateV5Request.decode(request().encode() + b"\0")

    def test_decodes_live_handle_and_kek_material(self):
        data = struct.pack("<IiI", 5, 42, 3) + b"abc\0"
        self.assertEqual(
            codec.AKSIdentityCreateV5Response.decode(data),
            codec.AKSIdentityCreateV5Response(live_handle=42, kek_material=b"abc"),
        )

    def test_rejects_malformed_response(self):
        with self.assertRaisesRegex(codec.AKSIdentityCreateCodecError, "truncated"):
            codec.AKSIdentityCreateV5Response.decode(struct.pack("<IiI", 5, 42, 4) + b"x")

    def test_rejects_response_trailing_bytes(self):
        with self.assertRaisesRegex(codec.AKSIdentityCreateCodecError, "trailing"):
            codec.AKSIdentityCreateV5Response.decode(struct.pack("<IiI", 5, 42, 0) + b"x")

    def test_create_response_limit_matches_for_bytes_and_mutable_buffers(self):
        accepted_kek = bytes(codec.MAX_BODY_BYTES - 12)
        rejected_kek = bytes(codec.MAX_BODY_BYTES - 8)
        for response_type, version in (
            (codec.AKSIdentityCreateV4Response, codec.CREATE_V4_VERSION),
            (codec.AKSIdentityCreateV5Response, codec.VERSION),
        ):
            with self.subTest(version=version, boundary="accepted"):
                body = struct.pack("<IiI", version, 42, len(accepted_kek)) + accepted_kek
                self.assertEqual(len(body), codec.MAX_BODY_BYTES)
                self.assertEqual(len(response_type.decode(body).kek_material), len(accepted_kek))
                self.assertEqual(
                    response_type.inspect_mutable(bytearray(body)),
                    (42, len(accepted_kek)),
                )
            with self.subTest(version=version, boundary="rejected"):
                body = struct.pack("<IiI", version, 42, len(rejected_kek)) + rejected_kek
                self.assertGreater(len(body), codec.MAX_BODY_BYTES)
                with self.assertRaisesRegex(
                    codec.AKSIdentityCreateCodecError,
                    "endpoint body limit",
                ):
                    response_type.decode(body)
                with self.assertRaisesRegex(
                    codec.AKSIdentityCreateCodecError,
                    "endpoint body limit",
                ):
                    response_type.inspect_mutable(bytearray(body))

    def test_copy_keybag_v1_round_trip_and_saved_object(self):
        request_value = codec.AKSIdentityCopyKeybagV1Request(
            session=0x0102030405060708,
            live_handle=42,
        )
        self.assertEqual(
            codec.AKSIdentityCopyKeybagV1Request.decode(request_value.encode()),
            request_value,
        )
        response = struct.pack("<II", codec.EXPORT_VERSION, 3) + b"key\0"
        self.assertEqual(
            codec.AKSIdentityCopyKeybagV1Response.decode(response).saved_keybag,
            b"key",
        )
        with self.assertRaisesRegex(codec.AKSIdentityCreateCodecError, "empty"):
            codec.AKSIdentityCopyKeybagV1Response.decode(
                struct.pack("<II", codec.EXPORT_VERSION, 0)
            )

    def test_export_response_limit_matches_for_bytes_and_mutable_buffers(self):
        accepted_keybag = b"k" * (codec.MAX_BODY_BYTES - 8)
        accepted = (
            struct.pack("<II", codec.EXPORT_VERSION, len(accepted_keybag))
            + accepted_keybag
        )
        self.assertEqual(len(accepted), codec.MAX_BODY_BYTES)
        self.assertEqual(
            len(codec.AKSIdentityCopyKeybagV1Response.decode(accepted).saved_keybag),
            len(accepted_keybag),
        )
        mutable = bytearray(accepted)
        extracted = codec.AKSIdentityCopyKeybagV1Response.extract_mutable(mutable)
        self.assertIsInstance(extracted, bytearray)
        self.assertEqual(len(extracted), len(accepted_keybag))
        self.assertEqual(extracted, accepted_keybag)
        extracted[:] = bytes(len(extracted))
        self.assertEqual(mutable, accepted)

        rejected_keybag = bytes(codec.MAX_BODY_BYTES - 4)
        rejected = (
            struct.pack("<II", codec.EXPORT_VERSION, len(rejected_keybag))
            + rejected_keybag
        )
        self.assertGreater(len(rejected), codec.MAX_BODY_BYTES)
        with self.assertRaisesRegex(
            codec.AKSIdentityCreateCodecError,
            "endpoint body limit",
        ):
            codec.AKSIdentityCopyKeybagV1Response.decode(rejected)
        with self.assertRaisesRegex(
            codec.AKSIdentityCreateCodecError,
            "endpoint body limit",
        ):
            codec.AKSIdentityCopyKeybagV1Response.extract_mutable(bytearray(rejected))


class AKSIdentityCreateV4Tests(unittest.TestCase):
    # Fixed independently observed request body for the bridgeOS 23P2048 layout.
    wire = bytes.fromhex(
        "04000000 0807060504030201 00410000 ffffffff"
        "10000000 0102030405060708090a0b0c0d0e0f10"
        "00000000 10000000 000102030405060708090a0b0c0d0e0f"
        "00000000 0600000000000000"
    )

    def value(self):
        return codec.AKSIdentityCreateV4Request(
            session=0x0102030405060708,
            internal_flags=0x4100,
            effective_bag_handle=-1,
            item1=bytes(range(1, 17)),
            item2=b"",
            account_uuid=bytes(range(16)),
            item3=b"",
            original_flags=6,
        )

    def test_fixed_wire_fixture_round_trips(self):
        self.assertEqual(self.value().encode(), self.wire)
        self.assertEqual(codec.AKSIdentityCreateV4Request.decode(self.wire), self.value())

    def test_v4_and_v5_requests_are_not_interchangeable(self):
        with self.assertRaisesRegex(codec.AKSIdentityCreateCodecError, "version"):
            codec.AKSIdentityCreateV5Request.decode(self.wire)
        with self.assertRaisesRegex(codec.AKSIdentityCreateCodecError, "version"):
            codec.AKSIdentityCreateV4Request.decode(request().encode())
        version_only_rewrite = struct.pack("<I", 4) + request().encode()[4:]
        with self.assertRaisesRegex(codec.AKSIdentityCreateCodecError, "trailing"):
            codec.AKSIdentityCreateV4Request.decode(version_only_rewrite)

    def test_every_truncation_is_rejected(self):
        for length in range(len(self.wire)):
            with self.subTest(length=length):
                with self.assertRaises(codec.AKSIdentityCreateCodecError):
                    codec.AKSIdentityCreateV4Request.decode(self.wire[:length])

    def test_response_version_selects_the_decoder(self):
        wire = bytes.fromhex("04000000 2a000000 03000000 61626300")
        self.assertEqual(
            codec.AKSIdentityCreateV4Response.decode(wire),
            codec.AKSIdentityCreateV4Response(live_handle=42, kek_material=b"abc"),
        )
        self.assertEqual(
            codec.AKSIdentityCreateV4Response.inspect_mutable(bytearray(wire)),
            (42, 3),
        )
        with self.assertRaisesRegex(codec.AKSIdentityCreateCodecError, "version"):
            codec.AKSIdentityCreateV5Response.decode(wire)


if __name__ == "__main__":
    unittest.main()
