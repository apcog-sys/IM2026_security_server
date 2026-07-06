"""
Certificate Generation Module

This module provides functions to generate RSA keys and Certificate Signing Requests (CSR)
for both digital signature and authentication purposes.

It creates:
- Public key (.key file)
- Private key (.key file)
- Certificate Signing Request (.csr file)
"""

import os
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
import cryptography.x509 as x509
from cryptography.hazmat.backends import default_backend
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CertificateGenerator:
    """Generate certificates and keys for digital signatures and authentication"""

    def __init__(self, output_dir: str = "certificates"):
        """
        Initialize the certificate generator
        
        Args:
            output_dir (str): Directory where certificates will be stored
        """
        self.output_dir = output_dir
        self.key_size = 2048
        self.public_exponent = 65537

        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"Created certificate directory: {output_dir}")

    def generate_rsa_keypair(self) -> tuple:
        """
        Generate an RSA key pair (public and private keys)
        
        Returns:
            tuple: (private_key, public_key)
        """
        logger.info(f"Generating {self.key_size}-bit RSA key pair...")
        
        private_key = rsa.generate_private_key(
            public_exponent=self.public_exponent,
            key_size=self.key_size,
            backend=default_backend()
        )
        
        public_key = private_key.public_key()
        logger.info("RSA key pair generated successfully")
        
        return private_key, public_key

    def create_certificate_signing_request(
        self,
        private_key,
        entity_code: str,
        entity_name: str,
        contact_person: str,
        email: str,
        phone: str,
        city: str,
        state: str,
        country: str
    ):
        """
        Create a Certificate Signing Request (CSR)
        
        Args:
            private_key: RSA private key object
            entity_code (str): Unique entity code
            entity_name (str): Organization name
            contact_person (str): Contact person name
            email (str): Email address
            phone (str): Phone number
            city (str): City name
            state (str): State/Province name
            country (str): Country code (e.g., 'US')
        
        Returns:
            CSR object
        """
        logger.info(f"Creating CSR for entity: {entity_code}")
        
        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, country),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state),
            x509.NameAttribute(NameOID.LOCALITY_NAME, city),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, entity_name),
            x509.NameAttribute(NameOID.COMMON_NAME, entity_code),
            x509.NameAttribute(NameOID.EMAIL_ADDRESS, email),
        ])

        # Add Subject Alternative Name (SAN) extension
        san_list = [
            x509.RFC822Name(email),
            x509.UniformResourceIdentifier(f"https://{entity_code.lower()}.local"),
        ]

        csr = x509.CertificateSigningRequestBuilder().subject_name(
            subject
        ).add_extension(
            x509.SubjectAlternativeName(san_list),
            critical=False,
        ).sign(private_key, hashes.SHA256(), default_backend())

        logger.info(f"CSR created successfully for entity: {entity_code}")
        return csr

    def save_private_key(self, private_key, filename: str, password: str = None) -> str:
        """
        Save private key to file
        
        Args:
            private_key: RSA private key object
            filename (str): Name of the output file
            password (str): Optional password to encrypt the private key
        
        Returns:
            str: Full path to saved file
        """
        filepath = os.path.join(self.output_dir, filename)
        
        if password:
            encryption = serialization.BestAvailableEncryption(password.encode())
        else:
            encryption = serialization.NoEncryption()

        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption
        )

        with open(filepath, "wb") as f:
            f.write(pem)
        
        os.chmod(filepath, 0o600)  # Restrict file permissions
        logger.info(f"Private key saved: {filepath}")
        return filepath

    def save_public_key(self, public_key, filename: str) -> str:
        """
        Save public key to file
        
        Args:
            public_key: RSA public key object
            filename (str): Name of the output file
        
        Returns:
            str: Full path to saved file
        """
        filepath = os.path.join(self.output_dir, filename)
        
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        with open(filepath, "wb") as f:
            f.write(pem)
        
        logger.info(f"Public key saved: {filepath}")
        return filepath

    def save_csr(self, csr, filename: str) -> str:
        """
        Save Certificate Signing Request to file
        
        Args:
            csr: CSR object
            filename (str): Name of the output file
        
        Returns:
            str: Full path to saved file
        """
        filepath = os.path.join(self.output_dir, filename)
        
        pem = csr.public_bytes(serialization.Encoding.PEM)

        with open(filepath, "wb") as f:
            f.write(pem)
        
        logger.info(f"CSR saved: {filepath}")
        return filepath

    def generate_certificates(
        self,
        cert_type: str,
        entity_code: str,
        entity_name: str,
        contact_person: str,
        email: str,
        phone: str,
        city: str,
        state: str,
        country: str,
        password: str = None
    ) -> dict:
        """
        Generate complete certificate package (keys + CSR)
        
        Args:
            cert_type (str): Type of certificate - 'signature' or 'auth'
            entity_code (str): Unique entity code
            entity_name (str): Organization name
            contact_person (str): Contact person name
            email (str): Email address
            phone (str): Phone number
            city (str): City name
            state (str): State/Province name
            country (str): Country code (2-letter code, e.g., 'US')
            password (str): Optional password to encrypt private key
        
        Returns:
            dict: Dictionary containing paths to generated files and metadata
        
        Raises:
            ValueError: If cert_type is not 'signature' or 'auth'
        """
        if cert_type.lower() not in ['signature', 'auth']:
            raise ValueError("cert_type must be either 'signature' or 'auth'")

        # Validate inputs
        if not all([entity_code, entity_name, email, city, state, country]):
            raise ValueError("Missing required certificate information")

        if len(country) != 2:
            raise ValueError("Country must be a 2-letter code (e.g., 'US')")

        cert_type_lower = cert_type.lower()
        prefix = 'sign' if cert_type_lower == 'signature' else 'Auth'

        logger.info(f"Generating {cert_type} certificates for entity: {entity_code}")

        try:
            # Generate RSA key pair
            private_key, public_key = self.generate_rsa_keypair()

            # Create CSR
            csr = self.create_certificate_signing_request(
                private_key,
                entity_code,
                entity_name,
                contact_person,
                email,
                phone,
                city,
                state,
                country
            )

            # Save keys and CSR
            private_key_path = self.save_private_key(
                private_key,
                f"{prefix}_private.key",
                password
            )
            public_key_path = self.save_public_key(
                public_key,
                f"{prefix}_public.key"
            )
            csr_path = self.save_csr(
                csr,
                f"{prefix}.csr"
            )

            result = {
                "status": "success",
                "certificate_type": cert_type,
                "entity_code": entity_code,
                "entity_name": entity_name,
                "timestamp": datetime.now().isoformat(),
                "files": {
                    "private_key": private_key_path,
                    "public_key": public_key_path,
                    "csr": csr_path
                },
                "key_size": self.key_size,
                "message": f"{cert_type.capitalize()} certificates generated successfully"
            }

            logger.info(f"Successfully generated {cert_type} certificates for {entity_code}")
            return result

        except Exception as e:
            logger.error(f"Error generating certificates: {str(e)}")
            raise

    def get_csr_details(self, csr_path: str) -> dict:
        """
        Read and parse CSR file to extract details
        
        Args:
            csr_path (str): Path to the CSR file
        
        Returns:
            dict: Dictionary containing CSR details
        """
        try:
            with open(csr_path, "rb") as f:
                csr_data = f.read()
            
            csr = x509.load_pem_x509_csr(csr_data, default_backend())
            
            subject = {}
            for attr in csr.subject:
                subject[attr.oid._name] = attr.value
            
            details = {
                "file": csr_path,
                "subject": subject,
                "signature_algorithm": csr.signature_algorithm_oid._name
            }
            
            return details
        except Exception as e:
            logger.error(f"Error reading CSR: {str(e)}")
            raise

    def get_key_info(self, key_path: str, key_type: str = "private", password: str = None) -> dict:
        """
        Read and parse key file to extract details
        
        Args:
            key_path (str): Path to the key file
            key_type (str): 'private' or 'public'
            password (str): Password if private key is encrypted
        
        Returns:
            dict: Dictionary containing key information
        """
        try:
            with open(key_path, "rb") as f:
                key_data = f.read()
            
            if key_type.lower() == "private":
                if password:
                    password_bytes = password.encode()
                else:
                    password_bytes = None
                
                key = serialization.load_pem_private_key(
                    key_data,
                    password=password_bytes,
                    backend=default_backend()
                )
                key_obj = key.public_key() if key_type.lower() == "private" else key
                key_size = key.key_size
            else:
                key = serialization.load_pem_public_key(
                    key_data,
                    backend=default_backend()
                )
                key_size = key.key_size
            
            info = {
                "file": key_path,
                "key_type": key_type,
                "key_size": key_size,
                "algorithm": "RSA"
            }
            
            return info
        except Exception as e:
            logger.error(f"Error reading key file: {str(e)}")
            raise


