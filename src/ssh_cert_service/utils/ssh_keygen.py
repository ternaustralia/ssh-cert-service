import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict


class SSHKeygen:
    SSH_NAME = "python_key"

    def __init__(self, comment) -> None:
        """Instance variables

        comment : string
            Comment for the private key to be generated
        """
        self.comment = comment

    def gen_key(
        self, passphrase: str = "", identity: str = "", domain: str = "", validity: str = "", principals: str = ""
    ) -> tuple:
        """Generate a SSH Key
        Parameters
        ----------
        comment : string
            Comment for the private key to be generated
        passphrase : string
            password that will be added to the public key
        indentity : string
            String the helps to identified the signed key
        domain : string
            String that will be allowed the signed key
        validity : string
            Expiration time for the signed key format -1d:+3w
        principals : string
            The user principals that will be allowed the signed key
        Returns
        ----------
        tuple
        """

        # Create temporary dicrectory and storage the keys there
        with tempfile.TemporaryDirectory() as tmp_dir:
            keys_path = f"{tmp_dir}/{self.SSH_NAME}"
            # Genarate private and public key
            subprocess.run(
                ("ssh-keygen", "-t", "rsa", "-C", self.comment, "-N", passphrase, "-f", keys_path),
                capture_output=True,
            )
            # Sign key
            self.sign_key(keys_path, f"{keys_path}.pub", identity, domain, validity, principals)
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

        with open(path, "r") as f:
            private = f.read()
        with open(f"{path}.pub", "r") as f:
            public = f.read()
        with open(f"{path}-cert.pub", "r") as f:
            cert = f.read()

        return private, public, cert

    def sign_key(
        self,
        private_path: str,
        public_path: str,
        identity: str = "",
        domain: str = "",
        validity: str = "-1d:+3w",
        principals: str = "",
    ):
        """Generate signed certificate
        Parameters
        ----------
        private_path : string
            Absoluted Path where the private key is located
        public : string
            Absoluted Path where the public key is located
        indentity : string
            String the helps to identified the signed key
        domain : string
            String that will be allowed the signed key
        validity : string
            Expiration time for the signed key format -1d:+3w
        principals : string
            The user principals that will be allowed the signed key
        Returns
        -------
        bool
        """
        if not private_path or not public_path:
            raise Exception("Public or private key cannot be empty")

        cmd = ["ssh-keygen", "-s", private_path, "-h"]

        if identity:
            cmd.append("-I")
            cmd.append(identity)
        else:
            cmd.append("-I")
            cmd.append("")

        if domain:
            cmd.append("-Z")
            cmd.append(domain)
        if validity:
            cmd.append("-V")
            cmd.append(validity)
        if principals:
            cmd.append("-n")
            cmd.append(principals)
        cmd.append(public_path)

        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def verify_signature(self, public: str, cert: str) -> bool:
        """Read public key and signed key to verified signature
        Parameters
        ----------
        public : bytes
           This is public generated previously
        cert : bytes
           This is the signature generated previously
        Returns
        -------
        bool
        """

        if not public or not cert:
            raise Exception("The public and signature are required to verify the data")

        with tempfile.TemporaryDirectory() as tmp_dir:
            keys_path = f"{tmp_dir}/{self.SSH_NAME}"
            tmp_public = open(f"{keys_path}.pub", "w")
            tmp_public.write(public)
            tmp_public.close()

            if os.path.exists(tmp_public.name):
                public_output = subprocess.run(("ssh-keygen", "-l", "-f", tmp_public.name), capture_output=True)
                pattern_public = f"(sha256\:.+)\s{self.comment}"
                p_result = re.search(pattern_public, public_output.stdout.decode(), re.IGNORECASE)
                public_match = p_result.groups(0)[0] if p_result else None

        cert_data = self.get_certificate_data(cert)
        return cert_data.get("signing_ca") == public_match

    def get_certificate_data(self, cert_key: str) -> Dict[str, Any]:
        cert = ""

        if not cert_key:
            raise Exception("To be able to load the certifiacate data is necessary the cert decode.")

        with tempfile.TemporaryDirectory() as tmp_dir:
            keys_path = f"{tmp_dir}/{self.SSH_NAME}"
            tmp_cert = open(f"{keys_path}-cert.pub", "w")
            tmp_cert.write(cert_key)
            tmp_cert.close()

            if os.path.exists(tmp_cert.name):
                cert_output = subprocess.run(("ssh-keygen", "-L", "-f", tmp_cert.name), capture_output=True)
                cert = cert_output.stdout.decode()

        if not cert:
            raise Exception("Imposible to verified the certificate key.")

        cert_data = dict()

        data_type = "Type\\:\\s(.+@.+)\\shost\\scertificate"
        result = re.search(data_type, cert, re.IGNORECASE)
        cert_data["type"] = result.groups(0)[0] if result else None

        public_key = "public\\skey\\:\\srsa-cert\\s(\\S+)"
        result = re.search(public_key, cert, re.IGNORECASE)
        cert_data["public_key"] = result.groups(0)[0] if result else None

        signing_ca = "signing\\sca\:\\sRSA\\s(\\S+)"
        result = re.search(signing_ca, cert, re.IGNORECASE)
        cert_data["signing_ca"] = result.groups(0)[0] if result else None

        key_id = 'key\\sid\\:\\s"([a-z]+)"'
        result = re.search(key_id, cert, re.IGNORECASE)
        cert_data["key_id"] = result.groups(0)[0] if result else None

        serial = "serial\\:\\s(\\d+)"
        result = re.search(serial, cert, re.IGNORECASE)
        cert_data["serial"] = result.groups(0)[0] if result else None

        valid = "valid\\:\\s(from\\s[0-9t\\:-]+\\sto\\s[0-9t\\:-]+)"
        result = re.search(valid, cert, re.IGNORECASE)
        cert_data["valid"] = result.groups(0)[0] if result else None

        principals = "principals\\:[^\\n]+\\s+([a-z-_]+(?:\\n\\s+))+"
        result = re.search(principals, cert, re.IGNORECASE)
        cert_data["principals"] = result.groups() if result else tuple()

        cert_data["critical"] = None

        cert_data["extensions"] = None

        return cert_data
