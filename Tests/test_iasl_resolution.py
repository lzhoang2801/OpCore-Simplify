import os
import sys
import unittest
from unittest.mock import Mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Scripts import dsdt
from Scripts import github

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
ZIP_URL = "https://github.com/open-acpica/acpica/releases/download/20260408/iasl-win-20260408.zip"
EXE_URL = "https://github.com/open-acpica/acpica/releases/download/20260408/iasl.exe"


def fixture(name):
    with open(os.path.join(FIXTURES, name), encoding="utf-8") as f:
        return f.read()


def release_with_urls(urls):
    return {"tag": "x", "body": "", "assets": [{"url": u} for u in urls]}


def fresh_dsdt():
    d = dsdt.DSDT.__new__(dsdt.DSDT)
    d.github = Mock()
    return d


class GetLatestIaslTest(unittest.TestCase):
    def resolve(self, tag_to_release):
        d = fresh_dsdt()
        d.github.get_release_tags.return_value = list(tag_to_release)
        d.github.get_release_by_tag.side_effect = (
            lambda owner, repo, tag: tag_to_release[tag]
        )
        return d.get_latest_iasl()

    def test_skips_binary_less_release(self):
        url = self.resolve({
            "20260930": release_with_urls([
                "https://github.com/open-acpica/acpica/releases/download/20260930/iasl",
            ]),
            "20260408": release_with_urls([ZIP_URL]),
        })
        self.assertEqual(url, ZIP_URL)

    def test_prefers_versioned_zip_over_bare_exe(self):
        url = self.resolve({
            "20260408": release_with_urls([EXE_URL, ZIP_URL]),
        })
        self.assertEqual(url, ZIP_URL)

    def test_falls_back_to_exact_exe(self):
        url = self.resolve({
            "20260408": release_with_urls([
                "https://github.com/open-acpica/acpica/releases/download/20260408/iasl_dbg.exe",
                EXE_URL,
            ]),
        })
        self.assertEqual(url, EXE_URL)

    def test_returns_none_when_nothing_usable(self):
        url = self.resolve({
            "20260930": release_with_urls([
                "https://github.com/open-acpica/acpica/releases/download/20260930/acpica-unix-20260930.tar.gz",
            ]),
        })
        self.assertIsNone(url)


class GetReleaseTagsTest(unittest.TestCase):
    def test_tag_order_preserved(self):
        g = github.Github()
        g.fetcher.fetch_and_parse_content = Mock(
            return_value=fixture("releases_index.html")
        )
        self.assertEqual(
            g.get_release_tags("acpica", "acpica"),
            ["20260930", "20260408"],
        )

    def test_release_by_tag_reads_per_tag_assets(self):
        html_by_url = {
            "expanded_assets": fixture("expanded_assets_with_win.html"),
            "releases/tag": fixture("release_tag_body.html"),
        }
        g = github.Github()

        def fake_fetch(url):
            for key, html in html_by_url.items():
                if key in url:
                    return html
            raise AssertionError("unexpected url: " + url)

        g.fetcher.fetch_and_parse_content = Mock(side_effect=fake_fetch)
        release = g.get_release_by_tag("acpica", "acpica", "20260408")
        urls = [a["url"] for a in release["assets"]]
        self.assertIn(ZIP_URL, urls)
        self.assertIn("Version changelog", release["body"])


if __name__ == "__main__":
    unittest.main()
