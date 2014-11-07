import unittest
import re

from distcovery.exceptions import NoMoreAttempts
from distcovery.importer import RandomUniqueNames

class TestRandomUniqueNames(unittest.TestCase):
    def test_creation(self):
        random_unique_names = RandomUniqueNames()
        self.assertTrue(isinstance(random_unique_names, RandomUniqueNames))

    def test_random_name(self):
        random_unique_names = RandomUniqueNames()
        self.assertTrue(re.match('X_\\d+$', random_unique_names.random_name()))

    def test_new(self):
        random_unique_names = RandomUniqueNames()
        self.assertTrue(re.match('X_\\d+$', random_unique_names.new()))

    def test_new_big_set(self):
        random_unique_names = RandomUniqueNames(limit=10000, length=2)

        names = set()
        for i in range(100):
            name = random_unique_names.new()
            self.assertNotIn(name, names)

            names.add(name)

        self.assertEqual(len(names), 100)

    def test_new_limit(self):
        random_unique_names = RandomUniqueNames(limit=10, length=2)

        with self.assertRaises(NoMoreAttempts) as ctx:
            for i in range(101):
                random_unique_names.new()

        self.assertEqual(ctx.exception.message,
                         NoMoreAttempts.template % \
                         {'limit': 10,
                          'limit_suffix': NoMoreAttempts.number_suffix(10),
                          'length': 2,
                          'length_suffix': NoMoreAttempts.number_suffix(2)})

if __name__ == '__main__':
    unittest.main()

