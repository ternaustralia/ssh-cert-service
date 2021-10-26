import os
# get path from the masterkey is located 
MASTER_PRIVATE_KEY_PATH = os.environ.get("COESRA_PRIVATE_KEY_PATH") 
MASTER_KEY_PASSPHRASE = os.environ.get("MASTER_KEY_PASSPHRASE_ENV", "") 