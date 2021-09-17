import os
import random
import string
import shutil
import subprocess
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

class SSHKeygen:
    PRIV_SSH_DIR = '/tmp/'
    SSH_NAME = 'python_key'

    def gen_key(self,
        comment: str = '',
        passphrase: str = '',
        identity: str = '',
        domain: str = '',
        validity: str = '',
        principals: str = ''
        ) -> tuple:
        """ Generate a SSH Key
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

        directory = self.get_random_name()
        path = Path(f'{self.PRIV_SSH_DIR}/{directory}')

        if path.exists():
            shutil.rmtree(path)
        else:
            os.mkdir(path)

        keys_path = f'{path}/{self.SSH_NAME}'
        # Genarate private and public key
        subprocess.run(f'ssh-keygen -t rsa -C "{comment}" -N "{passphrase}" -f {keys_path}', shell=True)
        # Sign key
        self.sign_key(keys_path, f'{keys_path}.pub', identity, domain, validity, principals)
        # self.sign_key(keys_path, f'{keys_path}.pub', 'coesra', 'coesra.com.au', '-1d:+12w5d', 'jeff')
        # Ready files into binary variables
        loaded_keys = self.load_keys(keys_path)
        # Delete directory
        shutil.rmtree(path)
        return loaded_keys

    def load_keys(self, path: str) -> tuple:
        """ Load all generated keys
            Parameters
            ----------
            path : string
                Abosluted path where all keys are located
            Returns
            ----------
            tuple
        """
        file = Path(path)

        with open(path, 'rb') as f:
            private = f.read()
        with open(f'{path}.pub', 'rb') as f:
            public = f.read()
        with open(f'{path}-cert.pub', 'rb') as f:
            cert = f.read()

        print(type(cert))

        return private, public, cert

    def get_random_name(self, N: int = 10) -> str:
        """ Generate a random string of 10 uppercase characteres
            Parameters
            ----------
            N : integer
                Length of the string for the random folder
            Returns
            ----------
            string
        """
        chars = string.ascii_uppercase + string.digits 
        return ''.join(random.choice(chars) for _ in range(N))

    def sign_key(self,
        private_path: str,
        public_path: str,
        identity: str = '',
        domain: str = '',
        validity: str = '-1d:+3w',
        principals: str = ''
        ):
        """ Generate signed certificate
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
            raise Exception('Public or private key cannot be empty')

        if identity:
            identity = f'-I {identity}'
        else:
            identity = f'-I ""'

        if domain:
            domain = f'-Z {domain}'
        if validity:
            validity = f'-V {validity}'
        if principals:
            principals = f'-n {principals}'

        subprocess.run(f'ssh-keygen -s {private_path} {identity} -h {domain} {validity} {principals} {public_path}', shell=True)

    def verify_signature(self, public: str, cert: str) -> bool:
        """ Read public key and signed key to verified signature
            Parameters
            ----------
            public : string
               This is public generated previously
            cert : string
               This is the signature generated previously
            Returns
            -------
            bool
        """

        if not public or not cert:
            raise Exception("The public and signature are required to verify the data")

        public = public.encode('ascii') 
        cert = bytes(cert.encode('ascii'))

        public_key = serialization.load_ssh_public_key(
            public,
            backend=default_backend()
        )
        # with open(f'{path}.pub', 'rb') as f:
        #     public = serialization.load_ssh_public_key(
        #         f.read(),
        #         backend=default_backend()
        #     )
        # with open(f'{path}-cert.pub', 'rb') as f:
        #     # cert = serialization.load_ssh_public_key(
        #     #     f.read(),
        #     #     backend=default_backend()
        #     # )
        #     cert = f.read()

        print(public_key)
        public_key.verify(
            cert,
            "",
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
            )

        return True