# Convenience functions for easy use

def generate_signature_certificates(
    entity_code: str,
    entity_name: str,
    contact_person: str,
    email: str,
    phone: str,
    city: str,
    state: str,
    country: str,
    output_dir: str = "certificates",
    password: str = None
) -> dict:
    """
    Generate digital signature certificates
    
    Creates:
    - sign_private.key
    - sign_public.key
    - sign.csr
    """
    generator = CertificateGenerator(output_dir)
    return generator.generate_certificates(
        cert_type="signature",
        entity_code=entity_code,
        entity_name=entity_name,
        contact_person=contact_person,
        email=email,
        phone=phone,
        city=city,
        state=state,
        country=country,
        password=password
    )


def generate_auth_certificates(
    entity_code: str,
    entity_name: str,
    contact_person: str,
    email: str,
    phone: str,
    city: str,
    state: str,
    country: str,
    output_dir: str = "certificates",
    password: str = None
) -> dict:
    """
    Generate authentication certificates
    
    Creates:
    - Auth_private.key
    - Auth_public.key
    - Auth.csr
    """
    generator = CertificateGenerator(output_dir)
    return generator.generate_certificates(
        cert_type="auth",
        entity_code=entity_code,
        entity_name=entity_name,
        contact_person=contact_person,
        email=email,
        phone=phone,
        city=city,
        state=state,
        country=country,
        password=password
    )


