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

