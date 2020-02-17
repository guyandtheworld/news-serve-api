import os
from .common import *

# you need to set "myproject = 'prod'" as an environment variable
# in your OS (on which your website is hosted)
if os.environ['RUN_TYPE'] == 'prod':
   from .prod import *
else:
   from .dev import *