# Example usage
if __name__ == "__main__":
    # Example: Generate signature certificates
    print("=" * 60)
    print("Generating Digital Signature Certificates")
    print("=" * 60)
    
    try:
        sig_result = generate_signature_certificates(
            entity_code="SECURITY_SERVER_1",
            entity_name="Security Server Organization",
            contact_person="John Doe",
            email="john.doe@security.org",
            phone="+1-234-567-8900",
            city="San Francisco",
            state="California",
            country="US"
        )
        
        print("\n✅ Signature Certificates Generated:")
        for key, value in sig_result.items():
            if key != "files":
                print(f"  {key}: {value}")
        print("  Files:")
        for file_type, path in sig_result["files"].items():
            print(f"    - {file_type}: {path}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")

    # Example: Generate auth certificates
    print("\n" + "=" * 60)
    print("Generating Authentication Certificates")
    print("=" * 60)
    
    try:
        auth_result = generate_auth_certificates(
            entity_code="AUTH_SERVER_1",
            entity_name="Authentication Server Organization",
            contact_person="Jane Smith",
            email="jane.smith@auth.org",
            phone="+1-987-654-3210",
            city="New York",
            state="New York",
            country="US"
        )
        
        print("\n✅ Auth Certificates Generated:")
        for key, value in auth_result.items():
            if key != "files":
                print(f"  {key}: {value}")
        print("  Files:")
        for file_type, path in auth_result["files"].items():
            print(f"    - {file_type}: {path}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
