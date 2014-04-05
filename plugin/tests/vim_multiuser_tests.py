import unittest
import vim_multiuser as sut


@unittest.skip("Don't forget to test!")
class VimMultiuserTests(unittest.TestCase):

    def test_example_fail(self):
        result = sut.vim_multiuser_example()
        self.assertEqual("Happy Hacking", result)
