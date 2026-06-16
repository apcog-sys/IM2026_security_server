# Certificate Generation Module

This module provides complete functionality to generate RSA key pairs and Certificate Signing Requests (CSR) for both digital signature and authentication purposes.

## Overview

The `certificate_generation.py` module creates:
- **Public Key** (.key file)
- **Private Key** (.key file)
- **Certificate Signing Request** (.csr file)

## Certificate Types

### Digital Signature Certificates
Created files:
- `sign_public.key` - Public key for signature verification
- `sign_private.key` - Private key for signing documents
- `sign.csr` - Certificate Signing Request

### Authentication Certificates
Created files:
- `Auth_public.key` - Public key for auth verification
- `Auth_private.key` - Private key for authentication
- `Auth.csr` - Certificate Signing Request

## Installation

Install required dependencies:
```bash
pip install cryptography pymysql fastapi uvicorn pydantic
```

Or use the requirements file:
```bash
pip install -r requirements.txt
```

## Usage

### Method 1: Using FastAPI Endpoints

#### Generate Certificates via API

**Endpoint:** `POST /api/certificate/generate`

**Request Body:**
```json
{
  "entity_code": "SECURITY_SERVER_1",
  "entity_name": "Security Organization",
  "contact_person": "John Doe",
  "email": "john@example.com",
  "phone": "+1-234-567-8900",
  "city": "San Francisco",
  "state": "California",
  "country": "US",
  "certificate_type": "signature",
  "password": "optional_password_for_key_encryption"
}
```

**Response:**
```json
{
  "status": "success",
  "certificate_type": "signature",
  "entity_code": "SECURITY_SERVER_1",
  "entity_name": "Security Organization",
  "timestamp": "2026-04-03T12:30:45.123456",
  "files": {
    "private_key": "certificates/sign_private.key",
    "public_key": "certificates/sign_public.key",
    "csr": "certificates/sign.csr"
  },
  "key_size": 2048,
  "message": "Signature certificates generated successfully"
}
```

#### Download Certificate Files

**Endpoint:** `GET /api/certificate/download/{cert_type}/{filename}`

Example:
```
GET /api/certificate/download/signature/sign_public.key
GET /api/certificate/download/auth/Auth_private.key
```

#### Get Certificate File List

**Endpoint:** `GET /api/certificate/{cert_type}/{entity_code}/files`

Example:
```
GET /api/certificate/signature/SECURITY_SERVER_1/files
```

### Method 2: Direct Python Usage

#### Generate Signature Certificates

```python
from certificate_generation import generate_signature_certificates

result = generate_signature_certificates(
    entity_code="SECURITY_SERVER_1",
    entity_name="Security Organization",
    contact_person="John Doe",
    email="john@example.com",
    phone="+1-234-567-8900",
    city="San Francisco",
    state="California",
    country="US",  # 2-letter country code
    output_dir="certificates",  # Optional, defaults to 'certificates'
    password="optional_password"  # Optional, for private key encryption
)

print(result['files'])
# Output:
# {
#   'private_key': 'certificates/sign_private.key',
#   'public_key': 'certificates/sign_public.key',
#   'csr': 'certificates/sign.csr'
# }
```

#### Generate Authentication Certificates

```python
from certificate_generation import generate_auth_certificates

result = generate_auth_certificates(
    entity_code="AUTH_SERVER_1",
    entity_name="Authentication Organization",
    contact_person="Jane Smith",
    email="jane@example.com",
    phone="+1-987-654-3210",
    city="New York",
    state="New York",
    country="US",
    output_dir="certificates",
    password="optional_password"
)

print(result['files'])
# Output:
# {
#   'private_key': 'certificates/Auth_private.key',
#   'public_key': 'certificates/Auth_public.key',
#   'csr': 'certificates/Auth.csr'
# }
```

#### Using CertificateGenerator Class

