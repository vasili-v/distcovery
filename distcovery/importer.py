import random
import sys
import imp

from distcovery.exceptions import NoMoreAttempts
from distcovery.path import Package

_MODULE_NAME_PREFIX = 'TestModule'
_IMPORT_MODULE_LINE = 'import %%s as %s%%d\n' % _MODULE_NAME_PREFIX

class RandomUniqueNames(object):
    def __init__(self, limit=10, length=15):
        self.__limit = int(limit) if limit > 1 else 1
        self.__length = int(length) if length > 1 else 1
        self.__factor = pow(10, self.__length)
        self.__format = 'X_%%0%dd' % self.__length
        self.__names = set()

    def random_name(self):
        return self.__format % int(random.random()*self.__factor)

    def new(self):
        limit = self.__limit
        name = self.random_name()
        while name in self.__names:
            limit -= 1
            if limit <= 0:
                raise NoMoreAttempts(self.__limit, self.__length)

            name = self.random_name()

        self.__names.add(name)
        return name

class Importer(object):
    def __init__(self, package):
        self.random_unique_names = RandomUniqueNames()

        self.aliases = {}
        self.sources = {}

        self.build_module('*', package)

    def build_module(self, alias, package):
        name = self.random_unique_names.new()

        self.aliases[alias] = name
        self.sources[name] = ''

        counter = 0
        for alias, importable in package.content.iteritems():
            if isinstance(importable, Package):
                self.build_module(alias, importable)
            else:
                counter += 1
                self.sources[name] += _IMPORT_MODULE_LINE % \
                                      (importable.str_name(), counter)

    def find_module(self, fullname, path=None):
        if fullname in self.sources:
            return self

    def load_module(self, fullname):
        if fullname in sys.modules:
            return sys.modules[fullname]

        module = imp.new_module(fullname)
        module.__file__ = '<test package>'
        module.__path__ = []
        module.__loader__ = self
        module.__package__ = fullname

        code = self.sources[fullname]

        sys.modules[fullname] = module
        try:
            exec(code, module.__dict__)
        except:
            del sys.modules[fullname]
            raise

        return module

