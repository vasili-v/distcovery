import random

from distcovery.exceptions import NoMoreAttempts

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

