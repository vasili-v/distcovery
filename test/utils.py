import os
import errno

def mock_directory_tree(tree):
    tree = dict([(os.path.join(*key), value) \
                      for key, value in tree.iteritems()])

    def listdir(path):
        try:
            names = tree[path]
        except KeyError:
            raise OSError(errno.ENOENT, os.strerror(errno.ENOENT), path)

        if names is None:
            raise OSError(errno.ENOTDIR, os.strerror(errno.ENOTDIR), path)

        return names

    def isfile(path):
        try:
            item = tree[path]
        except KeyError:
            return False

        return item is None

    def isdir(path):
        try:
            item = tree[path]
        except KeyError:
            return False

        return item is not None

    return listdir, isfile, isdir

class PreserveOs(object):
    def setUp(self):
        super(PreserveOs, self).setUp()

        self.__listdir = os.listdir
        self.__isfile = os.path.isfile
        self.__isdir = os.path.isdir

    def tearDown(self):
        os.path.isdir = self.__isdir
        os.path.isfile = self.__isfile
        os.listdir = self.__listdir

        super(PreserveOs, self).tearDown()

    def full_test_tree(self):
        tree = {('.',): ('__init__.py', 'test_first.py', 'test_second.py',
                         'test_sub_first', 't_sub_first', 'test_sub_third'),
                ('.', '__init__.py'): None,
                ('.', 'test_first.py'): None,
                ('.', 'test_second.py'): None,
                ('.', 'test_sub_first'): ('__init__.py', 'test_sub_first.py'),
                ('.', 'test_sub_first', '__init__.py'): None,
                ('.', 'test_sub_first', 'test_sub_first.py'): None,
                ('.', 't_sub_first'): ('__init__.py', 'test_sub_first.py'),
                ('.', 't_sub_first', '__init__.py'): None,
                ('.', 't_sub_first', 'test_sub_first.py'): None,
                ('.', 'test_sub_second'): ('test_sub_first.py',),
                ('.', 'test_sub_second', 'test_sub_first.py'): None,
                ('.', 'test_sub_third'): ('__init__.py', 'test_sub_first.py',
                                          'test_sub_second'),
                ('.', 'test_sub_third', '__init__.py'): None,
                ('.', 'test_sub_third', 'test_sub_first.py'): None,
                ('.', 'test_sub_third', 'test_sub_second'): \
                    ('__init__.py', 'test_sub_first.py', 't_sub_second.py'),
                ('.', 'test_sub_third', 'test_sub_second', '__init__.py'): None,
                ('.', 'test_sub_third', 'test_sub_second',
                 'test_sub_first.py'): None,
                ('.', 'test_sub_third', 'test_sub_second',
                 't_sub_second.py'): None}

        os.listdir, os.path.isfile, os.path.isdir = mock_directory_tree(tree)

        self.expected_modules = (('first', 'test_first'),
                                 ('second', 'test_second'),
                                 ('sub_first.sub_first',
                                  'test_sub_first.test_sub_first'),
                                 ('sub_third.sub_first',
                                  'test_sub_third.test_sub_first'),
                                 ('sub_third.sub_second.sub_first',
                                  'test_sub_third.test_sub_second.' \
                                      'test_sub_first'))

