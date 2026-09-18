# SPDX-License-Identifier: MIT
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest import mock


SOURCE = Path(__file__).parents[1]
sys.path.insert(0, str(SOURCE))
import t2_activation_bundle as bundle


def identifier(number: int) -> str:
    return str(uuid.UUID(int=number))


class ActivationBundleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.users = Path(self.temporary.name) / "users"
        self.users.mkdir(mode=0o700)
        self.user_root = self.users / "1000"
        self.user_root.mkdir(mode=0o700)
        self.identities = self.user_root / "identities"
        self.identities.mkdir(mode=0o700)
        self.operation_id = identifier(1)
        self.account_uuid = identifier(2)
        self.bag_uuid = identifier(3)
        self.store = bundle.ActivationBundleStore(
            root=self.identities,
            operation_id=self.operation_id,
            account_uuid=self.account_uuid,
            linux_uid=1000,
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_stage_then_atomically_publish_complete_generation(self) -> None:
        secret = bytearray(range(1, 17))
        secret_digest = hashlib.sha256(secret).hexdigest()
        self.assertEqual(self.store.stage(secret), secret_digest)
        self.assertEqual(secret, bytearray(16))
        self.assertTrue(self.store.pending_secret_path.exists())
        self.assertFalse(self.store.final_directory.exists())

        recovered = None
        with self.store.staged_secret(secret_digest) as staged:
            recovered = staged
            self.assertEqual(staged, bytearray(range(1, 17)))
        self.assertEqual(recovered, bytearray(16))

        saved = bytearray(b"saved-keybag")
        saved_digest = hashlib.sha256(saved).hexdigest()
        committed = self.store.commit(
            saved,
            expected_keybag_sha256=saved_digest,
            activation_secret_sha256=secret_digest,
            bag_uuid=self.bag_uuid,
        )
        self.assertEqual(saved, bytearray(len(b"saved-keybag")))
        self.assertFalse(self.store.pending_directory.exists())
        self.assertEqual(committed.directory, self.identities / self.operation_id)
        self.assertEqual(committed.keybag_path.read_bytes(), b"saved-keybag")
        self.assertEqual(
            committed.activation_secret_path.read_bytes(), bytes(range(1, 17))
        )
        for path in (
            committed.keybag_path,
            committed.activation_secret_path,
            committed.manifest_path,
        ):
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        manifest = json.loads(committed.manifest_path.read_bytes())
        self.assertEqual(manifest["phase"], "complete")
        self.assertEqual(manifest["activation_secret_sha256"], secret_digest)
        self.assertNotIn(bytes(range(1, 17)).hex(), committed.manifest_path.read_text())
        replay = bytearray(b"saved-keybag")
        reconciled = self.store.commit(
            replay,
            expected_keybag_sha256=saved_digest,
            activation_secret_sha256=secret_digest,
            bag_uuid=self.bag_uuid,
        )
        self.assertEqual(replay, bytearray(len(b"saved-keybag")))
        self.assertEqual(reconciled.manifest_sha256, committed.manifest_sha256)

    def test_stage_syncs_pending_generation_then_parent(self) -> None:
        actual_sync = bundle._sync_directory
        synced = []

        def record_sync(path: Path) -> None:
            synced.append(path)
            actual_sync(path)

        with mock.patch.object(bundle, "_sync_directory", side_effect=record_sync):
            self.store.stage(bytearray(range(1, 17)))

        self.assertEqual(
            synced,
            [self.store.pending_directory, self.store.root],
        )

    def test_stage_parent_sync_failure_prevents_success_and_wipes_input(self) -> None:
        secret = bytearray(range(1, 17))
        actual_sync = bundle._sync_directory

        def fail_parent_sync(path: Path) -> None:
            if path == self.store.root:
                raise bundle.ActivationBundleError(
                    "activation bundle directory sync failed"
                )
            actual_sync(path)

        with mock.patch.object(bundle, "_sync_directory", side_effect=fail_parent_sync):
            with self.assertRaisesRegex(
                bundle.ActivationBundleError,
                "directory sync failed",
            ):
                self.store.stage(secret)

        self.assertEqual(secret, bytearray(16))
        self.assertTrue(self.store.pending_secret_path.exists())
        self.assertFalse(self.store.final_directory.exists())

    def test_commit_retry_syncs_parent_after_rename_sync_failure(self) -> None:
        secret_digest = self.store.stage(bytearray(range(1, 17)))
        keybag = b"saved-keybag"
        keybag_digest = hashlib.sha256(keybag).hexdigest()
        actual_sync = bundle._sync_directory

        def fail_parent_sync(path: Path) -> None:
            if path == self.store.root:
                raise bundle.ActivationBundleError(
                    "activation bundle directory sync failed"
                )
            actual_sync(path)

        with mock.patch.object(bundle, "_sync_directory", side_effect=fail_parent_sync):
            with self.assertRaisesRegex(
                bundle.ActivationBundleError,
                "directory sync failed",
            ):
                self.store.commit(
                    bytearray(keybag),
                    expected_keybag_sha256=keybag_digest,
                    activation_secret_sha256=secret_digest,
                    bag_uuid=self.bag_uuid,
                )

        self.assertFalse(self.store.pending_directory.exists())
        self.assertTrue(self.store.final_directory.exists())

        synced = []

        def record_sync(path: Path) -> None:
            synced.append(path)
            actual_sync(path)

        with mock.patch.object(bundle, "_sync_directory", side_effect=record_sync):
            reconciled = self.store.commit(
                bytearray(keybag),
                expected_keybag_sha256=keybag_digest,
                activation_secret_sha256=secret_digest,
                bag_uuid=self.bag_uuid,
            )

        self.assertEqual(synced, [self.store.root])
        self.assertEqual(reconciled.directory, self.store.final_directory)

    def test_unsafe_or_interrupted_staging_fails_closed_and_wipes_input(self) -> None:
        unsafe = Path(self.temporary.name) / "unsafe"
        unsafe.mkdir(mode=0o755)
        with self.assertRaisesRegex(bundle.ActivationBundleError, "not private"):
            bundle.ActivationBundleStore(
                root=unsafe,
                operation_id=identifier(10),
                account_uuid=identifier(11),
                linux_uid=1000,
            )

        secret = bytearray(range(1, 17))
        digest = self.store.stage(secret)
        self.store.pending_secret_path.chmod(0o644)
        with self.assertRaisesRegex(bundle.ActivationBundleError, "metadata"):
            with self.store.staged_secret(digest):
                pass

        second_root = self.user_root / "second-identities"
        second_root.mkdir(mode=0o700)
        second_store = bundle.ActivationBundleStore(
            root=second_root,
            operation_id=identifier(20),
            account_uuid=identifier(21),
            linux_uid=1000,
        )
        secret = bytearray(range(1, 17))
        with mock.patch.object(bundle.os, "write", side_effect=OSError("short")):
            with self.assertRaises(bundle.ActivationBundleError):
                second_store.stage(secret)
        self.assertEqual(secret, bytearray(16))
        self.assertTrue(second_store.pending_directory.exists())
        self.assertFalse(second_store.final_directory.exists())

        third_root = self.user_root / "third-identities"
        third_root.mkdir(mode=0o700)
        third_store = bundle.ActivationBundleStore(
            root=third_root,
            operation_id=identifier(30),
            account_uuid=identifier(31),
            linux_uid=1000,
        )
        digest = third_store.stage(bytearray(range(1, 17)))
        partial_keybag = third_store.pending_directory / "user.kb"
        partial_keybag.write_bytes(b"partial")
        partial_keybag.chmod(0o600)
        partial_manifest = third_store.pending_directory / "manifest.json"
        partial_manifest.write_bytes(b"{")
        partial_manifest.chmod(0o600)
        saved = bytearray(b"saved-keybag")
        committed = third_store.commit(
            saved,
            expected_keybag_sha256=hashlib.sha256(b"saved-keybag").hexdigest(),
            activation_secret_sha256=digest,
            bag_uuid=identifier(32),
        )
        self.assertEqual(committed.keybag_path.read_bytes(), b"saved-keybag")
        self.assertFalse(third_store.pending_directory.exists())


if __name__ == "__main__":
    unittest.main()
