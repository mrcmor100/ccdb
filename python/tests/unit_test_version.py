import unittest

class PathUtilsTest(unittest.TestCase):

    def test_version(self):
        # No exception while importing here
        import ccdb.version

        self.assertTrue(ccdb.version.major == 2)
