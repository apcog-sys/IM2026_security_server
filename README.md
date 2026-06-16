# System Configuration Management API

A FastAPI-based web application for managing system configurations including database and network settings.

## Features

- **Database Configuration Management**
  - Test database connections
  - Save and retrieve DB configuration locally
  - Persistent storage in `db_config.json`

- **Network Configuration CRUD Operations**
  - Create, read, update, and delete network configurations
  - Store in MySQL database via `network_config` table
  - Real-time updates with timestamps

- **Interactive Web UI**
  - Tab-based interface for System Configuration
  - DB Configuration panel
  - Network Configuration management with table view
  - Modal forms for adding/editing configurations

- **RESTful API**
  - Complete CRUD endpoints for network configurations
  - DB connection management endpoints
  - Health check endpoint

## Prerequisites

- Python 3.8 or higher
- MySQL Server running locally or accessible via network
- pip (Python package manager)

## Installation

1. Clone or download the project files

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Create the MySQL database and table (run this on your MySQL server):
```sql
-- Create Database
CREATE DATABASE IF NOT EXISTS gateway1;

-- Use Database
USE gateway1;

-- Create Table: network_config
CREATE TABLE network_config (
    id VARCHAR(100) PRIMARY KEY,           -- SECURITY_SERVER_1
    title VARCHAR(255),                    -- Security Server 1
    version VARCHAR(50),                   -- 1.0.0
    network_instance VARCHAR(100),         -- default
    gateway_code VARCHAR(100),             -- GW_001
    entity_id INT,                         -- 1

    host VARCHAR(100),                     -- 127.0.0.1
    port INT,                              -- 9001
    hostname VARCHAR(255),                 -- security-gateway.federated.local
    ip_address VARCHAR(50),                -- 10.0.0.50

    environment VARCHAR(50),               -- PROD

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

## Running the Application

Start the FastAPI server:
```bash
python ss1.py
```

The application will start on `http://localhost:8000`

## Usage

### Web Interface
1. Open browser and go to `http://localhost:8000/`
2. **DB Configuration Tab:**
   - Enter your MySQL connection details
   - Click "Test Connection" to verify connectivity
   - Click "Save Configuration" to store credentials locally
3. **Network Configuration Tab:**
   - View all network configurations in table
   - Click "+ Add New Network Config" to create new entry
   - Click "Edit" to modify existing configurations
   - Click "Delete" to remove configurations

### API Endpoints

#### Database Configuration
- `POST /api/db/test-connection` - Test database connection
- `POST /api/db/save-config` - Save database configuration
- `GET /api/db/get-config` - Get current database configuration

#### Network Configuration
- `GET /api/network` - List all network configurations
- `GET /api/network/{id}` - Get specific network configuration
- `POST /api/network` - Create new network configuration
- `PUT /api/network/{id}` - Update existing network configuration
- `DELETE /api/network/{id}` - Delete network configuration

#### System
- `GET /api/health` - Health check
- `GET /api/docs` - Interactive API documentation (Swagger UI)
- `GET /api/redoc` - ReDoc API documentation

## Configuration Storage

- **Database Config**: Stored locally in `db_config.json`
- **Network Config**: Stored in MySQL `network_config` table

## Example Requests

### Test DB Connection
```bash
curl -X POST "http://localhost:8000/api/db/test-connection" \
  -H "Content-Type: application/json" \
  -d '{
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "password",
    "database": "gateway1"
  }'
```

### Create Network Configuration
```bash
curl -X POST "http://localhost:8000/api/network" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "SECURITY_SERVER_1",
    "title": "Security Server 1",
    "version": "1.0.0",
    "network_instance": "default",
    "gateway_code": "GW_001",
    "entity_id": 1,
    "host": "127.0.0.1",
    "port": 9001,
    "hostname": "security-gateway.federated.local",
    "ip_address": "10.0.0.50",
    "environment": "PROD"
  }'
```

### List All Network Configurations
```bash
curl "http://localhost:8000/api/network"
```

## File Structure

```
SS1/
├── ss1.py              # FastAPI application
├── index.html          # Web UI
├── requirements.txt    # Python dependencies
├── db_config.json      # Database configuration (auto-generated)
└── README.md           # This file
```

## Notes

- Database credentials are stored locally in `db_config.json` after configuration
- All timestamps are automatically managed by MySQL
- The application supports PROD, TEST, and DEV environments
- Network configuration IDs must be unique
- All API responses include proper HTTP status codes and error messages

## Troubleshooting

- **Connection refused error**: Ensure MySQL server is running on the specified host:port
- **Database not found**: Create the database and table as shown in Installation section
- **Module not found**: Run `pip install -r requirements.txt` again
- **Port already in use**: Change the port in `ss1.py` from 8000 to another available port

## API Documentation

Once the server is running, access interactive documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
