from distutils.core import setup
from distcovery import Test

setup(name='Distcovery',
      version='0.0.1',
      description='Command "test" for distutils setup',
      long_description='The library provides command "test" for distutils ' \
                       'setup. The command allows to run tests ' \
                       'all together or individually and calculate ' \
                       'test coverage.',
      author='Vasili Vasilyeu',
      author_email='vasili.v@tut.by',
      url='https://github.com/vasili-v/distcovery',
      py_modules=['distcovery'],
      license='MIT',
      platforms=('Linux', 'Darwin'),
      cmdclass={'test': Test})

