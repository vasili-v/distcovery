import unittest

# Reload module to run its global section under coverage supervision
import distcovery.exceptions
reload(distcovery.exceptions)

from distcovery.exceptions import DistcoveryException, NoMoreAttempts, \
                                  InvalidTestRoot, NoTestModulesException, \
                                  UnknownModulesException

class TestDistcoveryException(unittest.TestCase):
    def test_raise(self):
        def raiser():
            raise DistcoveryException()

        self.assertRaises(AttributeError, raiser)

    def test_inheritance(self):
        class TestException(DistcoveryException):
            template = '%(xxx)s %(yyy)s %(zzz)s'

        errors = []
        def raiser():
            try:
                raise TestException(xxx='xxx', yyy='yyy', zzz='zzz')
            except TestException as error:
                errors.append(error)
                raise

        self.assertRaises(TestException, raiser)
        self.assertEqual(str(errors[0]), 'xxx yyy zzz')

class TestNoMoreAttempts(unittest.TestCase):
    def test_raise_single_limit(self):
        errors = []
        def raiser():
            try:
                raise NoMoreAttempts(1, 5)
            except NoMoreAttempts as error:
                errors.append(error)
                raise

        self.assertRaises(NoMoreAttempts, raiser)
        self.assertEqual(str(errors[0]),
                         NoMoreAttempts.template % {'limit': 1,
                                                    'limit_suffix': '',
                                                    'length': 5,
                                                    'length_suffix': 's'})

    def test_raise_single_length(self):
        errors = []
        def raiser():
            try:
                raise NoMoreAttempts(3, 1)
            except NoMoreAttempts as error:
                errors.append(error)
                raise

        self.assertRaises(NoMoreAttempts, raiser)
        self.assertEqual(str(errors[0]),
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
        errors = []
        def raiser():
            try:
                raise InvalidTestRoot('path1', 'path2')
            except InvalidTestRoot as error:
                errors.append(error)
                raise

        self.assertRaises(InvalidTestRoot, raiser)
        self.assertEqual(str(errors[0]),
                         InvalidTestRoot.template % {'tests': 'path1',
                                                     'current': 'path2'})

class TestNoTestModulesException(unittest.TestCase):
    def test_raise(self):
        errors = []
        def raiser():
            try:
                raise NoTestModulesException('path')
            except NoTestModulesException as error:
                errors.append(error)
                raise

        self.assertRaises(NoTestModulesException, raiser)
        self.assertEqual(str(errors[0]),
                         NoTestModulesException.template % {'path': 'path'})

class TestUnknownModulesException(unittest.TestCase):
    def test_raise(self):
        modules = ['xxx', 'yyy', 'zzz']
        errors = []
        def raiser():
            try:
                raise UnknownModulesException(modules)
            except UnknownModulesException as error:
                errors.append(error)
                raise

        self.assertRaises(UnknownModulesException, raiser)
        modules, suffix = UnknownModulesException.stringify_list(modules)
        self.assertEqual(str(errors[0]),
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

