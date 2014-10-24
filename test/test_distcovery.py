import unittest

from distcovery import Test

class TestDistcovery(unittest.TestCase):
    def test_creation(self):
        test = Test()
        self.assertTrue(isinstance(test, Test))

    def test_collect_modules(self):
        test = Test()
        test.collect_modules()
        self.assertTrue(hasattr(test, 'test_modules'))
        self.assertEqual(test.test_modules, {})

if __name__ == '__main__':
    unittest.main()

