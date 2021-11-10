# Default settings
#
# This file is read before all other configuration sources
#

# Set some defaults
# When deployed, these values must be configured
USER_CA_NAME = "SSH CA"
# TODO: when the app starts up, it should probably verify these settings, and fail fast
#       without CA_KEY, and CA_PASS the app is useless
# USER_CA_KEY = None
# USER_CA_PASS = None
SSH_PRINCIPAL_CLAIM = "preferred_username"
