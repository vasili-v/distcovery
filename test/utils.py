import os
import errno
import sys

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

        self.expected_content = {'first': 'test_first',
                                 'second': 'test_second',
                                 'sub_first': 'test_sub_first',
                                 'sub_first.sub_first': \
                                     'test_sub_first.test_sub_first',
                                 'sub_third': 'test_sub_third',
                                 'sub_third.sub_first': \
                                     'test_sub_third.test_sub_first',
                                 'sub_third.sub_second': \
                                     'test_sub_third.test_sub_second',
                                 'sub_third.sub_second.sub_first': \
                                     'test_sub_third.test_sub_second.' \
                                     'test_sub_first'}

class ImportTrash(object):
    def setUp(self):
        self.modules_trash = []
        self.meta_path_trash = []

    def tearDown(self):
        for item in self.meta_path_trash:
            if item in sys.meta_path:
                sys.meta_path.remove(item)

        for name in self.modules_trash:
            if name in sys.modules:
                del sys.modules[name]

