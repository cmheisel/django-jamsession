from settings import *

INSTALLED_APPS += ('django_hudson', )

PROJECT_APPS = ('jamsession', )

HUDSON_TASKS = ('coverage', 'tests')

import logging
logging.basicConfig(level=logging.WARNING)
