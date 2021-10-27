# Default settings
#
# This file is read before all other configuration sources
#

import os

# get path from the masterkey is located 
MASTER_PRIVATE_KEY_PATH = os.environ.get("COESRA_PRIVATE_KEY_PATH_ENV") 
MASTER_KEY_PASSPHRASE = os.environ.get("MASTER_KEY_PASSPHRASE_ENV", "") 