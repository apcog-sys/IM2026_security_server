-- Create Database
CREATE DATABASE IF NOT EXISTS gateway1;

-- Use Database
USE gateway1;

-- 🟢 Table: network_config (REGISTER FIRST)
CREATE TABLE IF NOT EXISTS network_config (
    id VARCHAR(100) PRIMARY KEY,           -- SECURITY_SERVER_1
    title VARCHAR(255),
    version VARCHAR(50),
    network_instance VARCHAR(100),
    gateway_code VARCHAR(100) UNIQUE,

    entity_id INT NULL,                    -- Will be updated later

    host VARCHAR(100),
    port INT,
    hostname VARCHAR(255),
    ip_address VARCHAR(50),

    environment VARCHAR(50),

    status VARCHAR(50) DEFAULT 'PENDING',  -- PENDING until entity linked

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 🟢 Table: entity_owner (REGISTER LATER)
CREATE TABLE IF NOT EXISTS entity_owner (
    id INT AUTO_INCREMENT PRIMARY KEY,

    entity_code VARCHAR(100) NOT NULL UNIQUE,
    entity_name VARCHAR(255) NOT NULL,

    contact_person VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),

    address TEXT,

    country VARCHAR(100),
    state VARCHAR(100),
    city VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 🟢 Table: security_server (Security Servers/Applications/Services)
CREATE TABLE IF NOT EXISTS security_server (
    id INT AUTO_INCREMENT PRIMARY KEY,

    server_code VARCHAR(100) NOT NULL UNIQUE,
    server_name VARCHAR(255) NOT NULL,
    description TEXT,

    server_type VARCHAR(50) NOT NULL,        -- 'SECURITY_SERVER', 'APPLICATION', 'SERVICE'
    
    entity_id INT,                            -- Link to entity_owner
    network_id VARCHAR(100),                  -- Link to network_config
    
    host VARCHAR(100),
    port INT,
    protocol VARCHAR(20),                     -- 'HTTP', 'HTTPS', 'TCP', 'UDP'
    
    version VARCHAR(50),
    status VARCHAR(50) DEFAULT 'PENDING',    -- 'ACTIVE', 'INACTIVE', 'PENDING', 'MAINTENANCE'
    
    environment VARCHAR(50),                  -- 'DEV', 'TEST', 'PROD'
    
    administrator VARCHAR(255),
    admin_email VARCHAR(255),
    admin_phone VARCHAR(50),
    
    certificate_path TEXT,
    certificate_expiry DATETIME,
    
    registration_date DATETIME,
    last_health_check DATETIME,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (entity_id) REFERENCES entity_owner(id) ON DELETE SET NULL,
    FOREIGN KEY (network_id) REFERENCES network_config(id) ON DELETE SET NULL
);

-- 🟢 Table: security_service (Services provided by servers)
CREATE TABLE IF NOT EXISTS security_service (
    id INT AUTO_INCREMENT PRIMARY KEY,

    service_code VARCHAR(100) NOT NULL UNIQUE,
    service_name VARCHAR(255) NOT NULL,
    description TEXT,
    
    server_id INT NOT NULL,                  -- Link to security_server
    
    service_type VARCHAR(100),               -- e.g., 'X-ROAD', 'SIGNATURE', 'AUTHENTICATION', 'AUTHORIZATION'
    status VARCHAR(50) DEFAULT 'ACTIVE',
    
    endpoint_url TEXT,
    wsdl_url TEXT,
    api_version VARCHAR(50),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (server_id) REFERENCES security_server(id) ON DELETE CASCADE
);

-- 🟢 Table: client_service_registry (Fetched from Global Server)
CREATE TABLE IF NOT EXISTS client_service_registry (
    id INT AUTO_INCREMENT PRIMARY KEY,

    -- 🌐 Security Server Info
    ss_id VARCHAR(100) NOT NULL,              -- SECURITY_SERVER_1
    ss_name VARCHAR(255),
    ss_hostname VARCHAR(255),
    ss_ip VARCHAR(50),
    ss_port INT,
    ss_environment VARCHAR(50),

    -- 🏢 Entity / Owner Info
    entity_code VARCHAR(100),
    entity_name VARCHAR(255),

    -- 🧩 Application Info
    app_code VARCHAR(100),
    app_name VARCHAR(255),

    -- 🔌 Service Info
    service_code VARCHAR(100) NOT NULL,
    service_name VARCHAR(255),
    service_type VARCHAR(50),                 -- REST / SOAP
    method VARCHAR(20),                       -- GET / POST

    endpoint_path VARCHAR(255),
    full_url TEXT,

    api_version VARCHAR(50),

    -- 🔐 Security Info
    certificate TEXT,                         -- Public cert of remote SS
    certificate_expiry DATETIME,
    tls_enabled BOOLEAN DEFAULT TRUE,

    -- 🔁 Routing / Reliability
    timeout INT DEFAULT 30,
    retry_count INT DEFAULT 3,

    -- 📡 Status & Sync
    status VARCHAR(50) DEFAULT 'ACTIVE',      -- ACTIVE / INACTIVE
    last_synced_at DATETIME,
    source VARCHAR(100),                      -- GLOBAL_SERVER / MANUAL

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- 🔍 Unique constraint (VERY IMPORTANT)
    UNIQUE KEY unique_service (
        ss_id,
        app_code,
        service_code,
        api_version
    )
);

-- 🟢 Indexes
CREATE INDEX idx_network_entity_id ON network_config(entity_id);
CREATE INDEX idx_network_env ON network_config(environment);
CREATE INDEX idx_entity_code ON entity_owner(entity_code);
CREATE INDEX idx_server_entity ON security_server(entity_id);
CREATE INDEX idx_server_network ON security_server(network_id);
CREATE INDEX idx_server_type ON security_server(server_type);
CREATE INDEX idx_server_status ON security_server(status);
CREATE INDEX idx_service_server ON security_service(server_id);
CREATE INDEX idx_client_registry_ss ON client_service_registry(ss_id);
CREATE INDEX idx_client_registry_app ON client_service_registry(app_code);
CREATE INDEX idx_client_registry_service ON client_service_registry(service_code);
CREATE INDEX idx_client_registry_status ON client_service_registry(status);
CREATE INDEX idx_client_registry_source ON client_service_registry(source);
