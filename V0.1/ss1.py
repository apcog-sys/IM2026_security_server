from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import uuid
from pydantic import BaseModel
from typing import Optional, List
import pymysql
from pymysql import Error
import json
import os
from datetime import datetime
import logging
import requests
from certificate_generation import generate_signature_certificates, generate_auth_certificates, CertificateGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="System Configuration API", version="1.0.0")

# Global variable to store DB configuration
db_config = {
    "host": None,
    "port": 3306,
    "user": None,
    "password": None,
    "database": None
}

# Resolve paths relative to this script's directory so any number of
# instances can run from different directories with their own db_config.json
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "db_config.json")

# ===================== Pydantic Models =====================

class DBConfig(BaseModel):
    host: str
    port: int = 3306
    user: str
    password: str
    database: str


class NetworkConfig(BaseModel):
    id: str
    title: str
    version: Optional[str] = None
    network_instance: Optional[str] = None
    gateway_code: Optional[str] = None
    entity_id: Optional[int] = None
    host: str
    port: Optional[int] = None
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    environment: Optional[str] = "PROD"


class EntityOwner(BaseModel):
    entity_code: str
    entity_name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None


class CertificateRequest(BaseModel):
    entity_code: str
    entity_name: str
    contact_person: str
    email: str
    phone: str
    city: str
    state: str
    country: str
    certificate_type: str  # 'signature' or 'auth'
    password: Optional[str] = None  # Optional password for private key encryption


class SecurityServer(BaseModel):
    server_code: str
    server_name: str
    server_type: str
    entity_id: int
    network_id: int
    host: str
    port: int
    protocol: str
    version: Optional[str] = None
    status: Optional[str] = 'ACTIVE'
    environment: Optional[str] = 'DEV'
    admin_name: Optional[str] = None
    admin_email: Optional[str] = None
    admin_phone: Optional[str] = None
    certificate_path: Optional[str] = None
    description: Optional[str] = None


class GlobalServerRequest(BaseModel):
    server_name: str
    server_url: str
    api_key: Optional[str] = None
    description: Optional[str] = None

class SecurityService(BaseModel):
    service_code: str
    service_name: str
    service_type: str
    server_id: int
    endpoint_url: str
    api_version: Optional[str] = 'v1.0'
    wsdl_url: Optional[str] = None
    description: Optional[str] = None


class MyApplication(BaseModel):
    app_code: str
    app_name: str
    app_type: str = 'APPLICATION'
    entity_id: Optional[int] = None
    network_id: str
    host: str
    port: int
    protocol: str
    version: Optional[str] = None
    status: Optional[str] = 'PENDING'
    environment: Optional[str] = 'DEV'
    administrator: Optional[str] = None
    admin_email: Optional[str] = None
    admin_phone: Optional[str] = None
    certificate_path: Optional[str] = None
    description: Optional[str] = None


class MyService(BaseModel):
    service_code: str
    service_name: str
    app_id: int
    service_type: str = 'REST'
    method: Optional[str] = 'GET'
    endpoint_path: str
    full_url: Optional[str] = None
    api_version: Optional[str] = 'v1.0'
    timeout: Optional[int] = 30
    retry_count: Optional[int] = 3
    status: Optional[str] = 'ACTIVE'
    is_public: Optional[bool] = False
    description: Optional[str] = None


class ClientServiceRegistry(BaseModel):
    ss_id: str
    ss_name: Optional[str] = None
    ss_hostname: Optional[str] = None
    ss_ip: Optional[str] = None
    ss_port: Optional[int] = None
    ss_environment: Optional[str] = None
    entity_code: Optional[str] = None
    entity_name: Optional[str] = None
    app_code: Optional[str] = None
    app_name: Optional[str] = None
    service_code: str
    service_name: Optional[str] = None
    service_type: Optional[str] = 'REST'
    method: Optional[str] = 'GET'
    endpoint_path: Optional[str] = None
    full_url: Optional[str] = None
    api_version: Optional[str] = 'v1.0'
    certificate: Optional[str] = None
    certificate_expiry: Optional[str] = None
    tls_enabled: Optional[bool] = True
    timeout: Optional[int] = 30
    retry_count: Optional[int] = 3
    status: Optional[str] = 'ACTIVE'
    last_synced_at: Optional[str] = None
    source: Optional[str] = 'MANUAL'


# ===================== Database Connection Functions =====================

def get_db_connection():
    """Create and return a database connection"""
    if not all([db_config['host'], db_config['user'], db_config['database']]):
        raise HTTPException(status_code=400, detail="Database not configured. Please configure DB connection first.")
    
    try:
        connection = pymysql.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Error as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")


