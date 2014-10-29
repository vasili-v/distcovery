import os
import re
import itertools

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

def _sub_item(match, alias, package):
    return alias + (match.group(_TEST_ALIAS),), \
           package + (match.group(_TEST_NAME),)

def _is_package(path):
    return os.path.isdir(path) and \
           os.path.isfile(os.path.join(path, '__init__.py'))

def _is_module(path):
    return os.path.isfile(path)

def _listdir(path):
    def expand(name):
        return os.path.join(path, name), name

    return itertools.imap(expand, os.listdir(path))

def _walk_path(path, alias, package):
    for sub_path, name in _listdir(path):
        match = _TEST_PACKAGE_COMPILED_REGEX.match(name)
        if match:
            if _is_package(sub_path):
                sub_alias, sub_package = _sub_item(match, alias, package)
                for module in _walk_path(sub_path, sub_alias, sub_package):
                    yield module

        else:
             match = _TEST_MODULE_COMPILED_REGEX.match(name)
             if match and _is_module(sub_path):
                 sub_alias, sub_package = _sub_item(match, alias, package)
                 yield _make_name(sub_alias), _make_name(sub_package)

def _walk(path):
    return dict(_walk_path(path, tuple(), tuple()))

class Test(Command):
    def collect_modules(self):
        self.test_modules = _walk(self.test_root)

    def initialize_options(self):
        pass

