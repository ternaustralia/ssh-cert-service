FLASK_APP=ssh_cert_service
FLASK_ENV=development

SSH_CERT_SERVICE_SETTINGS=development.cfg

# TODO: move this into development.cfg?
#       it's secrets ... would be much better to fake it away somehow
SSH_CERT_SERVICE_OIDC_DISCOVERY_URL=
SSH_CERT_SERVICE_OIDC_CLIENT_ID=
SSH_CERT_SERVICE_OIDC_CLIENT_SECRET=
SSH_CERT_SERVICE_OIDC_USE_REFRESH_TOKEN=