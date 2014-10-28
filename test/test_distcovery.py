import unittest
import os
import re

from distutils.cmd import Command
from distutils.dist import Distribution

from mocks import mock_directory_tree

from distcovery import _TEST_PACKAGE_REGEX, _make_name, _sub_item, Test

class TestDistcovery(unittest.TestCase):
    def test__make_name(self):
        self.assertEqual(_make_name(('xxx', 'yyy', 'zzz')), 'xxx.yyy.zzz')

    def test__sub_item(self):
        match = re.match(_TEST_PACKAGE_REGEX, 'test_sub_item')
        self.assertEqual(_sub_item(('item',), ('test_item',), match),
                         (('item', 'sub_item'), ('test_item', 'test_sub_item')))

class TestDistcoveryTest(unittest.TestCase):
    def setUp(self):
        super(TestDistcoveryTest, self).setUp()

        self.listdir = os.listdir
        self.isfile = os.path.isfile
        self.isdir = os.path.isdir

    def tearDown(self):
        os.path.isdir = self.isdir
        os.path.isfile = self.isfile
        os.listdir = self.listdir

        super(TestDistcoveryTest, self).tearDown()

    def test_class_attributes(self):
        self.assertTrue(issubclass(Test, Command))

    def test_creation(self):
        test = Test(Distribution())
        self.assertTrue(isinstance(test, Test))

    def test_collect_modules_empty(self):
        os.listdir, os.path.isfile, os.path.isdir = mock_directory_tree({})

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

