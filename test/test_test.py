import unittest
import os
import sys
import StringIO

from distutils import log
from distutils.cmd import Command
from distutils.dist import Distribution

from utils import mock_directory_tree, PreserveOs

# Reload module to run its global section under coverage supervision
import distcovery.test
reload(distcovery.test)

from distcovery.exceptions import NoTestModulesException, \
                                  UnknownModulesException
from distcovery.test import Test

class TestTest(PreserveOs, unittest.TestCase):
    def setUp(self):
        super(TestTest, self).setUp()

        log.set_verbosity(1)

        self.__stdout = sys.stdout
        self.stdout = StringIO.StringIO()
        sys.stdout = self.stdout

        self.__unittest_main = unittest.main

    def tearDown(self):
        unittest.main = self.__unittest_main

        sys.stdout = self.__stdout

        super(TestTest, self).tearDown()

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
        test.collect_modules()
        test.print_test_modules()

        self.assertEqual(self.stdout.getvalue(),
                         'Test suites:\n' \
                         '\tsub_third.sub_first\n' \
                         '\tsecond\n' \
                         '\tsub_first.sub_first\n' \
                         '\tsub_third.sub_second.sub_first\n' \
                         '\tfirst\n')

    def test_validate_modules_no_test_modules(self):
        test = Test(Distribution())
        test.test_modules = []

        with self.assertRaises(NoTestModulesException) as ctx:
            test.validate_modules([])

        self.assertEqual(ctx.exception.message,
                         NoTestModulesException.template % \
                         {'path': test.test_root})

    def test_validate_modules_unknown_modules(self):
        self.full_test_tree()

        test = Test(Distribution())
        test.test_root = '.'
        test.collect_modules()
        modules = ['first_unknown', 'third_unknown', 'fourth_unknown']
        with self.assertRaises(UnknownModulesException) as ctx:
            test.validate_modules(modules + ['second', 'first'])

        modules, suffix = UnknownModulesException.stringify_list(modules)
        self.assertEqual(ctx.exception.message,
                         UnknownModulesException.template % \
                         {'modules': modules, 'suffix': suffix})

    def test_validate_modules(self):
        self.full_test_tree()

        test = Test(Distribution())
        test.test_root = '.'
        test.collect_modules()
        test.validate_modules(['second', 'first'])

    def test_run_print_test_modules(self):
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

    def test_run(self):
        self.full_test_tree()

        arguments = []
        def main(*args, **kwargs):
            arguments.append((args, kwargs))

        unittest.main = main

        test = Test(Distribution())
        test.test_root = '.'
        test.module = 'first'
        test.run()

        self.assertEqual(arguments,
                         [(('test_first',),
                           {'argv': sys.argv[:1],
                            'exit': False,
                            'verbosity': 1})])

if __name__ == '__main__':
    unittest.main()