def ensure_global_server_table_exists():
    """Ensure the global_server_config table exists in the database"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT 1 FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'global_server_config'
        """, (db_config['database'],))
        
        if not cursor.fetchone():
            # Create table
            cursor.execute("""
                CREATE TABLE global_server_config (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    server_name VARCHAR(255) NOT NULL UNIQUE,
                    server_url VARCHAR(500) NOT NULL,
                    api_key VARCHAR(1000),
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_server_url (server_url)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            connection.commit()
            logger.info("global_server_config table created successfully")
        
        cursor.close()
        connection.close()
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Could not ensure global_server_config table exists: {str(e)}")


def save_db_config_to_file():
    """Save DB configuration to JSON file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(db_config, f, indent=4)
        logger.info("DB configuration saved to file")
    except Exception as e:
        logger.error(f"Error saving config file: {e}")


def load_db_config_from_file():
    """Load DB configuration from JSON file"""
    global db_config
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config_data = json.load(f)
                db_config.update(config_data)
            logger.info("DB configuration loaded from file")
    except Exception as e:
        logger.error(f"Error loading config file: {e}")


# Load configuration on startup
load_db_config_from_file()


# ===================== API Routes - DB Configuration =====================

@app.post("/api/db/test-connection")
async def test_db_connection(config: DBConfig):
    """Test database connection"""
    try:
        connection = pymysql.connect(
            host=config.host,
            port=config.port,
            user=config.user,
            password=config.password,
            database=config.database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        connection.close()
        logger.info(f"Database connection test successful to {config.host}")
        return {"status": "success", "message": "Database connection successful"}
    except Error as e:
        logger.error(f"Database connection test failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/db/save-config")
async def save_db_configuration(config: DBConfig):
    """Save database configuration"""
    global db_config
    try:
        # Test the connection first
        connection = pymysql.connect(
            host=config.host,
            port=config.port,
            user=config.user,
            password=config.password,
            database=config.database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        connection.close()
        
        # Save to global variable
        db_config.update({
            "host": config.host,
            "port": config.port,
            "user": config.user,
            "password": config.password,
            "database": config.database
        })
        
        # Save to file
        save_db_config_to_file()
        
        logger.info(f"DB configuration saved: {config.host}:{config.port}/{config.database}")
        return {"status": "success", "message": "Configuration saved successfully"}
    except Error as e:
        logger.error(f"Error saving DB configuration: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/db/get-config")
async def get_db_configuration():
    """Get current database configuration (without password)"""
    return {
        "host": db_config.get("host"),
        "port": db_config.get("port", 3306),
        "user": db_config.get("user"),
        "database": db_config.get("database")
    }


# ===================== API Routes - Network Configuration CRUD =====================

@app.get("/api/network", response_model=List[dict])
async def get_all_network_configs():
    """Get all network configurations"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("SELECT * FROM network_config ORDER BY created_at DESC")
        results = cursor.fetchall()
        
        # Convert datetime objects to strings
        for result in results:
            if isinstance(result.get('created_at'), datetime):
                result['created_at'] = result['created_at'].isoformat()
            if isinstance(result.get('updated_at'), datetime):
                result['updated_at'] = result['updated_at'].isoformat()
        
        cursor.close()
        connection.close()
        
        logger.info(f"Retrieved {len(results)} network configurations")
        return results
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving network configs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/network/{network_id}", response_model=dict)
async def get_network_config(network_id: str):
    """Get a specific network configuration by ID"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("SELECT * FROM network_config WHERE id = %s", (network_id,))
        result = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if not result:
            raise HTTPException(status_code=404, detail=f"Network configuration '{network_id}' not found")
        
        # Convert datetime to string
        if isinstance(result.get('created_at'), datetime):
            result['created_at'] = result['created_at'].isoformat()
        if isinstance(result.get('updated_at'), datetime):
            result['updated_at'] = result['updated_at'].isoformat()
        
        logger.info(f"Retrieved network configuration: {network_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving network config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/network", response_model=dict)
async def create_network_config(config: NetworkConfig):
    """Create a new network configuration"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if ID already exists
        cursor.execute("SELECT id FROM network_config WHERE id = %s", (config.id,))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            raise HTTPException(status_code=400, detail=f"Network configuration with ID '{config.id}' already exists")
        
        # Insert new configuration
        insert_query = """
            INSERT INTO network_config 
            (id, title, version, network_instance, gateway_code, entity_id, host, port, hostname, ip_address, environment)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (
            config.id,
            config.title,
            config.version,
            config.network_instance,
            config.gateway_code,
            config.entity_id,
            config.host,
            config.port,
            config.hostname,
            config.ip_address,
            config.environment
        ))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        logger.info(f"Created network configuration: {config.id}")
        return {"status": "success", "message": f"Network configuration '{config.id}' created successfully", "id": config.id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating network config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/network/{network_id}", response_model=dict)
async def update_network_config(network_id: str, config: NetworkConfig):
    """Update an existing network configuration"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if configuration exists
        cursor.execute("SELECT id FROM network_config WHERE id = %s", (network_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail=f"Network configuration '{network_id}' not found")
        
        # Update configuration
        update_query = """
            UPDATE network_config 
            SET title = %s, version = %s, network_instance = %s, gateway_code = %s, 
                entity_id = %s, host = %s, port = %s, hostname = %s, ip_address = %s, 
                environment = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        
        cursor.execute(update_query, (
            config.title,
            config.version,
            config.network_instance,
            config.gateway_code,
            config.entity_id,
            config.host,
            config.port,
            config.hostname,
            config.ip_address,
            config.environment,
            network_id
        ))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        logger.info(f"Updated network configuration: {network_id}")
        return {"status": "success", "message": f"Network configuration '{network_id}' updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating network config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/network/{network_id}", response_model=dict)
async def delete_network_config(network_id: str):
    """Delete a network configuration"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if configuration exists
        cursor.execute("SELECT id FROM network_config WHERE id = %s", (network_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail=f"Network configuration '{network_id}' not found")
        
        # Delete configuration
        cursor.execute("DELETE FROM network_config WHERE id = %s", (network_id,))
        connection.commit()
        cursor.close()
        connection.close()
        
        logger.info(f"Deleted network configuration: {network_id}")
        return {"status": "success", "message": f"Network configuration '{network_id}' deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting network config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================== API Routes - Entity Owner CRUD =====================

@app.get("/api/entity", response_model=List[dict])
async def get_all_entities():
    """Get all entity owners"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("SELECT * FROM entity_owner ORDER BY created_at DESC")
        results = cursor.fetchall()
        
        # Convert results to list of dicts
        entity_list = []
        for row in results:
            # Since we use DictCursor, row is already a dict
            if isinstance(row, dict):
                entity_list.append({
                    'id': row.get('id'),
                    'entity_code': row.get('entity_code'),
                    'entity_name': row.get('entity_name'),
                    'contact_person': row.get('contact_person'),
                    'email': row.get('email'),
                    'phone': row.get('phone'),
                    'address': row.get('address'),
                    'country': row.get('country'),
                    'state': row.get('state'),
                    'city': row.get('city'),
                    'created_at': row.get('created_at').isoformat() if isinstance(row.get('created_at'), datetime) else row.get('created_at'),
                    'updated_at': row.get('updated_at').isoformat() if isinstance(row.get('updated_at'), datetime) else row.get('updated_at')
                })
            else:
                # Fallback for tuple format
                entity_list.append({
                    'id': row[0],
                    'entity_code': row[1],
                    'entity_name': row[2],
                    'contact_person': row[3],
                    'email': row[4],
                    'phone': row[5],
                    'address': row[6],
                    'country': row[7],
                    'state': row[8],
                    'city': row[9],
                    'created_at': row[10].isoformat() if isinstance(row[10], datetime) else row[10],
                    'updated_at': row[11].isoformat() if isinstance(row[11], datetime) else row[11]
                })
        
        cursor.close()
        connection.close()
        
        logger.info(f"Retrieved {len(entity_list)} entities")
        return entity_list
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving entities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/entity/{entity_id}", response_model=dict)
async def get_entity(entity_id: int):
    """Get a specific entity owner by ID"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("SELECT * FROM entity_owner WHERE id = %s", (entity_id,))
        result = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if not result:
            raise HTTPException(status_code=404, detail=f"Entity '{entity_id}' not found")
        
        # Since we use DictCursor, result is already a dict
        if isinstance(result, dict):
            entity = {
                'id': result.get('id'),
                'entity_code': result.get('entity_code'),
                'entity_name': result.get('entity_name'),
                'contact_person': result.get('contact_person'),
                'email': result.get('email'),
                'phone': result.get('phone'),
                'address': result.get('address'),
                'country': result.get('country'),
                'state': result.get('state'),
                'city': result.get('city'),
                'created_at': result.get('created_at').isoformat() if isinstance(result.get('created_at'), datetime) else result.get('created_at'),
                'updated_at': result.get('updated_at').isoformat() if isinstance(result.get('updated_at'), datetime) else result.get('updated_at')
            }
        else:
            # Fallback for tuple format
            entity = {
                'id': result[0],
                'entity_code': result[1],
                'entity_name': result[2],
                'contact_person': result[3],
                'email': result[4],
                'phone': result[5],
                'address': result[6],
                'country': result[7],
                'state': result[8],
                'city': result[9],
                'created_at': result[10].isoformat() if isinstance(result[10], datetime) else result[10],
                'updated_at': result[11].isoformat() if isinstance(result[11], datetime) else result[11]
            }
        
        logger.info(f"Retrieved entity: {entity_id}")
        return entity
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving entity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/entity", response_model=dict)
async def create_entity(entity: EntityOwner):
    """Create a new entity owner"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if entity code already exists
        cursor.execute("SELECT id FROM entity_owner WHERE entity_code = %s", (entity.entity_code,))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            raise HTTPException(status_code=400, detail=f"Entity code '{entity.entity_code}' already exists")
        
        # Insert new entity
        insert_query = """
            INSERT INTO entity_owner 
            (entity_code, entity_name, contact_person, email, phone, address, country, state, city)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (
            entity.entity_code,
            entity.entity_name,
            entity.contact_person,
            entity.email,
            entity.phone,
            entity.address,
            entity.country,
            entity.state,
            entity.city
        ))
        
        connection.commit()
        entity_id = cursor.lastrowid
        cursor.close()
        connection.close()
        
        logger.info(f"Created entity: {entity.entity_code}")
        return {"status": "success", "message": f"Entity '{entity.entity_code}' created successfully", "id": entity_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating entity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/entity/{entity_id}", response_model=dict)
async def update_entity(entity_id: int, entity: EntityOwner):
    """Update an existing entity owner"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if entity exists
        cursor.execute("SELECT id FROM entity_owner WHERE id = %s", (entity_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail=f"Entity '{entity_id}' not found")
        
        # Update entity
        update_query = """
            UPDATE entity_owner 
            SET entity_name = %s, contact_person = %s, email = %s, phone = %s, 
                address = %s, country = %s, state = %s, city = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        
        cursor.execute(update_query, (
            entity.entity_name,
            entity.contact_person,
            entity.email,
            entity.phone,
            entity.address,
            entity.country,
            entity.state,
            entity.city,
            entity_id
        ))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        logger.info(f"Updated entity: {entity_id}")
        return {"status": "success", "message": f"Entity '{entity_id}' updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating entity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/entity/{entity_id}", response_model=dict)
async def delete_entity(entity_id: int):
    """Delete an entity owner"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if entity exists
        cursor.execute("SELECT id FROM entity_owner WHERE id = %s", (entity_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail=f"Entity '{entity_id}' not found")
        
        # Delete entity
        cursor.execute("DELETE FROM entity_owner WHERE id = %s", (entity_id,))
        connection.commit()
        cursor.close()
        connection.close()
        
        logger.info(f"Deleted entity: {entity_id}")
        return {"status": "success", "message": f"Entity '{entity_id}' deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting entity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================== API Routes - Certificate Generation =====================

@app.post("/api/certificate/generate")
async def generate_certificate(cert_request: CertificateRequest):
    """Generate digital signature or authentication certificates"""
    try:
        # Validate certificate type
        if cert_request.certificate_type.lower() not in ['signature', 'auth']:
            raise HTTPException(status_code=400, detail="certificate_type must be 'signature' or 'auth'")
        
        # Validate country code (must be 2 letters)
        if len(cert_request.country) != 2:
            raise HTTPException(status_code=400, detail="Country must be a 2-letter code (e.g., 'US')")
        
        # Check if certificates directory exists
        cert_dir = "certificates"
        if not os.path.exists(cert_dir):
            os.makedirs(cert_dir)
        
        logger.info(f"Generating {cert_request.certificate_type} certificate for {cert_request.entity_code}")
        
        # Generate both signature and auth certificates
        signature_result = generate_signature_certificates(
            entity_code=cert_request.entity_code,
            entity_name=cert_request.entity_name,
            contact_person=cert_request.contact_person,
            email=cert_request.email,
            phone=cert_request.phone,
            city=cert_request.city,
            state=cert_request.state,
            country=cert_request.country,
            output_dir=cert_dir,
            password=cert_request.password
        )
        
        auth_result = generate_auth_certificates(
            entity_code=cert_request.entity_code,
            entity_name=cert_request.entity_name,
            contact_person=cert_request.contact_person,
            email=cert_request.email,
            phone=cert_request.phone,
            city=cert_request.city,
            state=cert_request.state,
            country=cert_request.country,
            output_dir=cert_dir,
            password=cert_request.password
        )
        
        logger.info(f"Successfully generated both signature and auth certificates for {cert_request.entity_code}")
        
        # Return combined result with both certificate types
        result = {
            "status": "success",
            "message": "Both signature and authentication certificates generated successfully",
            "signature_certificate": signature_result,
            "auth_certificate": auth_result,
            "timestamp": datetime.now().isoformat()
        }
        return result
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating certificate: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/certificate/{cert_type}/{entity_code}/files")
async def get_certificate_files(cert_type: str, entity_code: str):
    """Get list of certificate files for an entity"""
    try:
        cert_type_lower = cert_type.lower()
        if cert_type_lower not in ['signature', 'auth']:
            raise HTTPException(status_code=400, detail="cert_type must be 'signature' or 'auth'")
        
        prefix = 'sign' if cert_type_lower == 'signature' else 'Auth'
        cert_dir = "certificates"
        
        files_list = []
        for file_extension in ['_public.key', '_private.key', '.csr']:
            filename = f"{prefix}{file_extension}"
            filepath = os.path.join(cert_dir, filename)
            
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                files_list.append({
                    "filename": filename,
                    "path": filepath,
                    "size": file_size,
                    "exists": True
                })
        
        if not files_list:
            raise HTTPException(status_code=404, detail=f"No certificate files found for {prefix}")
        
        logger.info(f"Retrieved {len(files_list)} certificate files for {prefix}")
        return {
            "certificate_type": cert_type,
            "prefix": prefix,
            "files": files_list
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving certificate files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/certificate/list/{cert_type}")
async def list_certificate_files(cert_type: str):
    """List all certificate files of a specific type (signature or auth)"""
    try:
        cert_type_lower = cert_type.lower()
        if cert_type_lower not in ['signature', 'auth']:
            raise HTTPException(status_code=400, detail="cert_type must be 'signature' or 'auth'")
        
        prefix = 'sign' if cert_type_lower == 'signature' else 'Auth'
        cert_dir = "certificates"
        
        # Create certificates directory if it doesn't exist
        if not os.path.exists(cert_dir):
            os.makedirs(cert_dir)
            return {"certificate_type": cert_type, "files": []}
        
        files_list = []
        # List all files in the certificates directory that match the prefix
        try:
            for file in os.listdir(cert_dir):
                if file.startswith(prefix):
                    filepath = os.path.join(cert_dir, file)
                    if os.path.isfile(filepath):
                        file_size = os.path.getsize(filepath)
                        file_modified = datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                        files_list.append({
                            "filename": file,
                            "size": file_size,
                            "modified": file_modified
                        })
        except OSError as e:
            logger.error(f"Error reading certificates directory: {str(e)}")
        
        logger.info(f"Found {len(files_list)} {cert_type} certificate files")
        return {
            "certificate_type": cert_type,
            "prefix": prefix,
            "files": sorted(files_list, key=lambda x: x['modified'], reverse=True)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing certificate files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/certificate/download/{cert_type}/{filename}")
async def download_certificate(cert_type: str, filename: str):
    """Download a specific certificate file"""
    try:
        cert_type_lower = cert_type.lower()
        if cert_type_lower not in ['signature', 'auth']:
            raise HTTPException(status_code=400, detail="cert_type must be 'signature' or 'auth'")
        
        prefix = 'sign' if cert_type_lower == 'signature' else 'Auth'
        
        # Validate filename starts with expected prefix
        if not filename.startswith(prefix):
            raise HTTPException(status_code=400, detail=f"Invalid filename for {prefix} certificates")
        
        cert_dir = "certificates"
        filepath = os.path.join(cert_dir, filename)
        
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail=f"File not found: {filename}")
        
        logger.info(f"Downloading certificate file: {filename}")
        return FileResponse(filepath, filename=filename)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading certificate: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/certificate/view")
async def view_certificate(path: str):
    """View certificate file content"""
    try:
        # Security check: ensure path is within certificates directory
        cert_dir = "certificates"
        full_path = os.path.join(cert_dir, os.path.basename(path))
        
        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail="Certificate file not found")
        
        # Read the certificate file
        with open(full_path, 'r') as f:
            content = f.read()
        
        logger.info(f"Viewed certificate file: {path}")
        return {"content": content, "filename": os.path.basename(full_path)}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error viewing certificate: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/register-to-global-server")
async def register_to_global_server(registration_data: dict):
    """Register this security server to the Global Server"""
    try:
        global_server_url = registration_data.get('global_server_url')
        api_key = registration_data.get('api_key')
        description = registration_data.get('description', '')
        include_certificate = registration_data.get('include_certificate', True)
        
        if not global_server_url:
            raise HTTPException(status_code=400, detail="Global Server URL is required")
        
        # Prepare registration payload
        payload = {
            'server_registration': {
                'description': description,
                'registered_at': datetime.now().isoformat(),
                'include_certificate': include_certificate
            }
        }
        
        # If certificate should be included, fetch the latest signature certificate
        if include_certificate:
            cert_dir = "certificates"
            cert_files = []
            if os.path.exists(cert_dir):
                for file in os.listdir(cert_dir):
                    if file.startswith('sign') and file.endswith('_public.key'):
                        file_path = os.path.join(cert_dir, file)
                        with open(file_path, 'r') as f:
                            cert_content = f.read()
                        cert_files.append({
                            'filename': file,
                            'content': cert_content
                        })
            
            if cert_files:
                payload['certificate'] = cert_files[0]
        
        # Register to global server
        headers = {'Content-Type': 'application/json'}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        try:
            response = requests.post(
                f"{global_server_url}/api/register-security-server",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Successfully registered to Global Server: {global_server_url}")
                return {
                    "message": "Security Server registered successfully",
                    "registration_id": response.json().get('registration_id', 'N/A')
                }
            else:
                logger.error(f"Registration failed with status {response.status_code}: {response.text}")
                raise HTTPException(status_code=400, detail=f"Registration failed: {response.text}")
        
        except requests.exceptions.Timeout:
            logger.error(f"Timeout connecting to Global Server: {global_server_url}")
            raise HTTPException(status_code=504, detail="Global Server connection timeout")
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to Global Server: {global_server_url}")
            raise HTTPException(status_code=503, detail="Cannot connect to Global Server")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering to Global Server: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================== API Routes - Global Server Configuration =====================

@app.get("/api/global-server")
async def list_global_servers():
    """Get all global server configurations"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            SELECT id, server_name, server_url, api_key, description, created_at
            FROM global_server_config
            ORDER BY created_at DESC
        """)
        
        servers = cursor.fetchall()
        cursor.close()
        connection.close()
        
        logger.info(f"Retrieved {len(servers)} global server configurations")
        return servers if servers else []
    
    except Exception as e:
        logger.error(f"Error retrieving global server configurations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/global-server/{server_id}")
async def get_global_server(server_id: int):
    """Get a specific global server configuration"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            SELECT id, server_name, server_url, api_key, description, created_at
            FROM global_server_config
            WHERE id = %s
        """, (server_id,))
        
        server = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if not server:
            raise HTTPException(status_code=404, detail="Global server configuration not found")
        
        logger.info(f"Retrieved global server configuration: {server_id}")
        return server
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving global server configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/global-server")
async def create_global_server(server_config: GlobalServerRequest):
    """Create a new global server configuration"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            INSERT INTO global_server_config (server_name, server_url, api_key, description, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            server_config.server_name,
            server_config.server_url,
            server_config.api_key,
            server_config.description,
            datetime.now().isoformat()
        ))
        
        connection.commit()
        new_id = cursor.lastrowid
        cursor.close()
        connection.close()
        
        logger.info(f"Created global server configuration: {new_id}")
        return {
            "id": new_id,
            "server_name": server_config.server_name,
            "server_url": server_config.server_url,
            "message": "Global server configuration created successfully"
        }
    
    except Exception as e:
        logger.error(f"Error creating global server configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/global-server/{server_id}")
async def update_global_server(server_id: int, server_config: GlobalServerRequest):
    """Update a global server configuration"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # Check if exists
        cursor.execute("SELECT id FROM global_server_config WHERE id = %s", (server_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="Global server configuration not found")
        
        # Update
        update_query = """
            UPDATE global_server_config
            SET server_name = %s, server_url = %s, description = %s
        """
        params = (server_config.server_name, server_config.server_url, server_config.description)
        
        # Only update api_key if provided
        if server_config.api_key:
            update_query += ", api_key = %s"
            params = (server_config.server_name, server_config.server_url, server_config.description, server_config.api_key)
        
        update_query += " WHERE id = %s"
        params = params + (server_id,)
        
        cursor.execute(update_query, params)
        connection.commit()
        cursor.close()
        connection.close()
        
        logger.info(f"Updated global server configuration: {server_id}")
        return {
            "id": server_id,
            "server_name": server_config.server_name,
            "server_url": server_config.server_url,
            "message": "Global server configuration updated successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating global server configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/global-server/{server_id}")
async def delete_global_server(server_id: int):
    """Delete a global server configuration"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("DELETE FROM global_server_config WHERE id = %s", (server_id,))
        
        if cursor.rowcount == 0:
            connection.close()
            raise HTTPException(status_code=404, detail="Global server configuration not found")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        logger.info(f"Deleted global server configuration: {server_id}")
        return {"message": "Global server configuration deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting global server configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================== Static Files =====================

@app.get("/")
async def root():
    """Serve the index.html file"""
    return FileResponse(os.path.join(SCRIPT_DIR, "index.html"))


# Serve static files (HTML, CSS, JS) from this script's directory
app.mount("/static", StaticFiles(directory=SCRIPT_DIR), name="static")


# ===================== Health Check =====================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    db_connected = False
    try:
        connection = get_db_connection()
        connection.close()
        db_connected = True
    except:
        db_connected = False
    
    return {
        "status": "healthy",
        "database_configured": all([db_config['host'], db_config['user'], db_config['database']]),
        "database_connected": db_connected
    }


# ===================== Root endpoint for API =====================

@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "name": "System Configuration API",
        "version": "1.0.0",
        "endpoints": {
            "ui": "/",
            "health": "/api/health",
            "db": {
                "test": "POST /api/db/test-connection",
                "save": "POST /api/db/save-config",
                "get": "GET /api/db/get-config"
            },
            "network": {
                "list": "GET /api/network",
                "get": "GET /api/network/{id}",
                "create": "POST /api/network",
                "update": "PUT /api/network/{id}",
                "delete": "DELETE /api/network/{id}"
            }
        }
    }


# ===================== Security Server Management =====================

@app.post("/api/security-server")
async def create_security_server(server: SecurityServer):
    """Create a new security server"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if entity exists
        cursor.execute("SELECT id FROM entity_owner WHERE id = %s", (server.entity_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="Entity not found")
        
        # Check if network exists
        cursor.execute("SELECT id FROM network_config WHERE id = %s", (server.network_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="Network configuration not found")
        
        # Insert security server
        query = """INSERT INTO security_server (
            server_code, server_name, server_type, entity_id, network_id, 
            host, port, protocol, version, status, environment, 
            admin_name, admin_email, admin_phone, registration_date, 
            certificate_path, last_health_check, health_status, description
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        
        from datetime import datetime
        values = (
            server.server_code, server.server_name, server.server_type, 
            server.entity_id, server.network_id, server.host, server.port, 
            server.protocol, server.version, server.status, server.environment,
            server.admin_name, server.admin_email, server.admin_phone,
            datetime.now(), server.certificate_path, datetime.now(), 
            'UP', server.description
        )
        
        cursor.execute(query, values)
        connection.commit()
        server_id = cursor.lastrowid
        
        cursor.close()
        connection.close()
        
        logger.info(f"Created security server: {server.server_code}")
        return {"id": server_id, "message": "Security server created successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating security server: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/security-server")
async def list_security_servers():
    """Get all security servers"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = """SELECT 
            id, server_code, server_name, server_type, entity_id, network_id,
            host, port, protocol, version, status, environment,
            admin_name, admin_email, admin_phone, registration_date,
            certificate_path, last_health_check, health_status, description
            FROM security_server 
            ORDER BY server_code"""
        
        cursor.execute(query)
        servers = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        # Ensure dict format
        result = []
        for row in servers:
            if isinstance(row, dict):
                result.append(row)
            else:
                result.append({
                    "id": row[0], "server_code": row[1], "server_name": row[2],
                    "server_type": row[3], "entity_id": row[4], "network_id": row[5],
                    "host": row[6], "port": row[7], "protocol": row[8], "version": row[9],
                    "status": row[10], "environment": row[11], "admin_name": row[12],
                    "admin_email": row[13], "admin_phone": row[14], "registration_date": str(row[15]),
                    "certificate_path": row[16], "last_health_check": str(row[17]),
                    "health_status": row[18], "description": row[19]
                })
        
        logger.info(f"Retrieved {len(result)} security servers")
        return result
    
    except Exception as e:
        logger.error(f"Error retrieving security servers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/security-server/{server_id}")
async def get_security_server(server_id: int):
    """Get a specific security server"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("""SELECT 
            id, server_code, server_name, server_type, entity_id, network_id,
            host, port, protocol, version, status, environment,
            admin_name, admin_email, admin_phone, registration_date,
            certificate_path, last_health_check, health_status, description
            FROM security_server WHERE id = %s""", (server_id,))
        
        server = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if not server:
            raise HTTPException(status_code=404, detail="Security server not found")
        
        # Ensure dict format
        if isinstance(server, dict):
            return server
        else:
            return {
                "id": server[0], "server_code": server[1], "server_name": server[2],
                "server_type": server[3], "entity_id": server[4], "network_id": server[5],
                "host": server[6], "port": server[7], "protocol": server[8], "version": server[9],
                "status": server[10], "environment": server[11], "admin_name": server[12],
                "admin_email": server[13], "admin_phone": server[14], "registration_date": str(server[15]),
                "certificate_path": server[16], "last_health_check": str(server[17]),
                "health_status": server[18], "description": server[19]
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving security server: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/security-server/{server_id}")
async def update_security_server(server_id: int, server: SecurityServer):
    """Update a security server"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if server exists
        cursor.execute("SELECT id FROM security_server WHERE id = %s", (server_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="Security server not found")
        
        # Update security server
        query = """UPDATE security_server SET 
            server_code = %s, server_name = %s, server_type = %s, entity_id = %s,
            network_id = %s, host = %s, port = %s, protocol = %s, version = %s,
            status = %s, environment = %s, admin_name = %s, admin_email = %s,
            admin_phone = %s, certificate_path = %s, description = %s
            WHERE id = %s"""
        
        values = (
            server.server_code, server.server_name, server.server_type, server.entity_id,
            server.network_id, server.host, server.port, server.protocol, server.version,
            server.status, server.environment, server.admin_name, server.admin_email,
            server.admin_phone, server.certificate_path, server.description, server_id
        )
        
        cursor.execute(query, values)
        connection.commit()
        
        cursor.close()
        connection.close()
        
        logger.info(f"Updated security server: {server.server_code}")
        return {"message": "Security server updated successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating security server: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/security-server/{server_id}")
async def delete_security_server(server_id: int):
    """Delete a security server"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Get server info before deletion
        cursor.execute("SELECT server_code FROM security_server WHERE id = %s", (server_id,))
        result = cursor.fetchone()
        if not result:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="Security server not found")
        
        server_code = result.get('server_code') if isinstance(result, dict) else result[0]
        
        # Delete associated services first (foreign key constraint)
        cursor.execute("DELETE FROM security_service WHERE server_id = %s", (server_id,))
        
        # Delete the server
        cursor.execute("DELETE FROM security_server WHERE id = %s", (server_id,))
        connection.commit()
        
        cursor.close()
        connection.close()
        
        logger.info(f"Deleted security server: {server_code}")
        return {"message": "Security server deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting security server: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================== Security Service Management =====================

@app.post("/api/security-service")
async def create_security_service(service: SecurityService):
    """Create a new security service"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if server exists
        cursor.execute("SELECT id FROM security_server WHERE id = %s", (service.server_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="Security server not found")
        
        # Insert security service
        query = """INSERT INTO security_service (
            service_code, service_name, service_type, server_id, 
            endpoint_url, api_version, wsdl_url, status, description
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        
        values = (
            service.service_code, service.service_name, service.service_type,
            service.server_id, service.endpoint_url, service.api_version,
            service.wsdl_url, 'ACTIVE', service.description
        )
        
        cursor.execute(query, values)
        connection.commit()
        service_id = cursor.lastrowid
        
        cursor.close()
        connection.close()
        
        logger.info(f"Created security service: {service.service_code}")
        return {"id": service_id, "message": "Security service created successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating security service: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/security-service")
async def list_security_services():
    """Get all security services"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = """SELECT 
            id, service_code, service_name, service_type, server_id,
            endpoint_url, api_version, wsdl_url, status, description
            FROM security_service 
            ORDER BY service_code"""
        
        cursor.execute(query)
        services = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        # Ensure dict format
        result = []
        for row in services:
            if isinstance(row, dict):
                result.append(row)
            else:
                result.append({
                    "id": row[0], "service_code": row[1], "service_name": row[2],
                    "service_type": row[3], "server_id": row[4], "endpoint_url": row[5],
                    "api_version": row[6], "wsdl_url": row[7], "status": row[8],
                    "description": row[9]
                })
        
        logger.info(f"Retrieved {len(result)} security services")
        return result
    
    except Exception as e:
        logger.error(f"Error retrieving security services: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/security-service/{service_id}")
async def get_security_service(service_id: int):
    """Get a specific security service"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("""SELECT 
            id, service_code, service_name, service_type, server_id,
            endpoint_url, api_version, wsdl_url, status, description
            FROM security_service WHERE id = %s""", (service_id,))
        
        service = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if not service:
            raise HTTPException(status_code=404, detail="Security service not found")
        
        # Ensure dict format
        if isinstance(service, dict):
            return service
        else:
            return {
                "id": service[0], "service_code": service[1], "service_name": service[2],
                "service_type": service[3], "server_id": service[4], "endpoint_url": service[5],
                "api_version": service[6], "wsdl_url": service[7], "status": service[8],
                "description": service[9]
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving security service: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/security-service/{service_id}")
async def update_security_service(service_id: int, service: SecurityService):
    """Update a security service"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if service exists
        cursor.execute("SELECT id FROM security_service WHERE id = %s", (service_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="Security service not found")
        
        # Update security service
        query = """UPDATE security_service SET 
            service_code = %s, service_name = %s, service_type = %s, server_id = %s,
            endpoint_url = %s, api_version = %s, wsdl_url = %s, description = %s
            WHERE id = %s"""
        
        values = (
            service.service_code, service.service_name, service.service_type,
            service.server_id, service.endpoint_url, service.api_version,
            service.wsdl_url, service.description, service_id
        )
        
        cursor.execute(query, values)
        connection.commit()
        
        cursor.close()
        connection.close()
        
        logger.info(f"Updated security service: {service.service_code}")
        return {"message": "Security service updated successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating security service: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/security-service/{service_id}")
async def delete_security_service(service_id: int):
    """Delete a security service"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Get service info before deletion
        cursor.execute("SELECT service_code FROM security_service WHERE id = %s", (service_id,))
        result = cursor.fetchone()
        if not result:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="Security service not found")
        
        service_code = result.get('service_code') if isinstance(result, dict) else result[0]
        
        # Delete the service
        cursor.execute("DELETE FROM security_service WHERE id = %s", (service_id,))
        connection.commit()
        
        cursor.close()
        connection.close()
        
        logger.info(f"Deleted security service: {service_code}")
        return {"message": "Security service deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting security service: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================== My Applications Management =====================

@app.post("/api/my-application")
async def create_my_application(app: MyApplication):
    """Create a new application"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if network exists
        cursor.execute("SELECT id FROM network_config WHERE id = %s", (app.network_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="Network configuration not found")
        
        # Check if entity exists (if provided)
        if app.entity_id:
            cursor.execute("SELECT id FROM entity_owner WHERE id = %s", (app.entity_id,))
            if not cursor.fetchone():
                cursor.close()
                connection.close()
                raise HTTPException(status_code=404, detail="Entity not found")
        
        # Insert application
        query = """INSERT INTO my_applications (
            app_code, app_name, description, app_type, entity_id, network_id,
            host, port, protocol, version, status, environment,
            administrator, admin_email, admin_phone, certificate_path,
            registration_date
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        
        values = (
            app.app_code, app.app_name, app.description, app.app_type,
            app.entity_id, app.network_id, app.host, app.port, app.protocol,
            app.version, app.status, app.environment, app.administrator,
            app.admin_email, app.admin_phone, app.certificate_path, datetime.now()
        )
        
        cursor.execute(query, values)
        connection.commit()
        app_id = cursor.lastrowid
        
        cursor.close()
        connection.close()
        
        logger.info(f"Created application: {app.app_code}")
        return {"id": app_id, "message": "Application created successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating application: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/my-application")
async def list_my_applications():
    """Get all applications"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = """SELECT 
            id, app_code, app_name, description, app_type, entity_id, network_id,
            host, port, protocol, version, status, environment,
            administrator, admin_email, admin_phone, certificate_path,
            registration_date, created_at, updated_at
            FROM my_applications 
            ORDER BY app_code"""
        
        cursor.execute(query)
        applications = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        result = []
        for row in applications:
            if isinstance(row, dict):
                result.append(row)
            else:
                result.append({
                    "id": row[0], "app_code": row[1], "app_name": row[2], "description": row[3],
                    "app_type": row[4], "entity_id": row[5], "network_id": row[6],
                    "host": row[7], "port": row[8], "protocol": row[9], "version": row[10],
                    "status": row[11], "environment": row[12], "administrator": row[13],
                    "admin_email": row[14], "admin_phone": row[15], "certificate_path": row[16],
                    "registration_date": str(row[17]), "created_at": str(row[18]), "updated_at": str(row[19])
                })
        
        logger.info(f"Retrieved {len(result)} applications")
        return result
    
    except Exception as e:
        logger.error(f"Error retrieving applications: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/my-application/{app_id}")
async def get_my_application(app_id: int):
    """Get a specific application"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("""SELECT 
            id, app_code, app_name, description, app_type, entity_id, network_id,
            host, port, protocol, version, status, environment,
            administrator, admin_email, admin_phone, certificate_path,
            registration_date, created_at, updated_at
            FROM my_applications WHERE id = %s""", (app_id,))
        
        application = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        if isinstance(application, dict):
            return application
        else:
            return {
                "id": application[0], "app_code": application[1], "app_name": application[2],
                "description": application[3], "app_type": application[4], "entity_id": application[5],
                "network_id": application[6], "host": application[7], "port": application[8],
                "protocol": application[9], "version": application[10], "status": application[11],
                "environment": application[12], "administrator": application[13],
                "admin_email": application[14], "admin_phone": application[15],
                "certificate_path": application[16], "registration_date": str(application[17]),
                "created_at": str(application[18]), "updated_at": str(application[19])
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving application: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/my-application/{app_id}")
async def update_my_application(app_id: int, app: MyApplication):
    """Update an application"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("SELECT id FROM my_applications WHERE id = %s", (app_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="Application not found")
        
        query = """UPDATE my_applications SET 
            app_code = %s, app_name = %s, description = %s, entity_id = %s,
            network_id = %s, host = %s, port = %s, protocol = %s, version = %s,
            status = %s, environment = %s, administrator = %s, admin_email = %s,
            admin_phone = %s, certificate_path = %s
            WHERE id = %s"""
        
        values = (
            app.app_code, app.app_name, app.description, app.entity_id,
            app.network_id, app.host, app.port, app.protocol, app.version,
            app.status, app.environment, app.administrator, app.admin_email,
            app.admin_phone, app.certificate_path, app_id
        )
        
        cursor.execute(query, values)
        connection.commit()
        
        cursor.close()
        connection.close()
        
        logger.info(f"Updated application: {app.app_code}")
        return {"message": "Application updated successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating application: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/my-application/{app_id}")
async def delete_my_application(app_id: int):
    """Delete an application"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("SELECT app_code FROM my_applications WHERE id = %s", (app_id,))
        result = cursor.fetchone()
        if not result:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="Application not found")
        
        app_code = result.get('app_code') if isinstance(result, dict) else result[0]
        
        # Delete associated services first (foreign key cascade)
        cursor.execute("DELETE FROM my_services WHERE app_id = %s", (app_id,))
        
        # Delete the application
        cursor.execute("DELETE FROM my_applications WHERE id = %s", (app_id,))
        connection.commit()
        
        cursor.close()
        connection.close()
        
        logger.info(f"Deleted application: {app_code}")
        return {"message": "Application deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting application: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================== My Services Management =====================

@app.post("/api/my-service")
async def create_my_service(service: MyService):
    """Create a new service"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if application exists
        cursor.execute("SELECT id FROM my_applications WHERE id = %s", (service.app_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Insert service
        query = """INSERT INTO my_services (
            service_code, service_name, description, app_id, service_type,
            method, endpoint_path, full_url, api_version, timeout,
            retry_count, status, is_public
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        
        values = (
            service.service_code, service.service_name, service.description,
            service.app_id, service.service_type, service.method,
            service.endpoint_path, service.full_url, service.api_version,
            service.timeout, service.retry_count, service.status, service.is_public
        )
        
        cursor.execute(query, values)
        connection.commit()
        service_id = cursor.lastrowid
        
        cursor.close()
        connection.close()
        
        logger.info(f"Created service: {service.service_code}")
        return {"id": service_id, "message": "Service created successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating service: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/my-service")
async def list_my_services():
    """Get all services"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = """SELECT 
            id, service_code, service_name, description, app_id, service_type,
            method, endpoint_path, full_url, api_version, timeout,
            retry_count, status, is_public, created_at, updated_at
            FROM my_services 
            ORDER BY service_code"""
        
        cursor.execute(query)
        services = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        result = []
        for row in services:
            if isinstance(row, dict):
                result.append(row)
            else:
                result.append({
                    "id": row[0], "service_code": row[1], "service_name": row[2],
                    "description": row[3], "app_id": row[4], "service_type": row[5],
                    "method": row[6], "endpoint_path": row[7], "full_url": row[8],
                    "api_version": row[9], "timeout": row[10], "retry_count": row[11],
                    "status": row[12], "is_public": row[13], "created_at": str(row[14]),
                    "updated_at": str(row[15])
                })
        
        logger.info(f"Retrieved {len(result)} services")
        return result
    
    except Exception as e:
        logger.error(f"Error retrieving services: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/my-service/{service_id}")
async def get_my_service(service_id: int):
    """Get a specific service"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("""SELECT 
            id, service_code, service_name, description, app_id, service_type,
            method, endpoint_path, full_url, api_version, timeout,
            retry_count, status, is_public, created_at, updated_at
            FROM my_services WHERE id = %s""", (service_id,))
        
        service = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        if isinstance(service, dict):
            return service
        else:
            return {
                "id": service[0], "service_code": service[1], "service_name": service[2],
                "description": service[3], "app_id": service[4], "service_type": service[5],
                "method": service[6], "endpoint_path": service[7], "full_url": service[8],
                "api_version": service[9], "timeout": service[10], "retry_count": service[11],
                "status": service[12], "is_public": service[13], "created_at": str(service[14]),
                "updated_at": str(service[15])
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving service: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/my-service/{service_id}")
async def update_my_service(service_id: int, service: MyService):
    """Update a service"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("SELECT id FROM my_services WHERE id = %s", (service_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="Service not found")
        
        query = """UPDATE my_services SET 
            service_code = %s, service_name = %s, description = %s, app_id = %s,
            service_type = %s, method = %s, endpoint_path = %s, full_url = %s,
            api_version = %s, timeout = %s, retry_count = %s, status = %s,
            is_public = %s
            WHERE id = %s"""
        
        values = (
            service.service_code, service.service_name, service.description,
            service.app_id, service.service_type, service.method,
            service.endpoint_path, service.full_url, service.api_version,
            service.timeout, service.retry_count, service.status,
            service.is_public, service_id
        )
        
        cursor.execute(query, values)
        connection.commit()
        
        cursor.close()
        connection.close()
        
        logger.info(f"Updated service: {service.service_code}")
        return {"message": "Service updated successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating service: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/my-service/{service_id}")
async def delete_my_service(service_id: int):
    """Delete a service"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("SELECT service_code FROM my_services WHERE id = %s", (service_id,))
        result = cursor.fetchone()
        if not result:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="Service not found")
        
        service_code = result.get('service_code') if isinstance(result, dict) else result[0]
        
        cursor.execute("DELETE FROM my_services WHERE id = %s", (service_id,))
        connection.commit()
        
        cursor.close()
        connection.close()
        
        logger.info(f"Deleted service: {service_code}")
        return {"message": "Service deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting service: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================== Client Service Registry Management (External Services) =====================

@app.post("/api/client-service-registry")
async def create_client_service_registry(service: ClientServiceRegistry):
    """Create a new client service registry entry"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            INSERT INTO client_service_registry (
                ss_id, ss_name, ss_hostname, ss_ip, ss_port, ss_environment,
                entity_code, entity_name, app_code, app_name,
                service_code, service_name, service_type, method,
                endpoint_path, full_url, api_version, certificate,
                certificate_expiry, tls_enabled, timeout, retry_count,
                status, last_synced_at, source
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            service.ss_id, service.ss_name, service.ss_hostname, service.ss_ip,
            service.ss_port, service.ss_environment, service.entity_code,
            service.entity_name, service.app_code, service.app_name,
            service.service_code, service.service_name, service.service_type,
            service.method, service.endpoint_path, service.full_url,
            service.api_version, service.certificate, service.certificate_expiry,
            service.tls_enabled, service.timeout, service.retry_count,
            service.status, service.last_synced_at, service.source
        ))
        
        connection.commit()
        service_id = cursor.lastrowid
        
        cursor.close()
        connection.close()
        
        logger.info(f"Created client service registry: {service.service_code} from {service.ss_id}")
        return {"id": service_id, "message": "Client service registry created successfully"}
    
    except Exception as e:
        logger.error(f"Error creating client service registry: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/client-service-registry")
async def get_all_client_service_registry():
    """Get all client service registry entries"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("SELECT * FROM client_service_registry ORDER BY created_at DESC")
        result = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return result if result else []
    
    except Exception as e:
        logger.error(f"Error retrieving client service registry: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/client-service-registry/{service_id}")
async def get_client_service_registry(service_id: int):
    """Get a specific client service registry entry"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("SELECT * FROM client_service_registry WHERE id = %s", (service_id,))
        result = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Client service registry not found")
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving client service registry: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/client-service-registry/{service_id}")
async def update_client_service_registry(service_id: int, service: ClientServiceRegistry):
    """Update a client service registry entry"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("SELECT id FROM client_service_registry WHERE id = %s", (service_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="Client service registry not found")
        
        cursor.execute("""
            UPDATE client_service_registry SET
                ss_id = %s, ss_name = %s, ss_hostname = %s, ss_ip = %s,
                ss_port = %s, ss_environment = %s, entity_code = %s, entity_name = %s,
                app_code = %s, app_name = %s, service_code = %s, service_name = %s,
                service_type = %s, method = %s, endpoint_path = %s, full_url = %s,
                api_version = %s, certificate = %s, certificate_expiry = %s,
                tls_enabled = %s, timeout = %s, retry_count = %s,
                status = %s, last_synced_at = %s, source = %s
            WHERE id = %s
        """, (
            service.ss_id, service.ss_name, service.ss_hostname, service.ss_ip,
            service.ss_port, service.ss_environment, service.entity_code,
            service.entity_name, service.app_code, service.app_name,
            service.service_code, service.service_name, service.service_type,
            service.method, service.endpoint_path, service.full_url,
            service.api_version, service.certificate, service.certificate_expiry,
            service.tls_enabled, service.timeout, service.retry_count,
            service.status, service.last_synced_at, service.source, service_id
        ))
        
        connection.commit()
        
        cursor.close()
        connection.close()
        
        logger.info(f"Updated client service registry: {service.service_code} from {service.ss_id}")
        return {"message": "Client service registry updated successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating client service registry: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/client-service-registry/{service_id}")
async def delete_client_service_registry(service_id: int):
    """Delete a client service registry entry"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("SELECT service_code, ss_id FROM client_service_registry WHERE id = %s", (service_id,))
        result = cursor.fetchone()
        if not result:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="Client service registry not found")
        
        service_code = result.get('service_code') if isinstance(result, dict) else result[0]
        ss_id = result.get('ss_id') if isinstance(result, dict) else result[1]
        
        cursor.execute("DELETE FROM client_service_registry WHERE id = %s", (service_id,))
        connection.commit()
        
        cursor.close()
        connection.close()
        
        logger.info(f"Deleted client service registry: {service_code} from {ss_id}")
        return {"message": "Client service registry deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting client service registry: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================== IM Gateway - Service Discovery =====================

@app.get("/api/im/services")
def im_available_services():
    """
    Returns all services available to client applications on this gateway.
    App1 calls this to discover what service_codes it can use.
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT service_code, service_name, service_type, method,
               entity_name, app_name, full_url, status, source, last_synced_at
        FROM client_service_registry
        WHERE status = 'ACTIVE'
        ORDER BY service_code
    """)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    services = []
    for row in rows:
        r = row if isinstance(row, dict) else {}
        services.append({
            "service_code":  r.get("service_code"),
            "service_name":  r.get("service_name"),
            "type":          r.get("service_type"),
            "method":        r.get("method"),
            "provider_entity": r.get("entity_name"),
            "provider_app":    r.get("app_name"),
            "status":        r.get("status"),
            "source":        r.get("source"),
            "how_to_call":   f"GET /api/im/request  |  header: X-IM-Service: {r.get('service_code')}"
        })

    return {
        "gateway": db_config.get("database", "unknown"),
        "total_services": len(services),
        "services": services
    }


# ===================== IM Gateway - Request & Forward =====================

@app.api_route("/api/im/request", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def im_gateway_request(request: Request):
    """
    IM Gateway - Requestor side (called by the client application, e.g. App1).

    Flow: App1 → [this endpoint on SS1] → SS2 /api/im/forward → App2

    Required header:  X-IM-Service: <service_code>
    OR query param:   ?service_code=<service_code>
    """
    service_code = (
        request.headers.get("X-IM-Service")
        or request.query_params.get("service_code")
    )
    if not service_code:
        raise HTTPException(
            status_code=400,
            detail="X-IM-Service header or service_code query param is required"
        )

    # Look up the service in client_service_registry
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM client_service_registry WHERE service_code = %s LIMIT 1",
        (service_code,)
    )
    svc = cursor.fetchone()
    cursor.close()
    connection.close()

    if not svc:
        raise HTTPException(
            status_code=404,
            detail=f"Service '{service_code}' not found in registry. "
                   "Please register the service or sync from Global Server first."
        )

    # Determine the provider Security Server's address
    ss_ip       = svc.get("ss_ip")       if isinstance(svc, dict) else None
    ss_hostname = svc.get("ss_hostname") if isinstance(svc, dict) else None
    ss_port     = svc.get("ss_port")     if isinstance(svc, dict) else None

    target_host = ss_ip or ss_hostname
    if not target_host or not ss_port:
        raise HTTPException(
            status_code=400,
            detail=f"Provider Security Server address not configured for '{service_code}'. "
                   "Set ss_ip/ss_hostname and ss_port in the client service registry."
        )

    request_id   = request.headers.get("X-IM-Request-Id", str(uuid.uuid4()))
    forward_url  = f"http://{target_host}:{ss_port}/api/im/forward"
    body         = await request.body()

    forward_headers = {
        "X-IM-Service":    service_code,
        "X-IM-Client":     db_config.get("database", "SECURITY_SERVER"),
        "X-IM-Request-Id": request_id,
        "Content-Type":    request.headers.get("Content-Type", "application/json"),
    }

    logger.info(f"[IM-REQUEST] service='{service_code}' → {forward_url} (req-id={request_id})")

    try:
        resp = requests.request(
            method=request.method,
            url=forward_url,
            params={"service_code": service_code},
            data=body or None,
            headers=forward_headers,
            timeout=30
        )
        logger.info(f"[IM-REQUEST] provider responded {resp.status_code}")
        try:
            return JSONResponse(content=resp.json(), status_code=resp.status_code)
        except Exception:
            return JSONResponse(content={"raw": resp.text}, status_code=resp.status_code)

    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail=f"Cannot connect to provider Security Server at {target_host}:{ss_port}"
        )
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Provider Security Server timed out")


@app.api_route("/api/im/forward", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def im_gateway_forward(request: Request):
    """
    IM Gateway - Provider side (called by the requester Security Server, e.g. SS1).

    Flow: SS1 → [this endpoint on SS2] → App2

    Required query param or header: service_code / X-IM-Service
    """
    service_code = (
        request.query_params.get("service_code")
        or request.headers.get("X-IM-Service")
    )
    if not service_code:
        raise HTTPException(
            status_code=400,
            detail="service_code query param or X-IM-Service header is required"
        )

    # Look up the service in the local my_services table
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM my_services WHERE service_code = %s AND status = 'ACTIVE' LIMIT 1",
        (service_code,)
    )
    svc = cursor.fetchone()
    cursor.close()
    connection.close()

    if not svc:
        raise HTTPException(
            status_code=404,
            detail=f"Service '{service_code}' not found in local service registry."
        )

    service_url    = svc.get("full_url")  if isinstance(svc, dict) else None
    service_method = svc.get("method", "GET") if isinstance(svc, dict) else "GET"

    if not service_url:
        raise HTTPException(
            status_code=400,
            detail=f"No URL configured for service '{service_code}'. Set full_url in my_services."
        )

    request_id = request.headers.get("X-IM-Request-Id", str(uuid.uuid4()))
    body       = await request.body()

    logger.info(f"[IM-FORWARD] service='{service_code}' → {service_url} (req-id={request_id})")

    try:
        resp = requests.request(
            method=service_method,
            url=service_url,
            data=body or None,
            headers={
                "Content-Type":    "application/json",
                "X-IM-Request-Id": request_id,
            },
            timeout=30
        )
        logger.info(f"[IM-FORWARD] app responded {resp.status_code}")
        try:
            return JSONResponse(content=resp.json(), status_code=resp.status_code)
        except Exception:
            return JSONResponse(content={"raw": resp.text}, status_code=resp.status_code)

    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail=f"Cannot connect to service application at {service_url}"
        )
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Service application timed out")


# ===================== Sync Global Services =====================

@app.post("/api/sync-global-services")
async def sync_global_services(request_data: dict):
    """Fetch all services from the Global Server and upsert into client_service_registry"""
    global_server_url = request_data.get("global_server_url", "").rstrip("/")
    if not global_server_url:
        raise HTTPException(status_code=400, detail="global_server_url is required")

    try:
        response = requests.get(f"{global_server_url}/api/global-service-register", timeout=10)
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail=f"Global server returned {response.status_code}: {response.text}")
        services = response.json()
        if not isinstance(services, list):
            raise HTTPException(status_code=502, detail="Unexpected response format from Global Server")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Cannot connect to Global Server. Check the URL and ensure it is running.")
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Global Server connection timed out")

    connection = get_db_connection()
    cursor = connection.cursor()
    now = datetime.now().isoformat()
    synced = 0
    updated = 0

    for svc in services:
        ss_id = svc.get("server_title") or str(svc.get("security_server_id", "GLOBAL"))
        service_code = svc.get("service_code", "")
        if not service_code:
            continue

        cursor.execute(
            "SELECT id FROM client_service_registry WHERE service_code = %s AND source = 'GLOBAL_SERVER'",
            (service_code,)
        )
        existing = cursor.fetchone()

        # Network info for the provider Security Server (SS2)
        ss_ip_val = svc.get("ss_ip") or svc.get("ss_host") or ""
        ss_port_val = svc.get("ss_port") or None
        ss_hostname_val = svc.get("ss_hostname") or ""
        ss_name_val = svc.get("server_title") or ss_id

        if existing:
            existing_id = existing.get("id") if isinstance(existing, dict) else existing[0]
            cursor.execute("""
                UPDATE client_service_registry SET
                    ss_id = %s, ss_name = %s, ss_hostname = %s, ss_ip = %s, ss_port = %s,
                    entity_code = %s, entity_name = %s,
                    app_code = %s, app_name = %s,
                    service_name = %s, service_type = %s, method = %s,
                    endpoint_path = %s, full_url = %s, api_version = %s,
                    status = %s, last_synced_at = %s
                WHERE id = %s
            """, (
                ss_id, ss_name_val, ss_hostname_val, ss_ip_val, ss_port_val,
                svc.get("entity_code", ""), svc.get("entity_name", ""),
                svc.get("subsystem_code", ""), svc.get("subsystem_name", ""),
                svc.get("service_name", ""), svc.get("protocol", "REST"),
                svc.get("http_method", "GET"),
                svc.get("service_url", ""), svc.get("service_url", ""),
                svc.get("service_version", "v1.0"),
                svc.get("status", "ACTIVE"), now,
                existing_id
            ))
            updated += 1
        else:
            cursor.execute("""
                INSERT INTO client_service_registry (
                    ss_id, ss_name, ss_hostname, ss_ip, ss_port,
                    entity_code, entity_name, app_code, app_name,
                    service_code, service_name, service_type, method,
                    endpoint_path, full_url, api_version,
                    status, last_synced_at, source
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                ss_id, ss_name_val, ss_hostname_val, ss_ip_val, ss_port_val,
                svc.get("entity_code", ""), svc.get("entity_name", ""),
                svc.get("subsystem_code", ""), svc.get("subsystem_name", ""),
                service_code, svc.get("service_name", ""),
                svc.get("protocol", "REST"), svc.get("http_method", "GET"),
                svc.get("service_url", ""), svc.get("service_url", ""),
                svc.get("service_version", "v1.0"),
                svc.get("status", "ACTIVE"), now, "GLOBAL_SERVER"
            ))
            synced += 1

    connection.commit()
    cursor.close()
    connection.close()

    logger.info(f"Global sync complete: {synced} new, {updated} updated")
    return {
        "status": "success",
        "message": f"Sync complete: {synced} new service(s) added, {updated} existing service(s) updated.",
        "new": synced,
        "updated": updated,
        "total": synced + updated
    }


# ===================== Startup Event =====================

@app.on_event("startup")
async def startup_event():
    """Initialize required tables on app startup"""
    try:
        ensure_global_server_table_exists()
        logger.info("Application startup complete")
    except Exception as e:
        logger.warning(f"Warning during startup: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    import argparse

    parser = argparse.ArgumentParser(description="Security Server (IM Gateway)")
    parser.add_argument("--port",   type=int, default=8000,        help="Port to listen on (default: 8000)")
    parser.add_argument("--host",   type=str, default="0.0.0.0",   help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--config", type=str, default=None,        help="Path to db_config.json (default: same dir as this script)")
    args = parser.parse_args()

    # Allow overriding the config file at startup
    if args.config:
        CONFIG_FILE = args.config
        load_db_config_from_file()

    print("=" * 60)
    print(f"  Security Server  |  db: {db_config.get('database', 'not configured')}")
    print(f"  http://{args.host}:{args.port}")
    print(f"  Docs: http://localhost:{args.port}/docs")
    print("=" * 60)

    uvicorn.run(app, host=args.host, port=args.port)
