import subprocess
import tempfile
from pathlib import Path

from ssh_cert_service.utils.ssh_keygen import SSHKeygen

COMMENT = "testing ssh key generation"
PASSPHRASE = ""
INDENTITY = "TESTING"
DOMAIN = "testing.com.au"
VALIDITY = "-1:+1d"
PRINCIPALS = "testing_user"
SSH_NAME = "python_key"


def test_gen_key(ca_key, ca_pass):
    """Test ssh-key generation"""
    ssh = SSHKeygen(ca_key, ca_pass)
    private_key, public_key, cert_key = ssh.gen_key(
        PASSPHRASE,
        INDENTITY,
        DOMAIN,
        VALIDITY,
        PRINCIPALS,
        COMMENT,
    )

    assert isinstance(private_key, str)
    assert isinstance(public_key, str)
    assert isinstance(cert_key, str)


def test_sign_key(ca_key, ca_pass):
    """Signing certificate"""
    ssh = SSHKeygen(ca_key, ca_pass)
    # Create temporary dicrectory and storage the keys there
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Check if Directory was create
        assert Path(tmp_dir).exists()

        keys_path = f"{tmp_dir}/{SSH_NAME}"
        # Genarate private and public key
        subprocess.run(
            ("ssh-keygen", "-t", "rsa", "-C", COMMENT, "-N", PASSPHRASE, "-f", keys_path),
            capture_output=True,
            check=True,
        )
        # Sign key
        ssh.sign_key(f"{keys_path}.pub", INDENTITY, DOMAIN, VALIDITY, PRINCIPALS)
        # Read files into binary variables
        private_key, public_key, cert_key = ssh.load_keys(keys_path)
        # Delete tmp directory

    assert isinstance(cert_key, str)


def test_load_keys(ca_key, ca_pass):
    """Load ssh_keys from a file"""
    ssh = SSHKeygen(ca_key, ca_pass)
    dir = ""
    # Create temporary dicrectory and storage the keys there
    with tempfile.TemporaryDirectory() as tmp_dir:
        keys_path = f"{tmp_dir}/{SSH_NAME}"
        # Genarate private and public key
        subprocess.run(
            ("ssh-keygen", "-t", "rsa", "-C", COMMENT, "-N", PASSPHRASE, "-f", keys_path),
            capture_output=True,
            check=True,
        )
        # Sign key
        ssh.sign_key(f"{keys_path}.pub", INDENTITY, DOMAIN, VALIDITY, PRINCIPALS)
        # Read files into binary variables
        loaded_keys = ssh.load_keys(keys_path)
        # Delete tmp directory
        dir = keys_path

    # Check if Directory was removed
    assert not Path(dir).exists()
    # Check if keys where loaded
    private_key, public_key, cert_key = loaded_keys
    assert isinstance(private_key, str)
    assert isinstance(public_key, str)
    assert isinstance(cert_key, str)


def test_verify_signature(ca_key, ca_pass):
    """Veify the signature of the cert with the public key"""
    ssh = SSHKeygen(ca_key, ca_pass)
    # Create temporary dicrectory and storage the keys there
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Check if Directory was create
        assert Path(tmp_dir).exists()

        keys_path = f"{tmp_dir}/{SSH_NAME}"
        # Genarate private and public key
        subprocess.run(
            ("ssh-keygen", "-t", "rsa", "-C", COMMENT, "-N", PASSPHRASE, "-f", keys_path),
            capture_output=True,
            check=True,
        )
        # Sign key
        ssh.sign_key(f"{keys_path}.pub", INDENTITY, DOMAIN, VALIDITY, PRINCIPALS)
        # Read files into binary variables
        private_key, public_key, cert_key = ssh.load_keys(keys_path)
        # Delete tmp directory

    is_signed = ssh.verify_signature(cert_key)
    assert is_signed


def test_get_certificate_data(ca_key, ca_pass):
    """Check if is possible to get the data from the certificate"""
    ssh = SSHKeygen(ca_key, ca_pass)
    # Create temporary dicrectory and storage the keys there
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Check if Directory was create
        assert Path(tmp_dir).exists()

        keys_path = f"{tmp_dir}/{SSH_NAME}"
        # Genarate private and public key
        subprocess.run(
            ("ssh-keygen", "-t", "rsa", "-C", COMMENT, "-N", PASSPHRASE, "-f", keys_path),
            capture_output=True,
            check=True,
        )
        # Sign key
        ssh.sign_key(f"{keys_path}.pub", INDENTITY, DOMAIN, VALIDITY, PRINCIPALS)
        # Read files into binary variables
        private_key, public_key, cert_key = ssh.load_keys(keys_path)
        # Delete tmp directory

    cert = ssh.get_certificate_data(cert_key)
    assert isinstance(cert, dict)
    assert cert.get("signing_ca") is not None
