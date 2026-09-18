"""Check lookup behavior and reject broken research routes."""
from contextlib import contextmanager
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import research
import check_research

ROOT = Path(__file__).resolve().parents[2]


@contextmanager
def copy_collection():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        for name in ('docs', 'catalog'):
            shutil.copytree(ROOT / name, root / name)
        yield root


def save_catalog(root, catalog):
    (root / 'catalog/research-map.json').write_text(json.dumps(catalog))


class DiscoveryTests(unittest.TestCase):
    def test_json_lookalikes_are_rejected_and_escaped_identifiers_are_preserved(self):
        with copy_collection() as root:
            path = root / 'catalog/research-map.json'
            catalog = research.read_catalog(root)
            catalog['purpose'] += ' ' + chr(0x2013) + ' I' + chr(0x00B2) + 'C'
            path.write_text(json.dumps(catalog, ensure_ascii=False))
            errors, _ = check_research.verify(root)
            warning = next(e for e in errors if 'non-ASCII JSON characters' in e)
            self.assertIn('catalog/research-map.json', warning)
            self.assertIn('U+00B2', warning)
            self.assertIn('U+2013', warning)
            path.write_text(json.dumps(catalog, ensure_ascii=True))
            self.assertEqual(json.loads(path.read_text()), catalog)
            errors, _ = check_research.verify(root)
            self.assertFalse(any('non-ASCII JSON characters' in e for e in errors))

    def test_linux_firmware_and_device_names_find_the_same_topic(self):
        catalog = research.read_catalog(ROOT)
        cases = {'SEP': 'sep', 'AppleKeyStore': 'sep', '05ac:8104': 'las',
                 'Lid Angle': 'las', 'LAS': 'las', 'ISP': 'camera-isp',
                 'AppleM8CameraInterface': 'camera-isp', 'gmux': 'graphics',
                 'i915': 'graphics', 'sampleTime': 'bridge-audio',
                 'aveserverd': 'ave', 'pmu,d2449': 'rtc'}
        for query, expected in cases.items():
            with self.subTest(query=query):
                self.assertEqual(research.search(catalog, query)[0]['id'], expected)
        self.assertEqual(research.search(catalog, 'no-such-component'), [])
        self.assertEqual(research.search(catalog, '---'), [])
        self.assertEqual([x['id'] for x in research.search(catalog, 'ISP')], ['camera-isp'])

    def test_shared_aop_name_stays_ambiguous(self):
        catalog = research.read_catalog(ROOT)
        results = research.search(catalog, 'AOP', 2)
        self.assertEqual({r['id'] for r in results}, {'aop-audio', 'aop-sensors'})
        with self.assertRaisesRegex(ValueError, 'unique topic ID'):
            research.show(ROOT, catalog, 'AOP')

    def test_show_preserves_evidence_limits_and_line_ranges(self):
        result = research.show(ROOT, research.read_catalog(ROOT), 'ISP')
        finding = next(f for f in result['findings'] if f['id'] == 'camera-internal-exposure-path')
        self.assertIn('unresolved', finding['scope'])
        self.assertIn('caches the original input', finding['finding'])
        for ref in result['references']:
            lines = (ROOT / ref['reference'].split('#')[0]).read_text().splitlines()
            self.assertGreaterEqual(ref['line_start'], 1)
            self.assertLessEqual(ref['line_end'], len(lines))
        las = research.show(ROOT, research.read_catalog(ROOT), 'las')
        edge = next(r for r in las['relationships'] if r['kind'] == 'possible-owner')
        self.assertEqual(edge['evidence'], 'inferred')
        self.assertIn('not proven', edge['description'])

    def test_unknown_finding_and_unindexed_chapter_are_rejected(self):
        with copy_collection() as root:
            catalog = research.read_catalog(root)
            catalog['topics'][0]['finding_ids'].append('nonexistent-finding')
            save_catalog(root, catalog)
            (root / 'docs/forgotten.md').write_text('# Forgotten analysis\n')
            errors = research.validate(root)
            self.assertTrue(any('unknown findings' in e for e in errors))
            self.assertTrue(any('document inventory mismatch' in e for e in errors))

    def test_deleted_heading_is_rejected(self):
        with copy_collection() as root:
            path = root / 'docs/platform/pci-services-and-dma.md'
            path.write_text(path.read_text().replace('## Reset and queue boundaries', '## Renamed without updating references'))
            self.assertTrue(any('missing heading' in e for e in research.validate(root)))

    def test_scope_and_generated_map_changes_are_detected(self):
        with copy_collection() as root:
            path = root / 'docs/README.md'
            path.write_text(path.read_text() + '\nUntracked editorial change.\n')
            self.assertTrue(any('generated map stale' in e for e in research.validate(root)))

    def test_reference_cannot_escape_repository(self):
        with self.assertRaisesRegex(ValueError, 'escaping'):
            research.location(ROOT, '../outside.md')
        with self.assertRaisesRegex(ValueError, 'repository reference'):
            research.location(ROOT, 'https://example.org/reference')

    def test_interface_map_keeps_transport_and_firmware_owner_separate(self):
        result = research.show(ROOT, research.read_catalog(ROOT), 'las')
        route = result['interfaces'][0]
        self.assertEqual(route['parent'], 'bce')
        self.assertIn('does not establish', route['scope'])
        with copy_collection() as root:
            catalog = research.read_catalog(root)
            catalog['interfaces'][0]['parent'] = 'las-usb'
            save_catalog(root, catalog)
            self.assertTrue(any('cyclic interface parent' in e for e in research.validate(root)))

    def test_nested_section_range_stops_at_next_peer(self):
        spans = research.heading_spans('# Main\n\n## One\nx\n### Nested\ny\n## Two\nz\n')
        self.assertEqual(spans['one'], (3, 6))
        self.assertEqual(spans['nested'], (5, 6))

    def test_current_collection_is_consistent(self):
        self.assertEqual(research.validate(ROOT), [])


if __name__ == '__main__':
    unittest.main()
