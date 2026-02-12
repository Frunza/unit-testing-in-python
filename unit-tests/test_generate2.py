import unittest

import sys
sys.path.append('app')
from app.generate import formatLinks

class TestGenerate2(unittest.TestCase):

    def test_formatLinks_singleLink(self):
        """Should format a single link correctly"""
        links = [{"label": "GitLab", "url": "https://gitlab.com"}]
        result = formatLinks(links)
        self.assertEqual(result, "[GitLab](https://gitlab.com)")

if __name__ == '__main__':
    unittest.main()
