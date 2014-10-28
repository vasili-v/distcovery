import os
import re

from distutils.cmd import Command

_TEST_UNIT_PREFIX = 'test_'
_PYTHON_TOKEN_REGEX = '([a-zA-Z0-9_]+)'
_TEST_PACKAGE_REGEX = '(%s%s)' % (_TEST_UNIT_PREFIX, _PYTHON_TOKEN_REGEX)
_TEST_MODULE_REGEX = '%s\\.py' % _TEST_PACKAGE_REGEX
_TEST_NAME = 1
_TEST_ALIAS = 2

_TEST_PACKAGE_COMPILED_REGEX = re.compile('%s$' % _TEST_PACKAGE_REGEX)
_TEST_MODULE_COMPILED_REGEX = re.compile('%s$' % _TEST_MODULE_REGEX)

def _make_name(sequence):
    return '.'.join(sequence)

def _sub_item(alias, package, match):
    return alias + (match.group(_TEST_ALIAS),), \
           package + (match.group(_TEST_NAME),)

def _is_package(path):
    return os.path.isdir(path) and \
           os.path.isfile(os.path.join(path, '__init__.py'))

def _is_module(path):
    return os.path.isfile(path)

class Test(Command):
    def collect_modules(self):
        def walk(path, alias, package):
            for name in os.listdir(path):
                sub_path = os.path.join(path, name)

                match = _TEST_PACKAGE_COMPILED_REGEX.match(name)
                if match:
                    if _is_package(sub_path):
                        sub_alias, sub_package = _sub_item(alias, package, match)
                        for module in walk(sub_path, sub_alias, sub_package):
                            yield module

                else:
                    match = _TEST_MODULE_COMPILED_REGEX.match(name)
                    if match and _is_module(sub_path):
                        yield _sub_item(alias, package, match)

        modules = []
        for alias, module in walk(self.test_root, tuple(), tuple()):
            modules.append((_make_name(alias), _make_name(module)))

        self.test_modules = dict(modules)

    def initialize_options(self):
        pass

