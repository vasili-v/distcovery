import unittest
import sys

from distutils import log
from distutils.cmd import Command

from distcovery.exceptions import NoTestModulesException, \
                                  UnknownModulesException
from distcovery.path import walk
from distcovery.coverage_wrapper import Coverage

class Test(Command):
    description = 'run tests for the package'

    user_options = [('module=', 'm', 'set of test modules to run (several ' \
                                     'modules can be listed using comma)'),
                    ('coverage-base=', None, 'base installation directory'),
                    ('coverage', 'c', 'calculate test coverage')]

    boolean_options = ['coverage']

    def collect_tests(self):
        self.test_package = walk(self.test_root)

    def initialize_options(self):
        self.module = None
        self.coverage_base = None
        self.coverage = None
        self.test_root = 'test'

    def finalize_options(self):
        self.set_undefined_options('install',
                                   ('install_purelib', 'coverage_base'))

    def print_test_package(self):
        log.info('Test suites:')
        for is_package, level, alias in self.test_package.enumerate(1):
            log.info('%s%s%s', level*'\t', alias, ':' if is_package else '')

    def validate_modules(self, modules):
        if not self.test_package.content:
            raise NoTestModulesException(self.test_root)

        modules = set(modules) - set(self.test_package.content.keys())
        if modules:
            raise UnknownModulesException(list(modules))

    def run(self):
        self.collect_tests()
        if not self.module:
            self.print_test_package()
            return

        modules = [item.strip() for item in self.module.split(',')]
        self.validate_modules(modules)

        coverage = Coverage(self.coverage, self.coverage_base, self.distribution)

        for module in modules:
            with coverage:
                unittest.main(self.test_package.content[module].str_name(),
                              argv=sys.argv[:1], exit=False,
                              verbosity=self.verbose)

        coverage.report()

