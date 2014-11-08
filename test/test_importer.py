import unittest
import re

from utils import PreserveOs

from distcovery.exceptions import NoMoreAttempts
from distcovery.path import Package, walk
from distcovery.importer import RandomUniqueNames, Importer

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

class TestImporter(PreserveOs, unittest.TestCase):
    def test_creation(self):
        importer = Importer(Package(('test', 'base'), 'test'))

        self.assertIsInstance(importer, Importer)
        self.assertEqual(importer.aliases.keys(), ['*'])

        name = importer.aliases['*']
        self.assertRegexpMatches(name, '^X_\\d+$')
        self.assertEquals(importer.sources, {name: ''})

    def test_build_module(self):
        self.full_test_tree()

        importer = Importer(walk('.'))
        self.assertEqual(set(importer.aliases.keys()),
                         set(('*', 'sub_first', 'sub_third',
                              'sub_third.sub_second')))

        name = importer.aliases['*']
        self.assertEqual(set(importer.sources[name].split('\n')),
                         set(['import test_first',
                              'import test_second',
                              'import test_sub_first.test_sub_first',
                              'import test_sub_third.test_sub_first',
                              'import test_sub_third.test_sub_second.' \
                                     'test_sub_first',
                              '']))

        name = importer.aliases['sub_first']
        self.assertEqual(set(importer.sources[name].split('\n')),
                         set(['import test_sub_first.test_sub_first',
                              '']))

        name = importer.aliases['sub_third']
        self.assertEqual(set(importer.sources[name].split('\n')),
                         set(['import test_sub_third.test_sub_first',
                              'import test_sub_third.test_sub_second.' \
                                     'test_sub_first',
                              '']))

        name = importer.aliases['sub_third.sub_second']
        self.assertEqual(set(importer.sources[name].split('\n')),
                         set(['import test_sub_third.test_sub_second.' \
                                     'test_sub_first',
                              '']))

    def test_find_module(self):
        self.full_test_tree()
        importer = Importer(walk('.'))

        name = importer.aliases['*']
        self.assertEqual(importer.find_module(name), importer)

    def test_find_module_non_test_module(self):
        self.full_test_tree()

        self.assertEqual(Importer(walk('.')).find_module('unittest'), None)

if __name__ == '__main__':
    unittest.main()

