import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Scripts import github

TIP = "e5d8a9f551b1e2a96e2f968696b460b65a7dad2e"
FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def fixture(name):
    with open(os.path.join(FIXTURES, name), encoding="utf-8") as f:
        return f.read()


class GetCommitsTest(unittest.TestCase):
    def get_commits_with(self, html):
        g = github.Github()
        with patch.object(g.fetcher, "fetch_and_parse_content", return_value=html):
            return g.get_commits("lzhoang2801", "OpCore-Simplify")

    def test_nested_payload_resolves_tip(self):
        commits = self.get_commits_with(fixture("commits_nested.html"))
        self.assertEqual(commits["commitGroups"][0]["commits"][0]["oid"], TIP)

    def test_nested_payload_preserves_current_commit(self):
        commits = self.get_commits_with(fixture("commits_nested.html"))
        self.assertEqual(commits["currentCommit"]["oid"], TIP)

    def test_legacy_shape_still_works(self):
        commits = self.get_commits_with(fixture("commits_legacy.html"))
        self.assertEqual(commits["commitGroups"][0]["commits"][0]["oid"], TIP)

    def test_unparseable_page_raises_naming_repo_and_branch(self):
        with self.assertRaises(ValueError) as ctx:
            self.get_commits_with(fixture("commits_empty.html"))
        self.assertIn("OpCore-Simplify", str(ctx.exception))
        self.assertIn("main", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
