import unittest

# Reload module to run its global section under coverage supervision
import distcovery.exceptions
reload(distcovery.exceptions)

from distcovery.exceptions import DistcoveryException, InvalidTestRoot, \
                                  NoTestModulesException, \
                                  UnknownModulesException

class TestDistcoveryException(unittest.TestCase):
    def test_raise(self):
        with self.assertRaises(AttributeError):
            raise DistcoveryException()

    def test_inheritance(self):
        class TestException(DistcoveryException):
            template = '%(xxx)s %(yyy)s %(zzz)s'

        with self.assertRaises(TestException) as ctx:
            raise TestException(xxx='xxx', yyy='yyy', zzz='zzz')

        self.assertEqual(ctx.exception.message, 'xxx yyy zzz')

class TestInvalidTestRoot(unittest.TestCase):
    def test_raise(self):
        with self.assertRaises(InvalidTestRoot) as ctx:
            raise InvalidTestRoot('path1', 'path2')

        self.assertEqual(ctx.exception.message,
                         InvalidTestRoot.template % {'tests': 'path1',
                                                     'current': 'path2'})

class TestNoTestModulesException(unittest.TestCase):
    def test_raise(self):
        with self.assertRaises(NoTestModulesException) as ctx:
            raise NoTestModulesException('path')

        self.assertEqual(ctx.exception.message,
                         NoTestModulesException.template % {'path': 'path'})

class TestUnknownModulesException(unittest.TestCase):
    def test_raise(self):
        modules = ['xxx', 'yyy', 'zzz']
        with self.assertRaises(UnknownModulesException) as ctx:
            raise UnknownModulesException(modules)

        modules, suffix = UnknownModulesException.stringify_list(modules)
        self.assertEqual(ctx.exception.message,
                         UnknownModulesException.template % \
                         {'modules': modules, 'suffix': suffix})

    def test_stringify_list_single_module(self):
        self.assertEqual(UnknownModulesException.stringify_list(['xxx']),
                         ('"xxx"', ''))

    def test_stringify_list_muliple_modules(self):
        self.assertEqual(UnknownModulesException. \
                             stringify_list(['xxx', 'yyy', 'zzz']),
                         ('"xxx", "yyy" and "zzz"', 's'))

if __name__ == '__main__':
    unittest.main()