```python
from certificate_generation import CertificateGenerator

# Initialize generator with custom output directory
generator = CertificateGenerator(output_dir="my_certs")

# Generate certificates
result = generator.generate_certificates(
    cert_type="signature",
    entity_code="SERVER_1",
    entity_name="Organization",
    contact_person="Person Name",
    email="email@example.com",
    phone="+1-234-567-8900",
    city="City",
    state="State",
    country="US",
    password="optional_encryption_password"
)

# Read CSR details
csr_details = generator.get_csr_details(result['files']['csr'])
print(csr_details)

# Read key information
key_info = generator.get_key_info(result['files']['public_key'], key_type='public')
print(key_info)
```

## Required Fields

All of the following fields are required:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `entity_code` | string | Unique entity identifier | `SECURITY_SERVER_1` |
| `entity_name` | string | Organization name | `Security Organization` |
| `contact_person` | string | Name of contact person | `John Doe` |
| `email` | string | Email address | `john@example.com` |
| `phone` | string | Phone number | `+1-234-567-8900` |
| `city` | string | City name | `San Francisco` |
| `state` | string | State/Province name | `California` |
| `country` | string | 2-letter country code | `US`, `GB`, `DE`, etc. |
| `certificate_type` | string | `'signature'` or `'auth'` | `signature` |

## Optional Fields

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `password` | string | Password to encrypt private key | No encryption |
| `output_dir` | string | Directory to store certificates | `certificates` |

## Certificate Details

### Certificate Properties
- **Key Size:** 2048-bit RSA
- **Key Format:** PEM (Privacy Enhanced Mail)
- **Private Key Encryption:** PKCS8
- **Hash Algorithm:** SHA256
- **File Permissions:** 600 (private key only)

### CSR Details
The CSR includes:
- Country, State, City, Organization, Common Name
- Email address
- Subject Alternative Names (SAN):
  - RFC822Name (email)
  - URI (entity code as domain)

## File Structure

```
project_root/
├── certificates/
│   ├── sign_public.key       # Digital signature public key
│   ├── sign_private.key      # Digital signature private key
│   ├── sign.csr              # Digital signature CSR
│   ├── Auth_public.key       # Auth public key
│   ├── Auth_private.key      # Auth private key
│   └── Auth.csr              # Auth CSR
├── ss1.py                    # Main FastAPI application
├── certificate_generation.py # Certificate generation module
├── index.html                # Web UI
└── README.md
```

## Security Considerations

1. **Private Key Protection:**
   - Private keys are always saved with restricted permissions (600)
   - Use strong passwords when encrypting private keys
   - Store private keys securely

2. **Key Size:**
   - 2048-bit RSA provides reasonable security for most applications
   - Can be extended to 4096-bit for higher security

3. **CSR Handling:**
   - CSRs can be submitted to a Certificate Authority (CA)
   - CA will sign the CSR to create a valid certificate

4. **File Permissions:**
   ```bash
   # Private keys
   -rw------- (600)
   
   # Public keys and CSR
   -rw-r--r-- (644)
   ```

## Error Handling

### Common Errors

1. **Invalid Country Code**
   ```
   ValueError: Country must be a 2-letter code (e.g., 'US')
   ```
   Solution: Use proper 2-letter ISO country codes (US, GB, DE, etc.)

2. **Missing Required Fields**
   ```
   ValueError: Missing required certificate information
   ```
   Solution: Ensure all required fields are provided

3. **Invalid Certificate Type**
   ```
   ValueError: cert_type must be either 'signature' or 'auth'
   ```
   Solution: Use only 'signature' or 'auth' for certificate_type

4. **Directory Permission Error**
   ```
   PermissionError: [Errno 13] Permission denied
   ```
   Solution: Check write permissions for certificate output directory

## API Integration Example

### Complete Workflow

