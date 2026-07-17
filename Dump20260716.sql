-- MySQL dump 10.13  Distrib 8.0.28, for Win64 (x86_64)
--
-- Host: localhost    Database: sgateway_sg1_db
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
-- Table structure for table `sg_application`
--

DROP TABLE IF EXISTS `sg_application`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sg_application` (
  `id` int NOT NULL AUTO_INCREMENT,
  `instance` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `entity_class` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `entity_code` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `application_code` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `sign_cert_pem` text COLLATE utf8mb4_unicode_ci,
  `sign_key_pem` text COLLATE utf8mb4_unicode_ci,
  `sign_serial` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `entity_class` (`entity_class`,`entity_code`,`application_code`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sg_application`
--

LOCK TABLES `sg_application` WRITE;
/*!40000 ALTER TABLE `sg_application` DISABLE KEYS */;
INSERT INTO `sg_application` VALUES (1,'GOVSTACK','GOV','1001','consumer-app','-----BEGIN CERTIFICATE-----\nMIIDTjCCAjagAwIBAgIIBzx9S3m0NB0wDQYJKoZIhvcNAQELBQAwQTELMAkGA1UE\nBhMCRUUxHDAaBgNVBAMME0dvdlN0YWNrIElNIFJvb3QgQ0ExFDASBgNVBAoMC0dv\ndlN0YWNrIElNMB4XDTI2MDYyMzE3MjAxNVoXDTI4MDkyNTE3MjExNVowazELMAkG\nA1UEBhMCRUUxHzAdBgNVBAMMFjEwMDEvY29uc3VtZXItYXBwIHNpZ24xJDAiBgNV\nBAoMG01pbmlzdHJ5IG9mIERpZ2l0YWwgQWZmYWlyczEVMBMGA1UECwwMY29uc3Vt\nZXItYXBwMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAtVam3e/1jdyn\nVe6rc+mJB/5/3kjtY/I9i+ASKHRoyPLcPOw730tRNxvLi7hrFC2+fHb1JPXGYkz+\nRBXmTx5BMFhf+UIzuZ9SASuN6ke/L2t0rB49UG2+QmHZePBB7B7J4IvFJlttkkql\nRndLCg+rqHKu5SuWTzxhTFmT7stBn0MH78/OpKLOvg5KR7ckgc8KZSgkrmYSod40\nAemuDqtTNBKD+w4glpkp2W6WT9OIw/iS4fU+y79mfKupi5FI+5kSNWG0QYRWqBCo\neVOAsYiMb5uzY1LlCFZY6m8zO6ntL4bu8oDkj9W89n8Wp82i6ahGvv2BIJuVR96t\nJwzvpdBuFwIDAQABoyAwHjAMBgNVHRMBAf8EAjAAMA4GA1UdDwEB/wQEAwIGwDAN\nBgkqhkiG9w0BAQsFAAOCAQEAAsgSENq5Eq9nBVnZxlFxeacgpnEwjj+t+Fz/kTQY\nuzlWoO4fhmz8kf1xDqdqunesaPiOmhorhSj1ggBO/YvQ56DY406t3Nu908+jiTE0\nn8jAyHXYj7X4utC/skrfU7QmsI1cwx9ulEKsHAOAqmTLKmU3gYLsiin8ZpVQwXIs\n/Nk7n4Uh0DLTq6wazcYG6fiCe8qz7vkE9+dZIn9O5Th4nzOD4ZofJUsKiDdGQkRD\n9pVFj5dIIPv93oFjoKCbYXu3svJVmn7fhg+1h60Ye7jy9D7uizAy9f1yJez8vo69\niA5LwmxlDiitUAqIZhTiXyvPc/9q8nevuiQrE9pTtItp1A==\n-----END CERTIFICATE-----\n','-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC1Vqbd7/WN3KdV\n7qtz6YkH/n/eSO1j8j2L4BIodGjI8tw87DvfS1E3G8uLuGsULb58dvUk9cZiTP5E\nFeZPHkEwWF/5QjO5n1IBK43qR78va3SsHj1Qbb5CYdl48EHsHsngi8UmW22SSqVG\nd0sKD6uocq7lK5ZPPGFMWZPuy0GfQwfvz86kos6+DkpHtySBzwplKCSuZhKh3jQB\n6a4Oq1M0EoP7DiCWmSnZbpZP04jD+JLh9T7Lv2Z8q6mLkUj7mRI1YbRBhFaoEKh5\nU4CxiIxvm7NjUuUIVljqbzM7qe0vhu7ygOSP1bz2fxanzaLpqEa+/YEgm5VH3q0n\nDO+l0G4XAgMBAAECggEADMQOjT3mVdf8eRfglBFoZzAAb8qcg6u7BMzVGmn6Mnip\nDn+Rm3T267VA4r4siPLLdSxUB7JnBpE7A9oIKPZin8pTlKhCHJrdsAgRPov8e+nJ\nqzrvFWlpundJqFzplyYiZMoSKqgcZ5m/rDKbuBfwUrR4IYQBrzml89+z2Admauqz\nfr13wqZnUJNxYpQs1kGSo0v+H2NQYP8EJ2HCco+Rd4tkxy7QGmuY/MCa/mD/n9J+\nbfNie5bOA2bGSbQg1LKWZmgl2TPmhI4Txnf8oPdGWyb34i/rhqujBbumYLPZGZpT\nrdHzIJhdTYH35viWO6HP45dTlgbpWEbjyGMNa0MJIQKBgQD3mcFLSPRXxvrbh5g5\nWl09IZI668v0BJBxJfohJvOW2QTGZz3c9WiYHQTHc9bNWcS/STHBBsZ38RFkVgg1\nmt8NclEZ1Wgj7wPUw0yDbTdaSebCNXJYMG2IHQm2lCEC1jzWZj/jUyViHSbnzZKC\nEsM9aUbqUNshPHIHEn8cE2eAJwKBgQC7fXRqYd5VbvXg57nj3H7UJtOg9UsQJu1o\nimlDFtgVVSSL4l6JSlAsp9mhC9FXQG6z//GA0ps3oRHJ7T/W+vVKyYuDD6no5kH7\n6LgLQJYcnO5Z203ufJ+ukIuGzru7+S4iFWI55Xj3OChBl5BFgSCVGn8OEjdqfYfC\nn1ZB5ndokQKBgCESpqEZw5md+JAuUoUGrwGlZFT+fiXAHlMe0YRwIYV6w4qE69yB\n41C+P48sx/pyDTfH3R99ejE3QC142Gvgnf670F11Bg4WtRpMZAICKqyixnIWlYl2\nHotZ5Zw/uREZ8NJqogoJZyrt3e6EpRc+zll7oH9YAY00974+GEB1zxNtAoGANfpk\nbcxHamlLuLh+OC/fA8052HlGZxwN9a8DpyEIjPu6TduaRAR1GKYqbcctOeV++auS\nJ/h6X4WrzWrUmlweCq4D0HPOAxNno9LYScUKcqprpMsSoLqYbnWG9gTG39NZiM6H\nPQvny6ULUfcEvj3y13qNYcu00J/bWhjtiIOFlUECgYEAwC/4ZM233EcyREooKge6\nQ9JS1SivehquQRhG+gd0Km4ncaM2fVpMyk3oqlm5lD2y3ezPGf/0W4GbnupTesw2\nBzrtFbrHo3dNtWrdeIjtAl+QrfRcBhMT6l7qxDTPVRre8mCjtqNcNPmgZNUMNigG\neVDgesq+B26RMP500R7+mds=\n-----END PRIVATE KEY-----\n','73c7d4b79b4341d','2026-06-23 17:21:16'),(2,'GOVSTACK','GOV','3001','health-app','-----BEGIN CERTIFICATE-----\nMIIDUjCCAjqgAwIBAgIIW9zszWG24CMwDQYJKoZIhvcNAQELBQAwQTELMAkGA1UE\nBhMCRUUxHDAaBgNVBAMME0dvdlN0YWNrIElNIFJvb3QgQ0ExFDASBgNVBAoMC0dv\ndlN0YWNrIElNMB4XDTI2MDYyMzE3MjYyM1oXDTI4MDkyNTE3MjcyM1owbzELMAkG\nA1UEBhMCRUUxHTAbBgNVBAMMFDMwMDEvaGVhbHRoLWFwcCBzaWduMSwwKgYDVQQK\nDCNNaW5pc3RyeSBvZiBoZWFsdGggJiBmYW1pbHkgd2VsZmFyZTETMBEGA1UECwwK\naGVhbHRoLWFwcDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBANrrNYyh\n1tUoUiT5bP47VsyIdAf7fwbbii77WJRgc5kgvzBaHzmqbvmLuZEryTh1MwPPk9zJ\nlr4WjZEY5Wb9zPFlIxf12oatbUli6AvENaARMMe6HK5gXtrC8KKx096r0g3dKFyb\n4TRJ7pgxwLgYSIFnkW/FHNHWDakqNiZ/t67JKSkFORoPMX9tNoRdNIHtHFFN10E0\nWqAEq//bWg7yB5jObT6uCSv9Lod1aR9rO0xAlMRdLlFYAK1CNqMpWWJVVDIVuJPP\n6ZmVLXI7BMibK7KYQApmyMGJdszAfnOLDMtkkp94iFEiyAS5Cjzk9VQvlQw0oeGx\nJRRtEori59oT/4MCAwEAAaMgMB4wDAYDVR0TAQH/BAIwADAOBgNVHQ8BAf8EBAMC\nBsAwDQYJKoZIhvcNAQELBQADggEBAEt61CRW538/hSJ1GiJPB/KWjp84tqDvNayq\nFFzdVook/KnAYaVuVPJQxNkknYg3a0wZjZhqDhv/X0SFoCZpXr8TU8cKiKVP8bQa\ntdh8ezzJltqriEKqw3y0nQ/UbOo74UqrC3adRxtQH+u21U4VdFKFPdGtcOzCSoI4\n8ug9HZgctnhnCBtLl2r3WQHsM3kqcfVYjCO62U1t3mU07M/7YyaoQ+N90p8mfkfI\nvEHK/LlatlqzufMO8tlJjPlPYrCaj7LA3XvxivtahtXjJ5BWhi2IVLBpzU7KCdrM\nL7V2tVIzP225/R/R7KCBUN7V814VxPDTpnWfYehSXwU983KGo9g=\n-----END CERTIFICATE-----\n','-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDa6zWModbVKFIk\n+Wz+O1bMiHQH+38G24ou+1iUYHOZIL8wWh85qm75i7mRK8k4dTMDz5PcyZa+Fo2R\nGOVm/czxZSMX9dqGrW1JYugLxDWgETDHuhyuYF7awvCisdPeq9IN3Shcm+E0Se6Y\nMcC4GEiBZ5FvxRzR1g2pKjYmf7euySkpBTkaDzF/bTaEXTSB7RxRTddBNFqgBKv/\n21oO8geYzm0+rgkr/S6HdWkfaztMQJTEXS5RWACtQjajKVliVVQyFbiTz+mZlS1y\nOwTImyuymEAKZsjBiXbMwH5ziwzLZJKfeIhRIsgEuQo85PVUL5UMNKHhsSUUbRKK\n4ufaE/+DAgMBAAECggEACLQ/GoYLoBKVw9BLjj3gB+Zk/8etzmpHnV+8ZeC5AQtV\nah/iC6jo0vDo+QpgETDg34XqdoqNWFzon3ewOZXLdM2ZxVD3+r5F7GULeWxKkPdC\nlK5a0QHNDNNX9NbmVaHarw3cA9KchjezcpCH2RMeGAcPSmuCwvmkWoxcP2J5KyeK\nqa7kq8HwJBrP4FTlcsfsglklt5dtd9QW3RkPsftwkqa0MULkUkTfxj9HvS/8jL/s\n/TLRy0ygq8yjSYItYK066f6N1fqxiGQF7ymoy/G6632XPjogryNjbzDvPlF+P7XE\nK34BCy1At5d/kx4jjKcx/GZ1+waDyWL17LLC0EYeAQKBgQD6cE/eitgcVcuobbu3\nEN9lPf/lszn5TbpE4/Kp3TjgXdU4UIH5wtjimUk9e+3gc4hREhZYZXnlz47fxB54\nWFN4WONNX2xr5CP6BItO33K9YnWPfdHWiwyuTyn6Di+e9GFMnn9F0lzN8rLR8aM9\n37HkAfaie3zPX/b1i/t4VK79rQKBgQDfx7ajZMwlL72u5wEI0E0cd1os/aQZwmsX\nuOJ9tKvgrltXZ2m3GaRSBhGlP7L3dkJPp/c3HeASoKjf7G2u5/Regc+EInvnZhNG\nNAOWmGeIL6LexULdF4wGcM7PsoituMBsDjvYf51JFtTJN0VUCXE/9Port2QO+k+O\nbsfSB6k37wKBgGCmL2ynELf+tFYP4z3HGS+tObCf9mOsB5LGlcPQSD7ud3cAOuj0\ntVbd6VH9HdRdQeJnpJAAuYZjD7Rzr36qN6xeQXp+tQz+QpQeZNTPjyxfbxcta2ns\nx7wNeRmzl9U0Ysh68oszn/UrEK/NHT6nsbNYvqH+HjC5zEj++NF7fP0RAoGARq5y\nBZHk2SoHI6NbNEl20bLxDJzgpDJAWTHQeBwE3ea0exryzR6QREgecq93+6misD5B\nW2tYRwnvzSqESmaBTQh7XyT1NdWL6PSs3Xgt21oQe4Sa5fJ2C+K9r+SYPybHwFmO\nlYdZSqindRa8ExsYZjcefYhjVkfBsR9UhgZdcIkCgYEAsfkjBb0mxc+mYoJIG14s\nlGaWaC8InATbHm4v1EhdTO8z18ZCqAxBlpopkSJOa/a9wYcsHgMGL2KBZ9xcPE2K\nOY/dgXEVudckKVYtLd9/8Ag4/CQXp7ybNOV3iUAxXFvyC9NFgjZ+SP80PAcl3MRw\n9aE9ci5RNuEYZHFVKsxoC2Y=\n-----END PRIVATE KEY-----\n','5bdceccd61b6e023','2026-06-23 17:27:23');
/*!40000 ALTER TABLE `sg_application` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sg_async_message`
--

DROP TABLE IF EXISTS `sg_async_message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sg_async_message` (
  `id` int NOT NULL AUTO_INCREMENT,
  `message_id` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `direction` varchar(8) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `consumer` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `service` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `body` text COLLATE utf8mb4_unicode_ci,
  `envelope` text COLLATE utf8mb4_unicode_ci,
  `provider_address` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `callback_url` varchar(512) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `attempts` int DEFAULT NULL,
  `next_attempt` datetime DEFAULT NULL,
  `response` text COLLATE utf8mb4_unicode_ci,
  `error` varchar(512) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `message_id` (`message_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sg_async_message`
--

LOCK TABLES `sg_async_message` WRITE;
/*!40000 ALTER TABLE `sg_async_message` DISABLE KEYS */;
/*!40000 ALTER TABLE `sg_async_message` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sg_globalconf`
--

DROP TABLE IF EXISTS `sg_globalconf`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sg_globalconf` (
  `id` int NOT NULL AUTO_INCREMENT,
  `conf_json` text COLLATE utf8mb4_unicode_ci,
  `signature` text COLLATE utf8mb4_unicode_ci,
  `signer_cert_pem` text COLLATE utf8mb4_unicode_ci,
  `verified` tinyint(1) DEFAULT NULL,
  `fetched_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sg_globalconf`
--

LOCK TABLES `sg_globalconf` WRITE;
/*!40000 ALTER TABLE `sg_globalconf` DISABLE KEYS */;
INSERT INTO `sg_globalconf` VALUES (25,'{\"instance\": \"GOVSTACK\", \"generated_at\": \"2026-07-09T11:44:40.364184Z\", \"entities\": [{\"entity_class\": \"GOV\", \"entity_code\": \"1001\", \"name\": \"Ministry of Digital Affairs\", \"applications\": [\"consumer-app\"]}, {\"entity_class\": \"GOV\", \"entity_code\": \"2001\", \"name\": \"Population Registry Agency\", \"applications\": [\"registry\"]}, {\"entity_class\": \"GOV\", \"entity_code\": \"3001\", \"name\": \"Ministry of health & family welfare\", \"applications\": [\"health-app\"]}, {\"entity_class\": \"GOV\", \"entity_code\": \"4001\", \"name\": \"Ministry of IT\", \"applications\": []}, {\"entity_class\": \"GOV\", \"entity_code\": \"5001\", \"name\": \"Ministry of education\", \"applications\": [\"EDU_app2\"]}], \"security_gateways\": [{\"gateway_code\": \"SG1\", \"owner\": \"GOV/1001\", \"address\": \"https://127.0.0.1:8443\", \"auth_cert_pem\": \"-----BEGIN CERTIFICATE-----\\nMIIDdDCCAlygAwIBAgIJAOrcTQgpvRlFMA0GCSqGSIb3DQEBCwUAMEExCzAJBgNV\\nBAYTAkVFMRwwGgYDVQQDDBNHb3ZTdGFjayBJTSBSb290IENBMRQwEgYDVQQKDAtH\\nb3ZTdGFjayBJTTAeFw0yNjA2MjMxNzE5MjRaFw0yODA5MjUxNzIwMjRaMFUxCzAJ\\nBgNVBAYTAkVFMREwDwYDVQQDDAhTRzEgYXV0aDEkMCIGA1UECgwbTWluaXN0cnkg\\nb2YgRGlnaXRhbCBBZmZhaXJzMQ0wCwYDVQQLDARhdXRoMIIBIjANBgkqhkiG9w0B\\nAQEFAAOCAQ8AMIIBCgKCAQEAtJSmBNJbPINZWZ2ARWDf3r5xnqnKR3wOuy1iyFyb\\n+b4Ry/va2jQuMEfnB5eKcbeJZ7nQMvGtT8nfFVR9p9cp+nmz5h6GbWdVrtUSKr83\\nC+YnyXaa6HWN1aUrIqXY9r2bpPSpPOmalNdp+f0mzWuIsbHbFKyhtKYX4n25P+nR\\ngR5I3Q9WAzF0CSdvhRTn5lVffara4t9TEPgS36/mxyaGvCObMmsAEP84H7A+xQeE\\nYVHiMZ0IIa7Vuv+0WYcUWw/SHMEC5YNiyhX+x1oOiRUph0FNxkObZ3NBNDSSo6I2\\n2O9WMFHtYUWnmWIgrVE/Ny4fjrkpqleXJb4uxKiCJLylXwIDAQABo1swWTAMBgNV\\nHRMBAf8EAjAAMB0GA1UdJQQWMBQGCCsGAQUFBwMCBggrBgEFBQcDATAOBgNVHQ8B\\nAf8EBAMCBaAwGgYDVR0RBBMwEYIJbG9jYWxob3N0hwR/AAABMA0GCSqGSIb3DQEB\\nCwUAA4IBAQCaUl/nFMW5wn5Sspq/c6p0WDNsxfbonvpJnco3iwCG8IVvEYzqQpST\\nrGhfCPRBR3COeAM3brSbtYxZ0ryaWa3ARpf1Huqhxh3PVrNRHbG76yrt7xgep84j\\nY/7Xb1xvTArm7ULKZNfx2a1ZbQzJeyOI2EMfa6/nH11IXWR6m+5JLHY/OTt1qa2K\\nfgKOkwqgABdXfnD4Ar6XPHdGYDPJCOT58nhOjC6MvAiUj2vp3BvmG5r7U6q+UR4G\\ne6FyM1iayS4b+7wKVPzTzpVHu+RBh1r+rCrL9bc513zZ252R5KhWsAw+wb/SAEmu\\nRAt5gfNOnpySBSnZTHSNc9dtB+JS5+OR\\n-----END CERTIFICATE-----\\n\", \"applications\": [\"GOVSTACK/GOV/1001/consumer-app\", \"GOVSTACK/GOV/3001/health-app\"]}, {\"gateway_code\": \"SG2\", \"owner\": \"GOV/2001\", \"address\": \"https://127.0.0.1:8444\", \"auth_cert_pem\": \"-----BEGIN CERTIFICATE-----\\nMIIDczCCAlugAwIBAgIJAMdJurTNLi6PMA0GCSqGSIb3DQEBCwUAMEExCzAJBgNV\\nBAYTAkVFMRwwGgYDVQQDDBNHb3ZTdGFjayBJTSBSb290IENBMRQwEgYDVQQKDAtH\\nb3ZTdGFjayBJTTAeFw0yNjA2MjMxNzE5NDZaFw0yODA5MjUxNzIwNDZaMFQxCzAJ\\nBgNVBAYTAkVFMREwDwYDVQQDDAhTRzIgYXV0aDEjMCEGA1UECgwaUG9wdWxhdGlv\\nbiBSZWdpc3RyeSBBZ2VuY3kxDTALBgNVBAsMBGF1dGgwggEiMA0GCSqGSIb3DQEB\\nAQUAA4IBDwAwggEKAoIBAQC3eV6wwghBbv6PgTNXD3Wdhnokh0uFamhhFqEIEU6G\\ncbJXeSlyqKBcktqdQfY1iSp0wCin8jpu2BBIAngyd7nz1Ep3GDxAEEu6Q224nYen\\n7fNfRe2rJFJrhE+SYiCiynPdMDqbmeJqZ0IHGOiUGehrXFDAwn92APF0cSu6CiTJ\\nNY5b67J2iLWYoyeK/2U5gQg8woE3S91MotlUHmYTCjCGR0zeST5hMSH97lHE4BGp\\nNPlyYAAoSjYrS0SCGPs4dEVPFRb1azgqOp+q8XUr6GN7Bzseeefy8sC8/dIdOURf\\nzOwmFNQtXdpwLOsgv9IqNs40b0TWYDRwnuN6kiZZl7qjAgMBAAGjWzBZMAwGA1Ud\\nEwEB/wQCMAAwHQYDVR0lBBYwFAYIKwYBBQUHAwIGCCsGAQUFBwMBMA4GA1UdDwEB\\n/wQEAwIFoDAaBgNVHREEEzARgglsb2NhbGhvc3SHBH8AAAEwDQYJKoZIhvcNAQEL\\nBQADggEBAB0bt3r2zP1RWqiPzthh5plVame7/Yse9sNhjilkSlnyk4m1z9smzfc9\\nKIXpieDJaaPaDnHQU2Y4lQDmj27lwK8WKEp0cC96QEhFZf3G9+wNOVqPft2PLmfG\\nrdmnbgtGccNBQTnH8V7eV5d3SnhNjHQS1BxMkstFSadDi/60Q3oLUZl55eExqMyA\\nz269G4FBCrfkXu//aoPGm1wI3MsG8s+gGxvLbJ5Y8c+w1d2//fwxZJa2z0Ai18RR\\nntJkbBCfefS1j3F2sZUtwMC79gi9fOAiSRCIIDMMCKUXSV2tij7kmEt2f2BOIfDp\\nLwYtkZ1hSrV/Lws6QGOlaNF04h5fH+c=\\n-----END CERTIFICATE-----\\n\", \"applications\": [\"GOVSTACK/GOV/2001/registry\", \"GOVSTACK/GOV/5001/EDU_app2\"]}], \"services\": [{\"service_id\": \"GOVSTACK/GOV/2001/registry/getPerson\", \"gateway_code\": \"SG2\", \"description\": \"Look up a person by national id\"}, {\"service_id\": \"GOVSTACK/GOV/2001/registry/echo\", \"gateway_code\": \"SG2\", \"description\": \"Echo service\"}, {\"service_id\": \"GOVSTACK/GOV/3001/health-app/getPerson\", \"gateway_code\": \"SG1\", \"description\": \"Look up a person by national id\"}], \"trusted_cas\": [\"-----BEGIN CERTIFICATE-----\\nMIIDNjCCAh6gAwIBAgIUYFJMFMYThzULhLs5vW/Y0OLevAAwDQYJKoZIhvcNAQEL\\nBQAwQTELMAkGA1UEBhMCRUUxHDAaBgNVBAMME0dvdlN0YWNrIElNIFJvb3QgQ0Ex\\nFDASBgNVBAoMC0dvdlN0YWNrIElNMB4XDTI2MDYxODEwMTMyNFoXDTM2MDYxNTEw\\nMTQyNFowQTELMAkGA1UEBhMCRUUxHDAaBgNVBAMME0dvdlN0YWNrIElNIFJvb3Qg\\nQ0ExFDASBgNVBAoMC0dvdlN0YWNrIElNMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A\\nMIIBCgKCAQEAoxdqn01j17FINsz8QodsY5kM0n/WwciGKp5/bH+zoI/Ld98ttAIc\\nwXL920HYLb99HOSZ99KSJm4IJK7vaeBD3wHwvJYzVcKLa36ufWlxQT1xtmeJGCQj\\nMP0zDB2t0yDFsrfd7Uc3z5IpGC2tJlzf8dVyyAUNW8k1VrwvbfnyHIYqdoaI2v70\\nxLf/NJbDZFtt5VeXOYbfrWyWUJjFO8wUQ97BoJ87A/swvhqzLXFl8Lpw6pxiDnhd\\nK500loN91SLjhLUyF1old/WsYuQriYmdu9dGzw7Z7rRLe6zhrTCSoI7v/VXPRMYD\\n7CN9cTl6oHLYD93aJo+9kz23IGT8tQpCsQIDAQABoyYwJDASBgNVHRMBAf8ECDAG\\nAQH/AgEBMA4GA1UdDwEB/wQEAwIBhjANBgkqhkiG9w0BAQsFAAOCAQEAO6XuAyjS\\nvtoh+wNsbndzsSc+EQKgAWKNpCWGSEkOf/u4gzTRNy+Nq72M1fHKV2LYDOgtDUx7\\nHMa1GOI8Se/PzZOceYPUeTv6t74vuFBbzMaxZ0IItBCgOCkqLoYbaRUoDEPwntNm\\nECs+LUxsVNfiGdyicf7hliXA113h6QBGu1wWqGRr3jGCdXKhV02eEkP4F1l7z99r\\nPsVLTDj722tIMmqxr+7mrSBobAq8XCgWEvCWYMPHv3KieQRhbn/GSFcUPK6QNMIP\\n3GkiZf/G8VpTYqsm0W1mFWwZaBayInHJLDVRe+vXptejnSvS6AVWMu7rWbNsweWj\\noLdZfAzsYJN4iQ==\\n-----END CERTIFICATE-----\\n\"], \"trusted_tsas\": [{\"url\": \"http://127.0.0.1:9002\", \"cert_pem\": \"-----BEGIN CERTIFICATE-----\\nMIIDRjCCAi6gAwIBAgIIH1rCAaT1kLcwDQYJKoZIhvcNAQELBQAwQTELMAkGA1UE\\nBhMCRUUxHDAaBgNVBAMME0dvdlN0YWNrIElNIFJvb3QgQ0ExFDASBgNVBAoMC0dv\\ndlN0YWNrIElNMB4XDTI2MDYxODEwMTMzMloXDTI4MDkyMDEwMTQzMlowSzELMAkG\\nA1UEBhMCRUUxGDAWBgNVBAMMD0dvdlN0YWNrIElNIFRTQTEUMBIGA1UECgwLR292\\nU3RhY2sgSU0xDDAKBgNVBAsMA1RTQTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCC\\nAQoCggEBAMOuDB8eDqiABspBsXUi+wr0+4AwIvG7Rk4qa2Y2dMCEUyuXRjOtW7Yb\\nto51tJPBFhOymL5/knCBDEkEaBpaXDRIX5s0T11vZ8enY5tfw+i9qHglIHI1bUCc\\nKc1M3/boZrosUP/Kx8sl4eixEeRm6tRZu0Jm4ZJjNnQdGWmW9WmzgAXqbz4XWWix\\nSiN6unjRjYTWV5E/yq+6WP8HfGSbKVw3YOQB4XY2RnAGGD0CocjgjE4jiqT1JbuH\\nAjhtI34WgWTKzDWzOjKh0x1MKOu4gJxzJzQcUl4jWGh0SfvHTOsELjb9a6xvn+0Y\\npLnB2es6BWKQ8FgJ59lSalwne2PMh18CAwEAAaM4MDYwDAYDVR0TAQH/BAIwADAW\\nBgNVHSUBAf8EDDAKBggrBgEFBQcDCDAOBgNVHQ8BAf8EBAMCBsAwDQYJKoZIhvcN\\nAQELBQADggEBAJOS5vMc91Sfbs4hA4RJ5M1XoeFepJqXCt7yENe5R4it5qlN8m6A\\n2/Ne+jp2jGbI7MiDR0MwVZCKAzsbe3aeCluDp+Zvnyo63DjjTVpFZb9Gr5jceiSe\\njiQbxLOAAd9JvpfXviONPNKInZOrj9rINjoOQPej5e6AS74HYx8P6rDV2LX9BY03\\n+l3yGENtbGSNWF+BodEjjy5REYAl0YYi2A5EGP00sCGwQA3WWJBw35ujhu+/LwL4\\ncbgK8YSOTAgXBhzufAZFY8t/ZTnttY2P6+fHOuPP100qQU0V+BCdUYo1bs9XLV38\\nyJypODnjL8OKR7dj0RtqtSABh7WJ/dEuj44=\\n-----END CERTIFICATE-----\\n\"}], \"global_settings\": {\"ocsp_fresh_seconds\": 3600, \"time_stamping_required\": true}}','nE5Dg8kAu8aSbzLM3G7bho0WxknrUqcrVBsq0VD9UtliAER27Hhdvw7SBEk4VQ3JZhwwPSC8wpv/2YalywaM+S3xm8ggp9Wl48j5WBWL58mu1ULQD+sN6Q4OqJdgXL5+1Mk853bbRccEdbxQW80ej+BZJAxSXXlFnEvznPu0bUrE/0+gz+3gOm9yY0oay8DEyoXonGktlcv1WqxpCsGZoOzLdbk2VgT4liRNgKXN6HAQhRrTojKuHLzXZ4WKLrUMNF4t+L85SXdthJUqUzd5gxwm45i0cMPQz59Yb4Ltg/H2UQnjhIyjn+buQ2nh8YNYjcDkIa9lhhi52Lopq5M2hw==','-----BEGIN CERTIFICATE-----\nMIIDSTCCAjGgAwIBAgIJAOsU+3gGZJaDMA0GCSqGSIb3DQEBCwUAMEExCzAJBgNV\nBAYTAkVFMRwwGgYDVQQDDBNHb3ZTdGFjayBJTSBSb290IENBMRQwEgYDVQQKDAtH\nb3ZTdGFjayBJTTAeFw0yNjA2MTgxMjQ0MTNaFw0yODA5MjAxMjQ1MTNaMGUxCzAJ\nBgNVBAYTAkVFMSswKQYDVQQDDCJJbmZvcm1hdGlvbiBNZWRpYXRvciBHbG9iYWwg\nU2VydmVyMRQwEgYDVQQKDAtHb3ZTdGFjayBJTTETMBEGA1UECwwKR2xvYmFsQ29u\nZjCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAKeHlNyS4N/sZ5xVicT8\nBPRUQi9RiGIrQT+Gk8nIEcSk9ca7GIY8ph4UOJyyMUbb3RIpwtDh7/oUGu5urmKK\nK9f2bUj53bSrEdHmD5n2XRvEdmhBUvw8eCd8Wppa3qWOP/491R8caE3319+JTTND\n18JXNsSiwXlTZ02NLkImMEX4sHYT/G4ipL8F+8RovLp8yHmeNMCSPPyPHf2UluLW\nOrgZgr75QFRyawvg+9K1lYWugMRjE+baE87AzIJbkzDMMBy1jsQo9+hyroLl2TIn\nNsiyXWjannE+f3BxrFl9t2mA1QokNTRdp7HFJclevVmZ7MEbTBwD9hO3ApKukaPd\nhDUCAwEAAaMgMB4wDAYDVR0TAQH/BAIwADAOBgNVHQ8BAf8EBAMCBsAwDQYJKoZI\nhvcNAQELBQADggEBABPs+0MxsGYsSPd3Y0xmDXs5d9jbb8eIF050+hqHV0hKjfJ6\nd0UigTgUm6OvPBe7TRASPtqNZZNmPvf7uibcrJxvuFJ7iqBfpsAW6bZhtu2EJtIV\nz0oL+eCrl4GZ3C1NCBh3S2aS3AarUnGmMEWZI7f5qT9r4zyTNs28N1++km9A6iUx\nOTvsGqa6XPFq7+TgEjj8syXcT/DWzwoHEk8S2+9JYhoGlIigwYGJYn41UMopxgPc\nu2YJ7Lcm/QM/jX+NBz0vwtP+YLauOShusz5E9Fn/rUtA+xsIHIZrAEDaKcT6mrlB\nTkPQ20NKdvbodrJ/K+Sy/XogtY7kLIs/J9O6wtE=\n-----END CERTIFICATE-----\n',1,'2026-07-09 11:44:41');
/*!40000 ALTER TABLE `sg_globalconf` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sg_identity`
--

DROP TABLE IF EXISTS `sg_identity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sg_identity` (
  `id` int NOT NULL AUTO_INCREMENT,
  `gateway_code` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `auth_cert_pem` text COLLATE utf8mb4_unicode_ci,
  `auth_key_pem` text COLLATE utf8mb4_unicode_ci,
  `auth_serial` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `registered` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sg_identity`
--

LOCK TABLES `sg_identity` WRITE;
/*!40000 ALTER TABLE `sg_identity` DISABLE KEYS */;
INSERT INTO `sg_identity` VALUES (1,'SG1','-----BEGIN CERTIFICATE-----\nMIIDdDCCAlygAwIBAgIJAOrcTQgpvRlFMA0GCSqGSIb3DQEBCwUAMEExCzAJBgNV\nBAYTAkVFMRwwGgYDVQQDDBNHb3ZTdGFjayBJTSBSb290IENBMRQwEgYDVQQKDAtH\nb3ZTdGFjayBJTTAeFw0yNjA2MjMxNzE5MjRaFw0yODA5MjUxNzIwMjRaMFUxCzAJ\nBgNVBAYTAkVFMREwDwYDVQQDDAhTRzEgYXV0aDEkMCIGA1UECgwbTWluaXN0cnkg\nb2YgRGlnaXRhbCBBZmZhaXJzMQ0wCwYDVQQLDARhdXRoMIIBIjANBgkqhkiG9w0B\nAQEFAAOCAQ8AMIIBCgKCAQEAtJSmBNJbPINZWZ2ARWDf3r5xnqnKR3wOuy1iyFyb\n+b4Ry/va2jQuMEfnB5eKcbeJZ7nQMvGtT8nfFVR9p9cp+nmz5h6GbWdVrtUSKr83\nC+YnyXaa6HWN1aUrIqXY9r2bpPSpPOmalNdp+f0mzWuIsbHbFKyhtKYX4n25P+nR\ngR5I3Q9WAzF0CSdvhRTn5lVffara4t9TEPgS36/mxyaGvCObMmsAEP84H7A+xQeE\nYVHiMZ0IIa7Vuv+0WYcUWw/SHMEC5YNiyhX+x1oOiRUph0FNxkObZ3NBNDSSo6I2\n2O9WMFHtYUWnmWIgrVE/Ny4fjrkpqleXJb4uxKiCJLylXwIDAQABo1swWTAMBgNV\nHRMBAf8EAjAAMB0GA1UdJQQWMBQGCCsGAQUFBwMCBggrBgEFBQcDATAOBgNVHQ8B\nAf8EBAMCBaAwGgYDVR0RBBMwEYIJbG9jYWxob3N0hwR/AAABMA0GCSqGSIb3DQEB\nCwUAA4IBAQCaUl/nFMW5wn5Sspq/c6p0WDNsxfbonvpJnco3iwCG8IVvEYzqQpST\nrGhfCPRBR3COeAM3brSbtYxZ0ryaWa3ARpf1Huqhxh3PVrNRHbG76yrt7xgep84j\nY/7Xb1xvTArm7ULKZNfx2a1ZbQzJeyOI2EMfa6/nH11IXWR6m+5JLHY/OTt1qa2K\nfgKOkwqgABdXfnD4Ar6XPHdGYDPJCOT58nhOjC6MvAiUj2vp3BvmG5r7U6q+UR4G\ne6FyM1iayS4b+7wKVPzTzpVHu+RBh1r+rCrL9bc513zZ252R5KhWsAw+wb/SAEmu\nRAt5gfNOnpySBSnZTHSNc9dtB+JS5+OR\n-----END CERTIFICATE-----\n','-----BEGIN PRIVATE KEY-----\nMIIEuwIBADANBgkqhkiG9w0BAQEFAASCBKUwggShAgEAAoIBAQC0lKYE0ls8g1lZ\nnYBFYN/evnGeqcpHfA67LWLIXJv5vhHL+9raNC4wR+cHl4pxt4lnudAy8a1Pyd8V\nVH2n1yn6ebPmHoZtZ1Wu1RIqvzcL5ifJdprodY3VpSsipdj2vZuk9Kk86ZqU12n5\n/SbNa4ixsdsUrKG0phfifbk/6dGBHkjdD1YDMXQJJ2+FFOfmVV99qtri31MQ+BLf\nr+bHJoa8I5syawAQ/zgfsD7FB4RhUeIxnQghrtW6/7RZhxRbD9IcwQLlg2LKFf7H\nWg6JFSmHQU3GQ5tnc0E0NJKjojbY71YwUe1hRaeZYiCtUT83Lh+OuSmqV5clvi7E\nqIIkvKVfAgMBAAECgf9pODQu8GM5CfqGEmqArRxvgt2xauhHvtbWjxt/+SDpOawl\nBMYAtBGLEFpi52nug4MMwrhi9sSFjprt/Xfk1E/MIsiFeEPb0NpG2jWRCC81lRCZ\n0wIaxmRemF8J++5FLItZvTWKHekfJmVvGegCHyZcY8XDxihy76n7JEaiIcZxSg4S\nsJnEcx578Ky+Y8dPn4KDXyatXkVzb48RPKJHLNyc2GkvwvkTT6EIWHdMUvHFkwLc\ns3VNRieEe2NKRJdTv/mNtC4QeLEEkNisvn5x86ZroxqDFUPPvp2Sn411agQR47P+\nIMRaZJ5FNKMjzney78F45a7t6M/cNP4hhF4JWo0CgYEA6Z8K6quyvkxQw1X2Wth4\n0vWXYD4JeRHrh5BNULzo7agQTEVrLkjLypg+DtDOP4teTavVC/gtHmaP0CF2qK8j\nKRn3hIyqcbvFWxIqNUhB4F8h/W9qOk1GDBxE5teouZ06fmBDxYZpMCZe9RWTrb8u\nivw4Um+V9EUMYe+vMKMvc00CgYEAxeDsGC3vB6gkfKxKj9sdyTkMVRbt93tnfG5X\nXxiVdNSBrUMV2zb7A63RcFnXB3XP6ZVvVkH+N0Iu1pgwqQFvbmzijMK0v5crZvEZ\nP51OsFkc+/1JULF42HIy9b0ocT9NHc6hBGtRyh5c23uFCQV2peQL30AIKJCSlsOC\nVNiyzVsCgYEAvznbqbLZIEM/aGSYvkuquqMkQTcGcf9lFxXa81duIfoLPSMlVEFp\n7m8nfOEVsZXWnyUjwiRmahfxZ5+8jN6unRoQLIMnkOjt5lm8CtkWcx3rqJLmFMrj\np04MaBfml+hG1OLfFnOq7iq6V0pOE04GPuWtBG0qBUPvmsqiT+GDGZECgYBybIr5\nvG4RZmia82I2Z4WE24lHFvhKeMCx0niRk/ywz0WhdD6KQfPK/9MxfbH7LWQp9XCp\nV4XyXEILc3wH7r2KBErJDLpKY9cEMvzfrU5YaV96U8/2anmv5/GR6m0dd3ZXeynf\nDVQBZadaf8XBHriqWwGGeld9ZYRuy+VsvNZAKwKBgHy/KTmGFf76VFCh/RY/FFti\nTsapSmFfFccvtSyZLixcS9ebve3/n9sAY1tpTuuZTgil9nK1RJTh5qXI0oIWBz1v\nS9y8kt/RqLC7anf6qzDD3hwmAQrrYalkHAm/P3H6FQflR+GJ6eKIny3JBNsEN3Yz\nt/rLmcu3GV8SJeWYxs9q\n-----END PRIVATE KEY-----\n','eadc4d0829bd1945',1,'2026-06-23 17:20:26');
/*!40000 ALTER TABLE `sg_identity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sg_message_log`
--

DROP TABLE IF EXISTS `sg_message_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sg_message_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `message_id` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `direction` varchar(8) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `consumer` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `service` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `request_hash` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `signature` text COLLATE utf8mb4_unicode_ci,
  `sig_verified` tinyint(1) DEFAULT NULL,
  `ts_serial` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ts_verified` tinyint(1) DEFAULT NULL,
  `response_status` int DEFAULT NULL,
  `note` varchar(512) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sg_message_log`
--

LOCK TABLES `sg_message_log` WRITE;
/*!40000 ALTER TABLE `sg_message_log` DISABLE KEYS */;
INSERT INTO `sg_message_log` VALUES (1,'5f733ed3535b49cd929b5a0c1cca7c94','in','GOVSTACK/GOV/5001/EDU_app2','GOVSTACK/GOV/3001/health-app/getPerson','J3jfBuTup+101FscA3UxU8pqo5tNR90z/4uTEUscamg=','V/99OBp85BYZ9hz9synMqJn7tx2tM86ZBZMypRzBM4mMg/JlwK4O/jX38UmvksFQbpy988OOhM0zLbzAFgesVVswPPUTWoSYV6o4Ha21LRyH3lID3sf7nktGrXFV+DKR6tdGSWK3aDFX9Z/PteGV0GM09m/tTim7h+57YQuzFSC4OR3kP4N1niyivyXwQ7NHllyKFNpvcKnW4XE3ZtN5+2ETVC+lyypHBEQZbWSywDJGMWPkkwMQEZS9ocG1LU8QaYOzbXd7l4UNqT+1H6XdRl981PR19GzuIECDFmAQMpVmf0VD0TcNOkl+nvc5Bm0jUR3zRSZ/PCCHv6mIpkdd+w==',1,'9113061258551d55',1,200,'subscription ok; backend http://127.0.0.1:8090/backend/persons','2026-06-23 18:27:09'),(2,'11993ccf58a94f9e907193bb840ad6b3','in','GOVSTACK/GOV/5001/EDU_app2','GOVSTACK/GOV/3001/health-app/getPerson','n3b/glxHdYWAoC/qbXp3L2RipcfsuR8L2AW3k5G80a0=','wqi354UxE86kJUPalFPE3NnMuANfoU5FOfiGc4lMpp7uiXWzmwryobieU9Rfdv00G1q/cPbj7wrT3L28qYRmY3uXRvamttoxcc7+tetUTZ4xfOYkKv9BItxazww6szbcKjLgDAtFqoTtLlcVMY7xhD4zjqDPD8F2NYnT1vdoWh0XjAHspWx5A/GdLKR613exZYuniFGnUvrJg3aESY/k7MXZz2XWls0OMP/Vs58/vGNaXdUoZBrQG36DIvezTdE97SsCCg0xhAr8zVP4jutH6s5AgcuO+tTc/J4qPfgNE3ukklFO9kikAJqWUVCJWQ6lNZ8YEDjXa5aoFAA+h6MdHg==',1,'5e7002c77ddebe27',1,200,'subscription ok; backend http://127.0.0.1:8090/backend/persons','2026-06-24 08:15:32'),(3,'64ec35c26b224681960616195dabddd3','out','GOVSTACK/GOV/1001/consumer-app','GOVSTACK/GOV/2001/registry/getPerson','+dnkCG7SQV6EVq/GEZYsk/c+JiRBqHU4NWDa8bGBMec=','OBUUIcWq8CPCnb260DcfklWTTPq8QePH7Y4Uo50yFmVZZOXlTO3sTH9s4RRkchsymT/SIM3ufrT6190wAOWkT5SfDICk6CEfl3dDQABR8r2X6BS660Yl+eiNyE/QG4a1wyAmOsmfEJvoHj8oMfygk7QQQHUFR/fgO8DcdreN5swCxLRhILj9cxZF5l9GKc1JFQorf4QxO1enDD7kMBpqc4rkP3qw8NDHV3O7YCRfn7OS+59HVnAN6lfnqa2FQKnbpl8Ie3vF9gW+Wk3Rqex7CHRg/BVH/egfv/Sy2JgyxVZeY2uNs5J1ENmC0iEKoo2Q23Ix+6iKDFr6e+EEK2q73w==',1,'ae823505fca1bf66',1,NULL,'-> https://127.0.0.1:8444','2026-07-09 11:52:08'),(4,'64ec35c26b224681960616195dabddd3','out','GOVSTACK/GOV/1001/consumer-app','GOVSTACK/GOV/2001/registry/getPerson','+dnkCG7SQV6EVq/GEZYsk/c+JiRBqHU4NWDa8bGBMec=','OBUUIcWq8CPCnb260DcfklWTTPq8QePH7Y4Uo50yFmVZZOXlTO3sTH9s4RRkchsymT/SIM3ufrT6190wAOWkT5SfDICk6CEfl3dDQABR8r2X6BS660Yl+eiNyE/QG4a1wyAmOsmfEJvoHj8oMfygk7QQQHUFR/fgO8DcdreN5swCxLRhILj9cxZF5l9GKc1JFQorf4QxO1enDD7kMBpqc4rkP3qw8NDHV3O7YCRfn7OS+59HVnAN6lfnqa2FQKnbpl8Ie3vF9gW+Wk3Rqex7CHRg/BVH/egfv/Sy2JgyxVZeY2uNs5J1ENmC0iEKoo2Q23Ix+6iKDFr6e+EEK2q73w==',1,'ae823505fca1bf66',1,200,'response received','2026-07-09 11:52:10');
/*!40000 ALTER TABLE `sg_message_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sg_service`
--

DROP TABLE IF EXISTS `sg_service`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sg_service` (
  `id` int NOT NULL AUTO_INCREMENT,
  `entity_class` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `entity_code` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `application_code` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `service_code` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `backend_url` varchar(512) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `enabled` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sg_service`
--

LOCK TABLES `sg_service` WRITE;
/*!40000 ALTER TABLE `sg_service` DISABLE KEYS */;
INSERT INTO `sg_service` VALUES (1,'GOV','3001','health-app','getPerson','http://127.0.0.1:8090/backend/persons','Look up a person by national id',1,'2026-06-23 17:29:09');
/*!40000 ALTER TABLE `sg_service` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sg_service_catalog`
--

DROP TABLE IF EXISTS `sg_service_catalog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sg_service_catalog` (
  `id` int NOT NULL AUTO_INCREMENT,
  `service_id` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `gateway_code` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fetched_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `service_id` (`service_id`)
) ENGINE=InnoDB AUTO_INCREMENT=72 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sg_service_catalog`
--

LOCK TABLES `sg_service_catalog` WRITE;
/*!40000 ALTER TABLE `sg_service_catalog` DISABLE KEYS */;
INSERT INTO `sg_service_catalog` VALUES (69,'GOVSTACK/GOV/2001/registry/echo','SG2','Echo service','2026-07-09 11:44:41'),(70,'GOVSTACK/GOV/2001/registry/getPerson','SG2','Look up a person by national id','2026-07-09 11:44:41'),(71,'GOVSTACK/GOV/3001/health-app/getPerson','SG1','Look up a person by national id','2026-07-09 11:44:41');
/*!40000 ALTER TABLE `sg_service_catalog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sg_subscriber`
--

DROP TABLE IF EXISTS `sg_subscriber`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sg_subscriber` (
  `id` int NOT NULL AUTO_INCREMENT,
  `service_code` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `service_id` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `subscriber` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `service_code` (`service_code`,`subscriber`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sg_subscriber`
--

LOCK TABLES `sg_subscriber` WRITE;
/*!40000 ALTER TABLE `sg_subscriber` DISABLE KEYS */;
INSERT INTO `sg_subscriber` VALUES (1,'getPerson','GOVSTACK/GOV/3001/health-app/getPerson','GOVSTACK/GOV/2001/registry','rejected','2026-06-23 18:11:54'),(2,'getPerson','GOVSTACK/GOV/3001/health-app/getPerson','GOVSTACK/GOV/5001/EDU_app2','approved','2026-06-23 18:25:01');
/*!40000 ALTER TABLE `sg_subscriber` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sg_subscription`
--

DROP TABLE IF EXISTS `sg_subscription`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sg_subscription` (
  `id` int NOT NULL AUTO_INCREMENT,
  `application_id` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `service_id` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `provider_gateway` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `application_id` (`application_id`,`service_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sg_subscription`
--

LOCK TABLES `sg_subscription` WRITE;
/*!40000 ALTER TABLE `sg_subscription` DISABLE KEYS */;
INSERT INTO `sg_subscription` VALUES (1,'GOVSTACK/GOV/1001/consumer-app','GOVSTACK/GOV/2001/registry/getPerson','SG2','approved','2026-06-23 17:21:22'),(2,'GOVSTACK/GOV/1001/consumer-app','GOVSTACK/GOV/2001/registry/echo','SG2','pending','2026-06-23 17:21:23');
/*!40000 ALTER TABLE `sg_subscription` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-07-16 19:33:33
