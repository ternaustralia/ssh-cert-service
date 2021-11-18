import os
import re
import subprocess
import tempfile
from typing import Any, Dict


class SSHKeygen:
    SSH_NAME = "python_key"

    def __init__(self, ca_key: str, ca_pass: str) -> None:
        """Instance variables

        ca_key: string
            path to ca private key

        ca_pass: string
            passphrase for ca private key

        comment : string
            Comment for the private key to be generated
        """
        self.ca_key = ca_key
        self.ca_pass = ca_pass

    def gen_key(
        self,
        passphrase: str = "",
        identity: str = "",
        validity: str = "",
        principals: str = "",
        comment: str = "",
    ) -> tuple:
        """Generate a SSH Key
        Parameters
        ----------
        passphrase : string
            password that will be used to encrypt private key
        indentity : string
            String that helps to identify the signed key
        validity : string
            Expiration time for the signed key format -1d:+3w (before, after)
        principals : string
            The user principals that will be allowed the signed key
        comment : string
            Comment for the private key to be generated
        Returns
        ----------
        tuple
        """

        if not self.ca_key:
            raise Exception(
                "Error!! The ca_private key is required to be able to sign certificates, please check with the admin."
            )

        # Create temporary dicrectory and storage the keys there
        with tempfile.TemporaryDirectory() as tmp_dir:
            keys_path = f"{tmp_dir}/{self.SSH_NAME}"
            # Genarate private and public key
            subprocess.run(
                ("ssh-keygen", "-t", "rsa", "-C", comment, "-N", passphrase, "-f", keys_path),
                capture_output=True,
                check=True,
            )

            # Sign key
            self.sign_key(f"{keys_path}.pub", identity, validity, principals)
            # Read files into binary variables
            loaded_keys = self.load_keys(keys_path)
            # Delete tmp directory

        return loaded_keys

    def load_keys(self, path: str) -> tuple:
        """Load all generated keys
        Parameters
        ----------
        path : string
            Abosluted path where all keys are located
        Returns
        ----------
        tuple
        """

        # Private key is necessary just when it generates new keys but it is not when needs just to sign CA
        private = ""
        if os.path.exists(path):
            with open(path, "r") as f:
                private = f.read()

        # Public and CA alway are required if there are not files it fails
        with open(f"{path}.pub", "r") as f:
            public = f.read()
        with open(f"{path}-cert.pub", "r") as f:
            cert = f.read()

        return private, public, cert

    def sign_key(
        self,
        public_path: str,
        identity: str = "",
        validity: str = "-1d:+1d",
        principals: str = "",
    ):
        """Generate signed certificate
        Parameters
        ----------
        public_path : string
            Path to public key which needs to be signed
        indentity : string
            String the helps to identify the signed key (this appears in sshd logs)
        validity : string
            Expiration time for the signed key format -1d:+3w (before:after)
        principals : string
            The principals that will be assigned to this key

        TODO: might be interesting to support for `-O` when signing ssh keys (e.g. agent/port/X11 forwarding, source-address-list etc....)

        Returns
        -------
        bool
        """
        if not public_path:
            raise Exception("Public key cannot be empty")

        cmd = ["ssh-keygen", "-s", self.ca_key, "-P", self.ca_pass]

        if identity:
            cmd.append("-I")
            cmd.append(identity)
        else:
            cmd.append("-I")
            cmd.append("")

        if validity:
            cmd.append("-V")
            cmd.append(validity)
        if principals:
            cmd.append("-n")
            cmd.append(principals)
        cmd.append(public_path)

        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    def verify_signature(self, public: str) -> bool:
        """Read public key and signed key to verified signature
        Parameters
        ----------
        public : bytes
           Public key to verify (must match the certificate)
        cert : bytes
           Certificate to verify (must match public key and CA)
        Returns
        -------
        bool
        """

        if not public:
            raise Exception("The public and signature are required to verify the data")

        # get hash four our ca key
        ca_output = subprocess.run(("ssh-keygen", "-l", "-f", self.ca_key), capture_output=True)
        pattern_public = r"(\S+:\S+)"
        p_result = re.search(pattern_public, ca_output.stdout.decode(), re.IGNORECASE)
        ca_match = p_result.group(1) if p_result else None

        cert_data = self.get_certificate_data(public)
        # The cert needs to match the public key and also our CA key

        return cert_data.get("signing_ca") == ca_match

    def get_certificate_data(self, cert_key: str) -> Dict[str, Any]:
        cert = ""

        if not cert_key:
            raise Exception("To be able to load the certifiacate data is necessary the cert decode.")

        with tempfile.TemporaryDirectory() as tmp_dir:
            keys_path = f"{tmp_dir}/{self.SSH_NAME}"
            cert_path = f"{keys_path}-cert.pub"
            tmp_cert = open(os.open(cert_path, os.O_CREAT | os.O_WRONLY, mode=0o600), "w")
            tmp_cert.write(cert_key)
            tmp_cert.close()
            if os.path.exists(cert_path):
                cert_output = subprocess.run(("ssh-keygen", "-L", "-f", cert_path), capture_output=True, check=True)
                cert = cert_output.stdout.decode()

        if not cert:
            raise Exception("Imposible to verified the certificate key.")

        cert_data = dict()

        # Type: <key type> <user|host> certificate
        data_type = r"Type: (.+) (.+) certificate"
        result = re.search(data_type, cert, re.IGNORECASE)
        cert_data["type"] = result.group(1) if result else None

        # Public key: <algo> <hash>
        public_key = r"public\skey:\srsa-cert\s(\S+)"
        result = re.search(public_key, cert, re.IGNORECASE)
        cert_data["public_key"] = result.group(1) if result else None

        # Signing CA: <algo> <hash>
        signing_ca = r"signing\sCA:\srsa\s(\S+)"
        result = re.search(signing_ca, cert, re.IGNORECASE)
        cert_data["signing_ca"] = result.group(1) if result else None

        # Key ID: "<keyid>"
        key_id = r'Key ID: "(.*)"'
        result = re.search(key_id, cert, re.IGNORECASE)
        cert_data["key_id"] = result.group(1) if result else None

        # Serial: <num>
        serial = r"Serial: (\d+)"
        result = re.search(serial, cert, re.IGNORECASE)
        cert_data["serial"] = result.group(1) if result else None

        # Valid: from <iso8601> to <iso8601>
        valid = r"Valid: (from [0-9T:-]+ to [0-9T:-]+)"
        result = re.search(valid, cert, re.IGNORECASE)
        cert_data["valid"] = result.group(1) if result else None

        # Principals:
        #         <principal 1>
        #         .....
        # FIXME: this currently matches only a single line
        principals = r"Principals:[^\n]+\s+([a-z-_]+(?:\n\s+))+"
        result = re.search(principals, cert, re.IGNORECASE)
        cert_data["principals"] = result.group(1).strip() if result else tuple()
        # cert_data["principals"] = tuple()

        cert_data["critical"] = None

        cert_data["extensions"] = None
        return cert_data
