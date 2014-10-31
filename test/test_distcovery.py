import unittest
import os
import re
import collections
import sys
import StringIO

from distutils import log
from distutils.cmd import Command
from distutils.dist import Distribution

from mocks import mock_directory_tree

from distcovery import _TEST_PACKAGE_REGEX, _make_name, _sub_item, \
                       _is_package, _is_module, _listdir, _walk_path, _walk, \
                       Test

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

    def full_test_tree(self):
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

        self.expected_modules = (('first', 'test_first'),
                                 ('second', 'test_second'),
                                 ('sub_first.sub_first',
                                  'test_sub_first.test_sub_first'),
                                 ('sub_third.sub_first',
                                  'test_sub_third.test_sub_first'),
                                 ('sub_third.sub_second.sub_first',
                                  'test_sub_third.test_sub_second.' \
                                      'test_sub_first'))

class TestDistcovery(PreserveOs, unittest.TestCase):
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

    def test__walk(self):
        self.full_test_tree()

        self.assertEqual(_walk('.'), dict(self.expected_modules))

class TestDistcoveryTest(PreserveOs, unittest.TestCase):
    def setUp(self):
        super(TestDistcoveryTest, self).setUp()

        log.set_verbosity(1)

        self.__stdout = sys.stdout
        self.stdout = StringIO.StringIO()
        sys.stdout = self.stdout

    def tearDown(self):
        sys.stdout = self.__stdout

        super(TestDistcoveryTest, self).tearDown()

    def test_class_attributes(self):
        self.assertTrue(issubclass(Test, Command))
        self.assertTrue(hasattr(Test, 'description'))
        self.assertTrue(hasattr(Test, 'user_options'))
        self.assertTrue(hasattr(Test, 'boolean_options'))

    def test_creation(self):
        test = Test(Distribution())
        self.assertTrue(isinstance(test, Test))
        self.assertEqual(test.module, None)
        self.assertEqual(test.coverage_base, None)
        self.assertEqual(test.coverage, None)
        self.assertEqual(test.test_root, 'test')

    def test_finalize_options(self):
        test = Test(Distribution())
        test.distribution.get_command_obj('install').install_purelib = 'test'

        test.finalize_options()
        self.assertEqual(test.coverage_base, 'test')

    def test_collect_modules_empty(self):
        tree = {('.',): tuple()}
        os.listdir, os.path.isfile, os.path.isdir = mock_directory_tree(tree)

        test = Test(Distribution())
        test.test_root = '.'
        test.collect_modules()
        self.assertTrue(hasattr(test, 'test_modules'))
        self.assertEqual(test.test_modules, {})

    def test_collect_modules(self):
        self.full_test_tree()

        test = Test(Distribution())
        test.test_root = '.'
        test.collect_modules()
        self.assertTrue(hasattr(test, 'test_modules'))
        self.assertEqual(test.test_modules, dict(self.expected_modules))

    def test_print_test_modules(self):
        self.full_test_tree()

        test = Test(Distribution())
        test.test_root = '.'
        test.print_test_modules()

        self.assertEqual(self.stdout.getvalue(),
                         'Test suites:\n' \
                         '\tsub_third.sub_first\n' \
                         '\tsecond\n' \
                         '\tsub_first.sub_first\n' \
                         '\tsub_third.sub_second.sub_first\n' \
                         '\tfirst\n')

    def test_run(self):
        self.full_test_tree()

        test = Test(Distribution())
        test.test_root = '.'
        test.run()

        self.assertEqual(self.stdout.getvalue(),
                         'Test suites:\n' \
                         '\tsub_third.sub_first\n' \
                         '\tsecond\n' \
                         '\tsub_first.sub_first\n' \
                         '\tsub_third.sub_second.sub_first\n' \
                         '\tfirst\n')

if __name__ == '__main__':
    unittest.main()

