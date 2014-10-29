import unittest
import os
import re
import collections

from distutils.cmd import Command
from distutils.dist import Distribution

from mocks import mock_directory_tree

from distcovery import _TEST_PACKAGE_REGEX, _make_name, _sub_item, \
                       _is_package, _is_module, _listdir, Test

class PreserveOs(object):
    def setUp(self):
        super(PreserveOs, self).setUp()

        self.__listdir = os.listdir
        self.__isfile = os.path.isfile
        self.__isdir = os.path.isdir

    def tearDown(self):
        os.path.isdir = self.__isdir
        os.path.isfile = self.__isfile
        os.listdir = self.__listdir

        super(PreserveOs, self).tearDown()

class TestDistcovery(PreserveOs, unittest.TestCase):
    def __arbitrary_tree(self):
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
        self.__arbitrary_tree()

        self.assertFalse(_is_package('test_first.py'))
        self.assertFalse(_is_package('test_second'))
        self.assertTrue(_is_package('test_third'))
        self.assertFalse(_is_package('test_forth'))
        self.assertFalse(_is_package('test_fifth'))

    def test__is_module(self):
        self.__arbitrary_tree()

        self.assertTrue(_is_module('test_first.py'))
        self.assertFalse(_is_module('test_second'))
        self.assertFalse(_is_module('test_third'))
        self.assertFalse(_is_module('test_forth'))
        self.assertFalse(_is_module('test_fifth'))

    def test__listdir(self):
        self.__arbitrary_tree()

        generator = _listdir('test_third')
        self.assertTrue(isinstance(generator, collections.Iterable))
        self.assertEqual(list(generator),
                         [(os.path.join('test_third', '__init__.py'),
                           '__init__.py'),
                          (os.path.join('test_third', 'test_item.py'),
                           'test_item.py')])

class TestDistcoveryTest(PreserveOs, unittest.TestCase):
    def test_class_attributes(self):
        self.assertTrue(issubclass(Test, Command))

    def test_creation(self):
        test = Test(Distribution())
        self.assertTrue(isinstance(test, Test))

    def test_collect_modules_empty(self):
        tree = {('.',): tuple()}
        os.listdir, os.path.isfile, os.path.isdir = mock_directory_tree(tree)

        test = Test(Distribution())
        test.test_root = '.'
        test.collect_modules()
        self.assertTrue(hasattr(test, 'test_modules'))
        self.assertEqual(test.test_modules, {})

    def test_collect_modules(self):
        tree = {('.',): ('__init__.py', 'test_first.py', 'test_second.py',
                         'test_sub_first', 't_sub_first', 'test_sub_third'),
                ('.', '__init__.py'): None,
                ('.', 'test_first.py'): None,
                ('.', 'test_second.py'): None,
                ('.', 'test_sub_first'): ('__init__.py', 'test_sub_first.py'),
                ('.', 'test_sub_first', '__init__.py'): None,
                ('.', 'test_sub_first', 'test_sub_first.py'): None,
                ('.', 't_sub_first'): ('__init__.py', 'test_sub_first.py'),
                ('.', 't_sub_first', '__init__.py'): None,
                ('.', 't_sub_first', 'test_sub_first.py'): None,
                ('.', 'test_sub_second'): ('test_sub_first.py',),
                ('.', 'test_sub_second', 'test_sub_first.py'): None,
                ('.', 'test_sub_third'): ('__init__.py', 'test_sub_first.py',
                                          'test_sub_second'),
                ('.', 'test_sub_third', '__init__.py'): None,
                ('.', 'test_sub_third', 'test_sub_first.py'): None,
                ('.', 'test_sub_third', 'test_sub_second'): \
                    ('__init__.py', 'test_sub_first.py', 't_sub_second.py'),
                ('.', 'test_sub_third', 'test_sub_second', '__init__.py'): None,
                ('.', 'test_sub_third', 'test_sub_second',
                 'test_sub_first.py'): None,
                ('.', 'test_sub_third', 'test_sub_second',
                 't_sub_second.py'): None}

        os.listdir, os.path.isfile, os.path.isdir = mock_directory_tree(tree)

        test = Test(Distribution())
        test.test_root = '.'
        test.collect_modules()
        self.assertTrue(hasattr(test, 'test_modules'))
        self.assertEqual(test.test_modules,
                         {'first': 'test_first',
                          'second': 'test_second',
                          'sub_first.sub_first': 'test_sub_first.' \
                                                 'test_sub_first',
                          'sub_third.sub_first': 'test_sub_third.' \
                                                 'test_sub_first',
                          'sub_third.sub_second.sub_first': \
                              'test_sub_third.test_sub_second.test_sub_first'})

if __name__ == '__main__':
    unittest.main()

