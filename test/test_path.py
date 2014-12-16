import unittest
import os
import re
import collections

from utils import mock_directory_tree, PreserveOs

# Reload module to run its global section under coverage supervision
import distcovery.path
reload(distcovery.path)

from distcovery.exceptions import InvalidTestRoot
from distcovery.path import _TEST_PACKAGE_PATTERN, _TEST_MODULE_PATTERN, \
                            _is_package, _is_module, Importable, Package, \
                            _split_path, walk

class TestPath(PreserveOs, unittest.TestCase):
    def small_test_tree(self):
        tree = {('test_first.py',): None,
                ('test_second',): tuple(),
                ('test_third',): ('__init__.py', 'test_item.py'),
                ('test_third', '__init__.py'): None,
                ('test_third', 'test_item.py'): None,
                ('test_forth',): ('module.py',),
                ('test_forth', 'module.py'): None}
        os.listdir, os.path.isfile, os.path.isdir = mock_directory_tree(tree)

    def test__is_package(self):
        self.small_test_tree()

        self.assertFalse(_is_package('test_first.py'))
        self.assertFalse(_is_package('test_second'))
        self.assertTrue(_is_package('test_third'))
        self.assertFalse(_is_package('test_forth'))
        self.assertFalse(_is_package('test_fifth'))

    def test__is_module(self):
        self.small_test_tree()

        self.assertTrue(_is_module('test_first.py'))
        self.assertFalse(_is_module('test_second'))
        self.assertFalse(_is_module('test_third'))
        self.assertFalse(_is_module('test_forth'))
        self.assertFalse(_is_module('test_fifth'))

    def test__split_path(self):
        self.assertEqual(_split_path(os.path.join('1', '2', '3', '4', '5'),
                                     os.path.join('1', '2')),
                         ('3', '4', '5'))

    def test__split_path_invalid_root(self):
        tests = os.path.join('1', '2', '3', '4', '5')
        current = os.path.join('a', 'b')

        errors = []
        def raiser():
            try:
                _split_path(tests, current)
            except InvalidTestRoot as error:
                errors.append(error)
                raise

        self.assertRaises(InvalidTestRoot, raiser)
        self.assertEqual(str(errors[0]),
                         InvalidTestRoot.template % \
                         {'tests': tests, 'current': current})

    def test_walk(self):
        self.full_test_tree()

        content = {}
        for alias, importable in walk('.').content.iteritems():
            content[alias] = importable.str_name()

        self.assertEqual(content, self.expected_content)

class TestImportable(unittest.TestCase):
    def test_join_sequence(self):
        self.assertEqual(Importable.join_sequence(('1', '2', '3')), '1.2.3')

    def test_creation_default(self):
        importable = Importable(('test', 'base'), 'test')
        self.assertTrue(isinstance(importable, Importable))

        self.assertEqual(importable.base, ('test', 'base'))
        self.assertEqual(importable.path, 'test')
        self.assertEqual(importable.alias, tuple())
        self.assertEqual(importable.name, tuple())

    def test_creation(self):
        parent = Importable(('test', 'base'), 'test')
        match = _TEST_MODULE_PATTERN.match('test_module.py')

        importable = Importable(('test', 'base'), 'test', match, parent)
        self.assertTrue(isinstance(importable, Importable))

        self.assertEqual(importable.base, ('test', 'base'))
        self.assertEqual(importable.path, 'test')
        self.assertEqual(importable.alias, ('module',))
        self.assertEqual(importable.name, ('test_module',))

    def test_str_alias(self):
        parent = Importable(('test', 'base'), 'test')
        match = _TEST_PACKAGE_PATTERN.match('test_package')

        parent = Importable(('test', 'base'), 'test', match, parent)
        match = _TEST_MODULE_PATTERN.match('test_module.py')

        importable = Importable(('test', 'base'), 'test', match, parent)
        self.assertEqual(importable.str_alias(), 'package.module')

    def test_str_name(self):
        parent = Importable(('test', 'base'), 'test')
        match = _TEST_PACKAGE_PATTERN.match('test_package')

        parent = Importable(('test', 'base'), 'test', match, parent)
        match = _TEST_MODULE_PATTERN.match('test_module.py')

        importable = Importable(('test', 'base'), 'test', match, parent)
        self.assertEqual(importable.str_name(),
                         'test.base.test_package.test_module')

class TestPackage(PreserveOs, unittest.TestCase):
    def test_creation(self):
        package = Package(('test', 'base'), 'test')
        self.assertTrue(isinstance(package, Package))

        self.assertEqual(package.modules, [])
        self.assertEqual(package.packages, [])
        self.assertEqual(package.content, {})

    def test_listdir(self):
        self.full_test_tree()

        package = Package(('test', 'base'), '.')
        self.assertEqual(tuple(package.listdir()),
                         (('./__init__.py', '__init__.py'),
                          ('./test_first.py', 'test_first.py'),
                          ('./test_second.py', 'test_second.py'),
                          ('./test_sub_first', 'test_sub_first'),
                          ('./t_sub_first', 't_sub_first'),
                          ('./test_sub_third', 'test_sub_third')))

    def test_walk(self):
        self.full_test_tree()

        package = Package(tuple(), '.')
        content = {}
        for alias, importable in package.walk():
            content[alias] = importable.str_name()

        self.assertEqual(content, self.expected_content)

    def test_enumerate(self):
        self.full_test_tree()

        package = walk('.')
        self.assertEqual(tuple(package.enumerate(1)),
                         ((False, 1, 'first'),
                          (False, 1, 'second'),
                          (True, 1, 'sub_first'),
                          (False, 2, 'sub_first.sub_first'),
                          (True, 1, 'sub_third'),
                          (False, 2, 'sub_third.sub_first'),
                          (True, 2, 'sub_third.sub_second'),
                          (False, 3, 'sub_third.sub_second.sub_first')))

if __name__ == '__main__':
    unittest.main()

