"""Synthetic privacy/container checks, no private values or experiments."""
import gzip
import io
import unittest
import zipfile
from publication_snapshot import safe, scan


class PublicationChecks(unittest.TestCase):
    def test_paths(self):
        self.assertTrue(safe('experiments/example/record.json'))
        for bad in ('/absolute', '../escape', 'a/../../b', 'a\\b'):
            self.assertFalse(safe(bad))

    def test_token_and_path_detection(self):
        self.assertIn(['x', 'codingame_token'], scan('x', b'cgp_' + b'a' * 30))
        self.assertIn(['x', 'host_path'], scan('x', b'/' + b'Users' + b'/fakeuser/test'))
        self.assertEqual(scan('x', b'ordinary scientific report 10 wins'), [])

    def test_nested_containers(self):
        token = b'ghp_' + b'x' * 30
        self.assertIn(['x.json', 'github_token'], scan('x.json.gz', gzip.compress(token)))
        output = io.BytesIO()
        with zipfile.ZipFile(output, 'w') as archive:
            archive.writestr('data.pkl', token)
        self.assertIn(['model.pt::data.pkl', 'github_token'], scan('model.pt', output.getvalue()))

    def test_executable_and_unsafe_zip(self):
        self.assertIn(['x', 'compiled_executable_magic'], scan('x', b'\x7fELF' + b'fake'))
        output = io.BytesIO()
        with zipfile.ZipFile(output, 'w') as archive:
            archive.writestr('../bad', b'text')
        with self.assertRaises(AssertionError):
            scan('x.zip', output.getvalue())


if __name__ == '__main__':
    unittest.main()