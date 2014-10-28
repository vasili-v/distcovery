import os
import re

from distutils.cmd import Command

_TEST_PACKAGE_NAME_REGEX = re.compile('^(test_([a-zA-Z0-9_]+))$')
_TEST_MODULE_NAME_REGEX = re.compile('^(test_([a-zA-Z0-9_]+))\\.py$')

def _make_name(sequence):
    return '.'.join(sequence)

def _sub_item(alias, package, match):
    return (alias + (match.group(2),), package + (match.group(1),))

class Test(Command):
    def collect_modules(self):
        def walk(path, alias, package):
            if not os.path.isfile(os.path.join(path, '__init__.py')):
                return

            for name in os.listdir(path):
                sub_path = os.path.join(path, name)

                match = _TEST_PACKAGE_NAME_REGEX.match(name)
                if match:
                    if os.path.isdir(sub_path):
                        sub_alias, sub_package = _sub_item(alias, package, match)
                        for module in walk(sub_path, sub_alias, sub_package):
                            yield module

                else:
                    match = _TEST_MODULE_NAME_REGEX.match(name)
                    if match and os.path.isfile(sub_path):
                        yield _sub_item(alias, package, match)

        modules = []
        for alias, module in walk(self.test_root, tuple(), tuple()):
            modules.append((_make_name(alias), _make_name(module)))

        self.test_modules = dict(modules)

    def initialize_options(self):
        pass

