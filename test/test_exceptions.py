import unittest

# Reload module to run its global section under coverage supervision
import distcovery.exceptions
reload(distcovery.exceptions)

from distcovery.exceptions import DistcoveryException, NoMoreAttempts, \
                                  InvalidTestRoot, NoTestModulesException, \
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

class TestNoMoreAttempts(unittest.TestCase):
    def test_raise_single_limit(self):
        with self.assertRaises(NoMoreAttempts) as ctx:
             raise NoMoreAttempts(1, 5)

        self.assertEqual(ctx.exception.message,
                         NoMoreAttempts.template % {'limit': 1,
                                                    'limit_suffix': '',
                                                    'length': 5,
                                                    'length_suffix': 's'})

    def test_raise_single_length(self):
        with self.assertRaises(NoMoreAttempts) as ctx:
             raise NoMoreAttempts(3, 1)

        self.assertEqual(ctx.exception.message,
                         NoMoreAttempts.template % {'limit': 3,
                                                    'limit_suffix': 's',
                                                    'length': 1,
                                                    'length_suffix': ''})

    def test_number_suffix_single(self):
        self.assertEqual(NoMoreAttempts.number_suffix(1), '')

    def test_number_suffix(self):
        self.assertEqual(NoMoreAttempts.number_suffix(2), 's')

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

