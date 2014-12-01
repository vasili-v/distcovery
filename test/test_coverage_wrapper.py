import unittest
import sys
import StringIO
import __builtin__
import os

from distutils import log

# Reload module to run its global section under coverage supervision
import distcovery.coverage_wrapper
reload(distcovery.coverage_wrapper)

from distcovery.coverage_wrapper import _DummyCoverage, Coverage, \
                                        _NO_COVERAGE_PACKAGE_WARNING

class _MockDistribution(object):
    def __init__(self, py_modules=None, packages=None):
        self.py_modules = py_modules if py_modules else []
        self.packages = packages if packages else []

class Test_DummyCoverage(unittest.TestCase):
    def test_creation(self):
        coverage = _DummyCoverage(source=[])
        self.assertTrue(isinstance(coverage, _DummyCoverage))

    def test_start(self):
        coverage = _DummyCoverage()
        self.assertEqual(coverage.start(), None)

    def test_stop(self):
        coverage = _DummyCoverage()
        self.assertEqual(coverage.stop(), None)

    def test_report(self):
        coverage = _DummyCoverage()
        self.assertEqual(coverage.report(), None)

class _MockCoverageModule(object):
    def __init__(self, coverage):
        self.coverage = coverage

class _MockCoverage(object):
    def __init__(self):
        self.creations = []
        self.starts = 0
        self.stops = 0

    def __call__(self, *args, **kwargs):
        self.creations.append((args, kwargs))
        return self

    def start(self):
        self.starts +=1

    def stop(self):
        self.stops += 1

    def report(self):
        print '\tThe report'

class TestCoverage(unittest.TestCase):
    def setUp(self):
        super(TestCoverage, self).setUp()

        self.__threshold = log.set_threshold(log.INFO)

        self.__stdout = sys.stdout
        self.stdout = StringIO.StringIO()
        sys.stdout = self.stdout

        self.__stderr = sys.stderr
        self.stderr = StringIO.StringIO()
        sys.stderr = self.stderr

        self.__import = __builtin__.__import__

    def tearDown(self):
        __builtin__.__import__ = self.__import
        sys.stderr = self.__stderr
        sys.stdout = self.__stdout

        log.set_threshold(self.__threshold)

        super(TestCoverage, self).tearDown()

    def __no_coverage_import(self, name, *args):
        if name == 'coverage':
            raise ImportError('test')

        return self.__import(name, *args)

    def __mock_coverage_import(self, name, *args):
        if name == 'coverage':
            return _MockCoverageModule(self.__coverage)

        return self.__import(name, *args)

    def test_creation_disabled(self):
        __builtin__.__import__ = self.__no_coverage_import

        coverage = Coverage(True, '', _MockDistribution())
        self.assertTrue(isinstance(coverage, Coverage))
        self.assertEqual(self.stderr.getvalue(), '')

    def test_creation_no_coverage(self):
        __builtin__.__import__ = self.__no_coverage_import

        coverage = Coverage(False, '', _MockDistribution())
        self.assertTrue(isinstance(coverage, Coverage))
        self.assertEqual(self.stderr.getvalue(),
                         _NO_COVERAGE_PACKAGE_WARNING % 'test' + '\n')

    def test_creation(self):
        self.__coverage = _MockCoverage()
        __builtin__.__import__ = self.__mock_coverage_import

        coverage = Coverage(False, 'test',
                            _MockDistribution(['xxx', 'yyy', 'zzz'],
                                              ['xxx', 'xxx.yyy', 'yyy']))
        self.assertTrue(isinstance(coverage, Coverage))
        self.assertEqual(self.__coverage.creations,
                         [((), {'source': [os.path.join('test', 'xxx.py'),
                                           os.path.join('test', 'yyy.py'),
                                           os.path.join('test', 'zzz.py'),
                                           os.path.join('test', 'xxx'),
                                           os.path.join('test', 'yyy')]})])

    def test_context(self):
        self.__coverage = _MockCoverage()
        __builtin__.__import__ = self.__mock_coverage_import

        first_path = sys.path[0]
        test_path = os.path.join(first_path, 'test')
        coverage = Coverage(False, test_path, _MockDistribution(['xxx']))

        self.assertEqual(self.__coverage.starts, 0)
        self.assertEqual(self.__coverage.stops, 0)

        with coverage:
            self.assertEqual(sys.path[0], test_path)
            self.assertEqual(self.__coverage.starts, 1)
            self.assertEqual(self.__coverage.stops, 0)

        self.assertEqual(sys.path[0], first_path)
        self.assertEqual(self.__coverage.starts, 1)
        self.assertEqual(self.__coverage.stops, 1)

    def test_report(self):
        self.__coverage = _MockCoverage()
        __builtin__.__import__ = self.__mock_coverage_import

        coverage = Coverage(False, 'test', _MockDistribution(['xxx']))
        coverage.report()
        self.assertEqual(self.stdout.getvalue(),
                         '\nCoverage report:\n\tThe report\n')

    def test_report_coverage_disabled(self):
        coverage = Coverage(True, '', _MockDistribution())
        coverage.report()
        self.assertEqual(self.stdout.getvalue(), '')

if __name__ == '__main__':
    unittest.main()

