# -------------------------------------------------------------------------------
#
#  Copyright (c) FotoNation.
#  All rights reserved. Confidential.
#
# -------------------------------------------------------------------------------


import os
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


# This method sets up and configures Django. It's used by scripts that need to
# execute as if running in a Django server (the settings are those from setting.py)
def boot_django():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ProiectLicenta.settings")
    django.setup()
