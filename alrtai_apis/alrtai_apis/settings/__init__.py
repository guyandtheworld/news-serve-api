import os
from .common import *

if os.environ['DJANGO_SETTINGS'] == 'prod':
   from .prod import *
else:
   from .dev import *
