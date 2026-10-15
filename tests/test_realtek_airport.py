"""Run with python -m unittest discover -s tests."""
import copy
import plistlib
import tempfile
import unittest
from pathlib import Path

from Scripts import realtek_airport, utils
from Scripts.datasets import kext_data, pci_data
from Scripts.github import Github
from Scripts.gathering_files import gatheringFiles
from Scripts.kext_maestro import KextMaestro


class RealtekAirPortTests(unittest.TestCase):
    def maestro(self):
        maestro = KextMaestro()
        maestro.kexts = copy.deepcopy(kext_data.kexts)
        for kext in maestro.kexts:
            kext.checked = False
        return maestro

    def test_selection_and_dependencies(self):
        for major in range(17, 27):
            with self.subTest(major=major):
                maestro = self.maestro()
                version = '{}.0.0'.format(major)
                for name in realtek_airport.selected_kexts(version):
                    self.assertTrue(maestro.check_kext(kext_data.kext_index_by_name[name], version))
                expected = set()
                if 18 <= major <= 20:
                    expected = {'Realtek88LegacyAirport', 'HS80211Family'}
                elif major == 22:
                    expected = {'AirPort_RTW88'}
                elif 23 <= major <= 25:
                    expected = {'AirPort_RTW88', 'IO80211FamilyLegacy', 'IOSkywalkFamily', 'AMFIPass', 'Lilu'}
                self.assertEqual({k.name for k in maestro.kexts if k.checked}, expected)

    def test_manual_modern_selection_adds_stack(self):
        maestro = self.maestro()
        self.assertTrue(maestro.check_kext(kext_data.kext_index_by_name['AirPort_RTW88'], '25.0.0'))
        self.assertTrue(all(maestro.kexts[kext_data.kext_index_by_name[n]].checked
                            for n in ['IOSkywalkFamily', 'IO80211FamilyLegacy', 'AMFIPass']))

    def test_unsupported_versions_cannot_force_load(self):
        for name, version in [('AirPort_RTW88', '21.0.0'), ('Realtek88LegacyAirport', '21.0.0'),
                              ('AirPort_RTW88', '26.0.0')]:
            with self.subTest(name=name, version=version):
                self.assertFalse(self.maestro().check_kext(kext_data.kext_index_by_name[name], version, True))

    def test_asset_name_and_pci_ids(self):
        github = Github.__new__(Github)
        self.assertEqual(github.extract_asset_name('Realtek-AirPort-Family-1.0.0.zip'), 'RealtekAirPortFamily')
        self.assertEqual(set(pci_data.RealtekAirPortIDs),
                         {'10EC-B822', '10EC-C822', '10EC-C82F', '10EC-C821', '10EC-B821'})
        self.assertTrue(set(pci_data.RealtekAirPortIDs).issubset(pci_data.WirelessCardIDs))

    def test_combined_archive_staging(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gather = gatheringFiles.__new__(gatheringFiles)
            gather.temporary_dir = str(root / 'extracted')
            gather.ock_files_dir = str(root / 'cache')
            gather.utils = utils.Utils()
            gather.kext = self.maestro()
            product = 'RealtekAirPortFamily'
            paths = ['Airport_RTW88/AirPort_RTW88.kext',
                     'LegacyAirport/Realtek88LegacyAirport.kext',
                     'LegacyAirport/HS80211Family.kext',
                     'Sonoma - Tahoe/AirPort_RTW88.kext',
                     'Sonoma - Tahoe/IOSkywalkFamily.kext',
                     'Sonoma - Tahoe/IO80211FamilyLegacy.kext',
                     'Sonoma - Tahoe/AMFIPass.kext']
            for relative in paths:
                contents = root / 'extracted' / product / relative / 'Contents'
                contents.mkdir(parents=True)
                (contents / 'Info.plist').write_bytes(plistlib.dumps({
                    'CFBundleIdentifier': 'test.' + Path(relative).stem,
                    'CFBundleVersion': '1.0.0'}))
            destination = root / 'cache' / product
            destination.mkdir(parents=True)
            self.assertTrue(gather.move_bootloader_kexts_to_product_directory(product))
            self.assertEqual({p.name for p in destination.iterdir()},
                             {'AirPort_RTW88.kext', 'Realtek88LegacyAirport.kext', 'HS80211Family.kext'})
            self.assertEqual(len(list(destination.rglob('Info.plist'))), 3)


if __name__ == '__main__':
    unittest.main()
