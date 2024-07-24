import os

dir_path = os.path.dirname(os.path.realpath(__file__))

# Read version
version_globals = {}
with open(os.path.join(dir_path, "nttt", "_version.py")) as fp:
    exec(fp.read(), version_globals)

__project__ = 'nttt'
__desc__ = 'A utility for Nina to clean up translated projects'
__version__ = version_globals['__version__']

print('Tool: {}'.format(__project__))
print('Description: {}'.format(__desc__))
print('Version: {}'.format(__version__))

import nttt
nttt.main()
