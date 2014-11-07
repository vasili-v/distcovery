import os
import re

from distcovery.exceptions import InvalidTestRoot

_TEST_UNIT_PREFIX = 'test_'
_PYTHON_TOKEN_REGEX = '([a-zA-Z0-9_]+)'
_TEST_PACKAGE_REGEX = '(%s%s)' % (_TEST_UNIT_PREFIX, _PYTHON_TOKEN_REGEX)
_TEST_MODULE_REGEX = '%s\\.py' % _TEST_PACKAGE_REGEX
_TEST_NAME = 1
_TEST_ALIAS = 2

_TEST_PACKAGE_PATTERN = re.compile('%s$' % _TEST_PACKAGE_REGEX)
_TEST_MODULE_PATTERN = re.compile('%s$' % _TEST_MODULE_REGEX)

def _is_package(path):
    return os.path.isdir(path) and \
           os.path.isfile(os.path.join(path, '__init__.py'))

def _is_module(path):
    return os.path.isfile(path)

class Importable(object):
    def __init__(self, base, path, match=None, parent=None):
        self.base = base
        self.path = path

        if match and parent:
            self.alias = parent.alias + (match.group(_TEST_ALIAS),)
            self.name = parent.name + (match.group(_TEST_NAME),)
        else:
            self.alias = tuple()
            self.name = tuple()

    @staticmethod
    def join_sequence(sequence):
        return '.'.join(sequence)

    def str_alias(self):
        return self.join_sequence(self.alias)

    def str_name(self):
        return self.join_sequence(self.base + self.name)

class Package(Importable):
    def __init__(self, base, path, match=None, parent=None):
        super(Package, self).__init__(base, path, match, parent)

        self.modules = []
        self.packages = []
        self.content = {}

    def listdir(self):
        for name in os.listdir(self.path):
            yield os.path.join(self.path, name), name

    def walk(self):
        for path, name in self.listdir():
            child = None

            match = _TEST_PACKAGE_PATTERN.match(name)
            if match:
                if _is_package(path):
                    child = Package(self.base, path, match, self)
                    for child_alias, child_iterable in child.walk():
                        self.content[child_alias] = child_iterable
                        yield child_alias, child_iterable

                    self.packages.append(child)
            else:
                match = _TEST_MODULE_PATTERN.match(name)
                if match and _is_module(path):
                    child = Importable(self.base, path, match, self)
                    self.modules.append(child)

            if child:
                child_alias = child.str_alias()

                self.content[child_alias] = child
                yield child_alias, child

    def enumerate(self, level=1):
        for module in self.modules:
            yield False, level, module.str_alias()

        for package in self.packages:
            yield True, level, package.str_alias()

            for item in package.enumerate(level + 1):
                yield item

def _split_path(path, root):
    head = path
    tail = tuple()
    while head != root:
        head, name = os.path.split(head)
        if not name:
            raise InvalidTestRoot(path, root)

        tail = (name,) + tail

    return tail

def walk(path):
    package = Package(_split_path(os.path.abspath(path), os.getcwd()), path)
    content = dict(package.walk())
    return package