```python
# 1. Create an entity
import requests

entity_data = {
    "entity_code": "ORG_001",
    "entity_name": "My Organization",
    "contact_person": "Admin User",
    "email": "admin@myorg.com",
    "phone": "+1-555-0123",
    "city": "Boston",
    "state": "Massachusetts",
    "country": "US",
    "address": "123 Main St"
}

# Create entity in database
entity_response = requests.post("http://localhost:8000/api/entity", json=entity_data)
print(entity_response.json())

# 2. Generate certificates for the entity
cert_request = {
    "entity_code": "ORG_001",
    "entity_name": "My Organization",
    "contact_person": "Admin User",
    "email": "admin@myorg.com",
    "phone": "+1-555-0123",
    "city": "Boston",
    "state": "Massachusetts",
    "country": "US",
    "certificate_type": "signature"
}

cert_response = requests.post("http://localhost:8000/api/certificate/generate", json=cert_request)
print(cert_response.json())

# 3. Download certificate files
files_response = requests.get("http://localhost:8000/api/certificate/signature/ORG_001/files")
files = files_response.json()

for file_info in files['files']:
    download = requests.get(f"http://localhost:8000/api/certificate/download/signature/{file_info['filename']}")
    with open(file_info['filename'], 'wb') as f:
        f.write(download.content)
    print(f"Downloaded: {file_info['filename']}")
```

## Testing

### Run Standalone Tests

```bash
python certificate_generation.py
```

This will generate example signature and auth certificates in the `certificates` directory.

### Expected Output

```
============================================================
Generating Digital Signature Certificates
============================================================

✅ Signature Certificates Generated:
  status: success
  certificate_type: signature
  entity_code: SECURITY_SERVER_1
  entity_name: Security Server Organization
  timestamp: 2026-04-03T12:30:45.123456
  key_size: 2048
  message: Signature certificates generated successfully
  Files:
    - private_key: certificates/sign_private.key
    - public_key: certificates/sign_public.key
    - csr: certificates/sign.csr

============================================================
Generating Authentication Certificates
============================================================

✅ Auth Certificates Generated:
  status: success
  certificate_type: auth
  entity_code: AUTH_SERVER_1
  entity_name: Authentication Server Organization
  timestamp: 2026-04-03T12:30:46.234567
  key_size: 2048
  message: Auth certificates generated successfully
  Files:
    - private_key: certificates/Auth_private.key
    - public_key: certificates/Auth_public.key
    - csr: certificates/Auth.csr
```

## Advanced Usage

### Custom Output Directory

```python
from certificate_generation import CertificateGenerator

generator = CertificateGenerator(output_dir="/secure/certificates")

result = generator.generate_certificates(
    cert_type="signature",
    entity_code="SERVER_1",
    # ... other parameters
)
```

### Retrieve Certificate Metadata

```python
# Get CSR details
csr_details = generator.get_csr_details("certificates/sign.csr")
print(f"Subject: {csr_details['subject']}")
print(f"Algorithm: {csr_details['signature_algorithm']}")

# Get key information
key_info = generator.get_key_info(
    "certificates/sign_private.key",
    key_type="private",
    password="encryption_password"
)
print(f"Key Size: {key_info['key_size']} bits")
print(f"Algorithm: {key_info['algorithm']}")
```

## Troubleshooting

### Certificates Not Generated

1. Check permissions on certificates directory
2. Ensure all required fields are provided
3. Verify country code is 2 letters

### Cannot Read Private Key

1. Verify correct password if encrypted
2. Check file exists and is readable
3. Ensure file permissions allow reading

### CSR Submission to CA

1. Use the `.csr` file to request a certificate from Certificate Authority
2. CA will validate the CSR details
3. CA returns a signed `.crt` certificate
4. Install the certificate with the matching private key

## Support

For issues or questions, check:
1. Python cryptography documentation: https://cryptography.io/
2. RFC 2314 - PKCS #10: Certification Request Syntax
3. RFC 5280 - Internet X.509 Public Key Infrastructure
