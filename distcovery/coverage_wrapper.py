import collections
import os
import sys

from distutils import log

class _DummyCoverage(object):
    def __init__(self, *args, **kwargs):
        pass

    def start(self, *args, **kwargs):
        pass

    def stop(self, *args, **kwargs):
        pass

    def report(self, *args, **kwargs):
        pass

_NO_COVERAGE_PACKAGE_WARNING = 'Couldn\'t import coverage with error "%s". ' \
                               'Skipping coverage calculations...'

class Coverage(object):
    def __init__(self, disabled, path, distribution):
        if disabled:
            coverage = _DummyCoverage
        else:
            try:
                from coverage import coverage
            except ImportError as error:
                log.warn(_NO_COVERAGE_PACKAGE_WARNING, error)
                coverage = _DummyCoverage

        self.__path = path

        self.__available = coverage is not _DummyCoverage
        source = list(self.__get_source(distribution))
        self.__coverage = coverage(source=source)

    def __get_source(self, distribution):
        if not self.__available:
            return

        if isinstance(distribution.py_modules, collections.Iterable):
            for module in set(distribution.py_modules):
                yield os.path.join(self.__path, module + '.py')

        if isinstance(distribution.packages, collections.Iterable):
            packages = set()
            for package in distribution.packages:
                packages.add(package.split('.', 1)[0])

            for package in packages:
                yield os.path.join(self.__path, package)

    def __enter__(self):
        self.__coverage.start()
        sys.path.insert(0, self.__path)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if sys.path[0] == self.__path:
            del sys.path[0]

        self.__coverage.stop()

    def report(self):
        if self.__available:
            log.info('\nCoverage report:')

        self.__coverage.report()

