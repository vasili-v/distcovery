import unittest
import sys

from distutils import log
from distutils.cmd import Command

from distcovery.exceptions import NoTestModulesException, \
                                  UnknownModulesException
from distcovery.path import walk
from distcovery.coverage_wrapper import Coverage
from distcovery.importer import Importer

class Test(Command):
    description = 'run tests for the package'

    user_options = [('module=', 'm', 'set of test modules to run (several ' \
                                     'modules can be listed using comma)'),
                    ('coverage-base=', None, 'base installation directory'),
                    ('coverage', 'c', 'calculate test coverage')]

    boolean_options = ['coverage']

    def collect_tests(self):
        self.test_package = walk(self.test_root)
        if not self.test_package.content:
            raise NoTestModulesException(self.test_root)

    def register_importer(self):
        self.importer = Importer(self.test_package)
        sys.meta_path.append(self.importer)

    def print_test_package(self):
        log.info('Test suites:')
        for is_package, level, alias in self.test_package.enumerate(1):
            log.info('%s%s%s', level*'\t', alias, ':' if is_package else '')

    def initialize_options(self):
        self.module = None
        self.coverage_base = None
        self.coverage = None
        self.test_root = 'test'

    def finalize_options(self):
        self.set_undefined_options('install',
                                   ('install_purelib', 'coverage_base'))

    def validate_modules(self, modules):
        modules = set(modules) - set(self.importer.aliases.keys() + \
                                     self.test_package.content.keys())
        if modules:
            raise UnknownModulesException(list(modules))

    def map_module(self, module):
        if module in self.importer.aliases:
            return self.importer.aliases[module]

        return self.test_package.content[module].str_name()

    def run(self):
        self.collect_tests()
        self.register_importer()

        if self.module:
            modules = [item.strip() for item in self.module.split(',')]
            self.validate_modules(modules)
        else:
            self.print_test_package()
            return

        coverage = Coverage(self.coverage, self.coverage_base,
                            self.distribution)

        for module in modules:
            module = self.map_module(module)

            with coverage:
                unittest.main(module, argv=sys.argv[:1], exit=False,
                              verbosity=self.verbose)

        coverage.report()

