-- MySQL dump 10.13  Distrib 8.0.28, for Win64 (x86_64)
--
-- Host: localhost    Database: gateway1
-- ------------------------------------------------------
-- Server version	8.0.28

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `client_service_registry`
--

DROP TABLE IF EXISTS `client_service_registry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `client_service_registry` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ss_id` varchar(100) NOT NULL,
  `ss_name` varchar(255) DEFAULT NULL,
  `ss_hostname` varchar(255) DEFAULT NULL,
  `ss_ip` varchar(50) DEFAULT NULL,
  `ss_port` int DEFAULT NULL,
  `ss_environment` varchar(50) DEFAULT NULL,
  `entity_code` varchar(100) DEFAULT NULL,
  `entity_name` varchar(255) DEFAULT NULL,
  `app_code` varchar(100) DEFAULT NULL,
  `app_name` varchar(255) DEFAULT NULL,
  `service_code` varchar(100) NOT NULL,
  `service_name` varchar(255) DEFAULT NULL,
  `service_type` varchar(50) DEFAULT NULL,
  `method` varchar(20) DEFAULT NULL,
  `endpoint_path` varchar(255) DEFAULT NULL,
  `full_url` text,
  `api_version` varchar(50) DEFAULT NULL,
  `certificate` text,
  `certificate_expiry` datetime DEFAULT NULL,
  `tls_enabled` tinyint(1) DEFAULT '1',
  `timeout` int DEFAULT '30',
  `retry_count` int DEFAULT '3',
  `status` varchar(50) DEFAULT 'ACTIVE',
  `last_synced_at` datetime DEFAULT NULL,
  `source` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_service` (`ss_id`,`app_code`,`service_code`,`api_version`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `client_service_registry`
--

LOCK TABLES `client_service_registry` WRITE;
/*!40000 ALTER TABLE `client_service_registry` DISABLE KEYS */;
INSERT INTO `client_service_registry` VALUES (1,'Test Security Gateway','Test Security Gateway',NULL,NULL,NULL,NULL,'ENTITY02','Apcog','HR','Human Resource System','XT220MFH7E','hello world','HTTP','GET','http://106.51.108.71:9090/app2/health','http://106.51.108.71:9090/app2/health','v1',NULL,NULL,1,30,3,'ACTIVE','2026-06-16 09:21:52','GLOBAL_SERVER','2026-06-16 03:51:52','2026-06-16 03:51:52'),(2,'Test Security Gateway','Test Security Gateway',NULL,NULL,NULL,NULL,'TEST_ORG','Test Organization','AXT569AE49','HR','getEmployee2','Get Employee Details','HTTP','GET','HTTP://localhost:5000/api/get/employee','HTTP://localhost:5000/api/get/employee','v1',NULL,NULL,1,30,3,'ACTIVE','2026-06-16 09:21:52','GLOBAL_SERVER','2026-06-16 03:51:52','2026-06-16 03:51:52'),(3,'Test Security Gateway','Test Security Gateway',NULL,NULL,NULL,NULL,'TEST_ORG','Test Organization','AXT569AE49','HR','getEmployee','Get Employee Details','REST','GET','http://hr-service/api/employee','http://hr-service/api/employee','v1',NULL,NULL,1,30,3,'ACTIVE','2026-06-16 09:21:52','GLOBAL_SERVER','2026-06-16 03:51:52','2026-06-16 03:51:52');
/*!40000 ALTER TABLE `client_service_registry` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `entity_owner`
--

DROP TABLE IF EXISTS `entity_owner`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `entity_owner` (
  `id` int NOT NULL AUTO_INCREMENT,
  `entity_code` varchar(100) NOT NULL,
  `entity_name` varchar(255) NOT NULL,
  `contact_person` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `phone` varchar(50) DEFAULT NULL,
  `address` text,
  `country` varchar(100) DEFAULT NULL,
  `state` varchar(100) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `entity_code` (`entity_code`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `entity_owner`
--

LOCK TABLES `entity_owner` WRITE;
/*!40000 ALTER TABLE `entity_owner` DISABLE KEYS */;
INSERT INTO `entity_owner` VALUES (1,'ORG_001','APCOG','Mohammed Sahqiue','msahique@apcogsys.net','8880655678','APCOGSYS, jayanagar 9th block, bangalore , India','India','Karnataka','Bangalore','2026-04-03 03:24:17','2026-04-03 03:33:30');
/*!40000 ALTER TABLE `entity_owner` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `global_server_config`
--

DROP TABLE IF EXISTS `global_server_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `global_server_config` (
  `id` int NOT NULL AUTO_INCREMENT,
  `server_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `server_url` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `api_key` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `server_name` (`server_name`),
  KEY `idx_server_url` (`server_url`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `global_server_config`
--

LOCK TABLES `global_server_config` WRITE;
/*!40000 ALTER TABLE `global_server_config` DISABLE KEYS */;
INSERT INTO `global_server_config` VALUES (1,'global server 1','127.0.0.1:9000',NULL,'this is the test global server','2026-04-10 06:29:31','2026-04-10 06:29:31');
/*!40000 ALTER TABLE `global_server_config` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `my_applications`
--

DROP TABLE IF EXISTS `my_applications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `my_applications` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_code` varchar(100) NOT NULL,
  `app_name` varchar(255) NOT NULL,
  `description` text,
  `app_type` varchar(50) NOT NULL DEFAULT 'APPLICATION',
  `entity_id` int DEFAULT NULL,
  `network_id` varchar(100) NOT NULL,
  `host` varchar(100) DEFAULT NULL,
  `port` int DEFAULT NULL,
  `protocol` varchar(20) DEFAULT NULL,
  `version` varchar(50) DEFAULT NULL,
  `status` varchar(50) DEFAULT 'PENDING',
  `environment` varchar(50) DEFAULT NULL,
  `administrator` varchar(255) DEFAULT NULL,
  `admin_email` varchar(255) DEFAULT NULL,
  `admin_phone` varchar(50) DEFAULT NULL,
  `certificate_path` text,
  `certificate_expiry` datetime DEFAULT NULL,
  `registration_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `last_health_check` datetime DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `app_code` (`app_code`),
  KEY `entity_id` (`entity_id`),
  KEY `network_id` (`network_id`),
  CONSTRAINT `my_applications_ibfk_1` FOREIGN KEY (`entity_id`) REFERENCES `entity_owner` (`id`) ON DELETE SET NULL,
  CONSTRAINT `my_applications_ibfk_2` FOREIGN KEY (`network_id`) REFERENCES `network_config` (`id`) ON DELETE CASCADE,
  CONSTRAINT `my_applications_chk_1` CHECK ((`app_type` = _utf8mb4'APPLICATION'))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `my_applications`
--

LOCK TABLES `my_applications` WRITE;
/*!40000 ALTER TABLE `my_applications` DISABLE KEYS */;
INSERT INTO `my_applications` VALUES (1,'APP_001','TSA','Application that provides universal time.','APPLICATION',NULL,'ss1','127.0.0.1',7000,'HTTPS','1.0','ACTIVE','DEV','Sahique','msahique@apcosys.net','8880655655',NULL,NULL,'2026-04-03 15:51:19',NULL,'2026-04-03 10:21:18','2026-04-03 10:21:18');
/*!40000 ALTER TABLE `my_applications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `my_services`
--

DROP TABLE IF EXISTS `my_services`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `my_services` (
  `id` int NOT NULL AUTO_INCREMENT,
  `service_code` varchar(100) NOT NULL,
  `service_name` varchar(255) NOT NULL,
  `description` text,
  `app_id` int NOT NULL,
  `service_type` varchar(50) DEFAULT 'REST',
  `method` varchar(20) DEFAULT NULL,
  `endpoint_path` varchar(255) NOT NULL,
  `full_url` text,
  `api_version` varchar(50) DEFAULT NULL,
  `timeout` int DEFAULT '30',
  `retry_count` int DEFAULT '3',
  `status` varchar(50) DEFAULT 'ACTIVE',
  `is_public` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `service_code` (`service_code`),
  KEY `app_id` (`app_id`),
  CONSTRAINT `my_services_ibfk_1` FOREIGN KEY (`app_id`) REFERENCES `my_applications` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `my_services`
--

LOCK TABLES `my_services` WRITE;
/*!40000 ALTER TABLE `my_services` DISABLE KEYS */;
INSERT INTO `my_services` VALUES (1,'SVC_001','Getuniversal Time','This service end point gives the universal time for the client that uses this endpoint.  ',1,'REST','GET','/api/get_universal_time','http://127.0.0.1:7000/api/get_universal_time','v1.0',30,3,'ACTIVE',1,'2026-04-03 10:28:49','2026-04-03 10:28:49');
/*!40000 ALTER TABLE `my_services` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `network_config`
--

DROP TABLE IF EXISTS `network_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `network_config` (
  `id` varchar(100) NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `version` varchar(50) DEFAULT NULL,
  `network_instance` varchar(100) DEFAULT NULL,
  `gateway_code` varchar(100) DEFAULT NULL,
  `entity_id` int DEFAULT NULL,
  `host` varchar(100) DEFAULT NULL,
  `port` int DEFAULT NULL,
  `hostname` varchar(255) DEFAULT NULL,
  `ip_address` varchar(50) DEFAULT NULL,
  `environment` varchar(50) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_network_entity_id` (`entity_id`),
  KEY `idx_network_env` (`environment`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `network_config`
--

LOCK TABLES `network_config` WRITE;
/*!40000 ALTER TABLE `network_config` DISABLE KEYS */;
INSERT INTO `network_config` VALUES ('ss1','SS1','1.0','1','GW_001',1,'127.0.0.1',8000,'gateway.local','127.0.0.1','TEST','2026-04-03 02:49:04','2026-04-03 02:49:29');
/*!40000 ALTER TABLE `network_config` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-06-16  9:45:10
