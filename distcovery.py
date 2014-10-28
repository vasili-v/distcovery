import os
import re

from distutils.cmd import Command

_TEST_PACKAGE_NAME_REGEX = re.compile('^(test_([a-zA-Z0-9_]+))$')
_TEST_MODULE_NAME_REGEX = re.compile('^(test_([a-zA-Z0-9_]+))\\.py$')

class Test(Command):
    def collect_modules(self):
        def import_string(sequence):
            return '.'.join(sequence)

        def sub_item(alias, package, match):
            return (alias + (match.group(2),), package + (match.group(1),))

        def walk(path, alias, package):
            if not os.path.isfile(os.path.join(path, '__init__.py')):
                return

            for name in os.listdir(path):
                sub_path = os.path.join(path, name)

                match = _TEST_PACKAGE_NAME_REGEX.match(name)
                if match:
                    if os.path.isdir(sub_path):
                        sub_alias, sub_package = sub_item(alias, package, match)
                        for module in walk(sub_path, sub_alias, sub_package):
                            yield module

                else:
                    match = _TEST_MODULE_NAME_REGEX.match(name)
                    if match and os.path.isfile(sub_path):
                        yield sub_item(alias, package, match)

        modules = []
        for alias, module in walk(self.test_root, tuple(), tuple()):
            modules.append((import_string(alias), import_string(module)))

        self.test_modules = dict(modules)

    def initialize_options(self):
        pass

