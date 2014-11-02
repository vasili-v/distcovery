import unittest
import os
import re
import collections

from utils import mock_directory_tree, PreserveOs

from distcovery.exceptions import InvalidTestRoot
from distcovery.path import _TEST_PACKAGE_REGEX, _make_name, _sub_item, \
                            _is_package, _is_module, _listdir, _walk_path, \
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

    def test__make_name(self):
        self.assertEqual(_make_name(('xxx', 'yyy', 'zzz')), 'xxx.yyy.zzz')

    def test__sub_item(self):
        match = re.match(_TEST_PACKAGE_REGEX, 'test_sub_item')
        self.assertEqual(_sub_item(match, ('item',), ('test_item',)),
                         (('item', 'sub_item'), ('test_item', 'test_sub_item')))

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

    def test__listdir(self):
        self.small_test_tree()

        generator = _listdir('test_third')
        self.assertTrue(isinstance(generator, collections.Iterable))
        self.assertEqual(list(generator),
                         [(os.path.join('test_third', '__init__.py'),
                           '__init__.py'),
                          (os.path.join('test_third', 'test_item.py'),
                           'test_item.py')])

    def test__walk_path(self):
        self.full_test_tree()

        self.assertEqual(tuple(_walk_path('.', tuple(), tuple())),
                         self.expected_modules)

    def test__split_path(self):
        self.assertEqual(_split_path(os.path.join('1', '2', '3', '4', '5'),
                                     os.path.join('1', '2')),
                         ['3', '4', '5'])

    def test__split_path_invalid_root(self):
        tests = os.path.join('1', '2', '3', '4', '5')
        current = os.path.join('a', 'b')
        with self.assertRaises(InvalidTestRoot) as ctx:
            _split_path(tests, current)

        self.assertEqual(ctx.exception.message,
                         InvalidTestRoot.template % \
                         {'tests': tests, 'current': current})

    def test_walk(self):
        self.full_test_tree()

        self.assertEqual(walk('.'), dict(self.expected_modules))

if __name__ == '__main__':
    unittest.main()

