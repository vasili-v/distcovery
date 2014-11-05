import os
import sys

from distutils.core import setup

def get_test_command_class():
    ''' Import installed distcovery package instead of using it from its source
        location
    '''

    first_path = sys.path[0]
    is_first_path_cwd = os.path.abspath(first_path) == os.path.abspath('.')
    if is_first_path_cwd:
        del sys.path[0]

    try:
        from distcovery.test import Test
    except ImportError:
        from distutils import log
        from distutils.cmd import Command

        class Test(Command):
            description = 'run tests for the package when the package has ' \
                          'been installed'
            user_options = []

            def initialize_options(self):
                pass

            def finalize_options(self):
                pass

            def run(self):
                log.warn('Install the package to run tests')

    finally:
        if is_first_path_cwd:
            sys.path.insert(0, first_path)

    return Test

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
      packages=['distcovery'],
      license='MIT',
      platforms=('Linux', 'Darwin'),
      cmdclass={'test': get_test_command_class()})

