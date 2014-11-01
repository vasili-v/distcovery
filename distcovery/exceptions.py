class DistcoveryException(Exception):
    def __init__(self, **kwargs):
        super(DistcoveryException, self). \
            __init__(self.template % kwargs)

class InvalidTestRoot(DistcoveryException):
    template = 'Can\'t run tests outside current directory. ' \
               'Tests directory: "%(tests)s". Current directory: "%(current)s".'

    def __init__(self, tests, current):
        super(InvalidTestRoot, self). \
            __init__(tests=tests, current=current)

class NoTestModulesException(DistcoveryException):
    template = 'Couldn\'t find any test module. Make sure that path ' \
               '"%(path)s" contains any valid python module named ' \
               '"test_*.py" or package "test_*".'

    def __init__(self, path):
        super(NoTestModulesException, self). \
            __init__(path=path)

class UnknownModulesException(DistcoveryException):
    template = 'Unknown module%(suffix)s: %(modules)s.'

    def __init__(self, modules):
        modules, suffix = self.stringify_list(modules)
        super(UnknownModulesException, self). \
            __init__(modules=modules, suffix=suffix)

    @staticmethod
    def stringify_list(items):
        last = '"%s"' % items[-1]

        if len(items) > 1:
            return '"%s" and %s' % ('", "'.join(items[:-1]), last), 's'

        return last, ''

