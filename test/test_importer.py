import unittest
import re
import sys
import imp

from utils import PreserveOs, ImportTrash

# Reload module to run its global section under coverage supervision
import distcovery.importer
reload(distcovery.importer)

from distcovery.exceptions import NoMoreAttempts
from distcovery.path import Package, walk
from distcovery.importer import _MODULE_NAME_PREFIX, _CASE_NAME_PREFIX, \
                                _enumerate_testmodules, _enumerate_testcases, \
                                RandomUniqueNames, Importer

class TestImporterGlobal(ImportTrash, unittest.TestCase):
    def test__enumerate_testmodules(self):
        test1 = imp.new_module('test1')
        test2 = imp.new_module('test2')
        test3 = imp.new_module('test3')

        global_section = {_MODULE_NAME_PREFIX + '1': test1,
                          _MODULE_NAME_PREFIX + '2': test2,
                          _MODULE_NAME_PREFIX + 'X': imp.new_module('testX'),
                          _MODULE_NAME_PREFIX + '3': test3,
                          _MODULE_NAME_PREFIX + '4': 'Some Data'}

        self.assertEqual(set(_enumerate_testmodules(global_section)),
                         set([test1, test2, test3]))

    def test__enumerate_testcases(self):
        test_module = imp.new_module('test1')
        test_module.__file__ = '<test package>'
        test_module.__path__ = []
        sys.modules['test1'] = test_module
        self.modules_trash.append('test1')

        exec('import unittest\n' \
             'class A(unittest.TestCase):\n' \
             '    pass\n' \
             'class B(unittest.TestCase):\n' \
             '    pass\n' \
             'class C(object):\n' \
             '    pass\n' \
             'class D:\n' \
             '    pass\n' \
             'c = C()\n', test_module.__dict__)

        global_section = {_MODULE_NAME_PREFIX + '1': test_module}

        testnames = set()
        testcases = set()
        for testname, testcase in _enumerate_testcases(global_section):
            testnames.add(testname)
            testcases.add(testcase.__name__)

        self.assertEqual(testnames, set([_CASE_NAME_PREFIX + '1',
                                         _CASE_NAME_PREFIX + '2']))
        self.assertEqual(testcases, set(['A', 'B']))

class TestRandomUniqueNames(unittest.TestCase):
    def test_creation(self):
        random_unique_names = RandomUniqueNames()
        self.assertTrue(isinstance(random_unique_names, RandomUniqueNames))

    def test_random_name(self):
        random_unique_names = RandomUniqueNames()
        self.assertRegexpMatches(random_unique_names.random_name(), '^X_\\d+$')

    def test_new(self):
        random_unique_names = RandomUniqueNames()
        self.assertRegexpMatches(random_unique_names.new(), '^X_\\d+$')

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

class TestImporter(ImportTrash, PreserveOs, unittest.TestCase):
    def __assert_source(self, source, *expected_modules):
        regex = 'import\\s(.*)\\sas\\s%s\\d+$' % re.escape(_MODULE_NAME_PREFIX)
        pattern = re.compile(regex)

        imported_modules = set()
        lines = source.split('\n')
        for line in lines[:-1]:
            match = pattern.match(line)
            self.assertNotEqual(match, None, 'Line %s doesn\'t matches ' \
                                             'regex "%s"' % (repr(line), regex))
            imported_modules.add(match.group(1))

        self.assertEqual(lines[-1], '')
        self.assertEqual(imported_modules, set(expected_modules))

    def test_creation(self):
        importer = Importer(Package(('test', 'base'), 'test'))

        self.assertIsInstance(importer, Importer)
        self.assertEqual(importer.aliases.keys(), [None])

        name = importer.aliases[None]
        self.assertRegexpMatches(name, '^X_\\d+$')
        self.assertEquals(importer.sources, {name: ''})

    def test_build_module(self):
        self.full_test_tree()

        importer = Importer(walk('.'))
        self.assertEqual(set(importer.aliases.keys()),
                         set((None, 'sub_first', 'sub_third',
                              'sub_third.sub_second')))

        name = importer.aliases[None]
        self.__assert_source(importer.sources[name],
                             'test_first',
                             'test_second',
                             'test_sub_first.test_sub_first',
                             'test_sub_third.test_sub_first',
                             'test_sub_third.test_sub_second.test_sub_first')

        name = importer.aliases['sub_first']
        self.__assert_source(importer.sources[name],
                             'test_sub_first.test_sub_first')

        name = importer.aliases['sub_third']
        self.__assert_source(importer.sources[name],
                             'test_sub_third.test_sub_first',
                             'test_sub_third.test_sub_second.test_sub_first')

        name = importer.aliases['sub_third.sub_second']
        self.__assert_source(importer.sources[name],
                             'test_sub_third.test_sub_second.test_sub_first')

    def test_find_module(self):
        self.full_test_tree()
        importer = Importer(walk('.'))

        name = importer.aliases[None]
        self.assertEqual(importer.find_module(name), importer)

    def test_find_module_non_test_module(self):
        self.full_test_tree()

        self.assertEqual(Importer(walk('.')).find_module('unittest'), None)

    def test_load_module(self):
        importer = Importer(Package(('test', 'base'), 'test'))
        importer.sources['test01'] = 'test = 1\n'
        self.modules_trash.append('test01')

        test01 = importer.load_module('test01')
        self.assertIsInstance(test01, type(sys))
        self.assertIn('test01', sys.modules)
        self.assertIs(test01, sys.modules['test01'])
        self.assertEqual(test01.__file__, '<test package>')
        self.assertEqual(test01.__path__, [])
        self.assertIs(test01.__loader__, importer)
        self.assertEqual(test01.__package__, 'test01')
        self.assertEqual(test01.test, 1)

    def test_load_module_failed(self):
        importer = Importer(Package(('test', 'base'), 'test'))
        importer.sources['test01'] = 'raise UserWarning(\'Test!\')\n'

        with self.assertRaises(UserWarning) as ctx:
            importer.load_module('test01')

        self.assertEqual(ctx.exception.message, 'Test!')
        self.assertNotIn('test01', sys.modules)

    def test_load_module_already_loaded(self):
        sys.modules['test01'] = 'test01'
        self.modules_trash.append('test01')

        importer = Importer(Package(('test', 'base'), 'test'))
        self.assertEqual(importer.load_module('test01'), 'test01')

    def test_load_module_global_testcase(self):
        importer = Importer(Package(('test', 'base'), 'test'))
        importer.sources['test01'] = 'import test02 as %s1\n' % _MODULE_NAME_PREFIX
        importer.sources['test02'] = 'import unittest\n' \
                                     'class Test(unittest.TestCase):\n' \
                                     '    pass\n'

        sys.meta_path.append(importer)
        self.meta_path_trash.append(importer)

        test01 = importer.load_module('test01')

        testname = _CASE_NAME_PREFIX + '1'
        self.assertIn(testname, test01.__dict__)

        testcase = test01.__dict__[testname]
        self.assertTrue(issubclass(testcase, unittest.TestCase))
        self.assertEqual(testcase.__name__, 'Test')

if __name__ == '__main__':
    unittest.main()

