"""
    Copyright 2023 University of Southampton
    Dr Philip Basford
    μ-VIS X-Ray Imaging Centre

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Override the production values here as needed for development
"""


import socket
import os
from .settings import BASE_DIR

LOG_DEBUG=False
PRODUCTION_SERVER = "xrh-server"
try:
    hostname = socket.gethostname()
except:
    hostname = "UNKNOWN"
DEV_SITE = (hostname != PRODUCTION_SERVER)
if DEV_SITE:
    print("*****USING DEVELOPMENT VERSION*****")
    URL_PREFIX = ""
    FORCE_SCRIPT_NAME = URL_PREFIX
    SESSION_COOKIE_PATH = "/"
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False

    ALLOWED_HOSTS = [
        "xrhms-dev.clients.soton.ac.uk",
        "xrhms-dev2.clients.soton.ac.uk",
        "xrh-testing-2.clients.soton.ac.uk",
        "xrh-testing3.clients.soton.ac.uk"]
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'my_log_handler': {
                'level': 'DEBUG' if LOG_DEBUG else 'INFO',
                'class': 'logging.FileHandler',
                'filename': os.path.join(BASE_DIR, 'django.log'),
            },
        },
        'loggers': {
            'django': {
                'handlers': ['my_log_handler'],
                'level': 'DEBUG' if LOG_DEBUG else 'INFO',
                'propagate': True,
            },
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
    }
else:
    PRIVATE_STORAGE_SERVER = 'apache'
