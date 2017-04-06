# proxy class to import current scheme

import os
import importlib
try:
    version = os.environ['MODEL_VERSION']
except KeyError:
    version = '817'

exec "from .model%s import *" % version
