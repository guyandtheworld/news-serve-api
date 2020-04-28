import os
from .common import *  # noqa

if os.environ['DJANGO_SETTINGS'] == 'prod':
    from .prod import *  # noqa
else:
    from .dev import *  # noqa
