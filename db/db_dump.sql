-- MySQL dump 10.13  Distrib 8.2.0, for macos14.0 (arm64)
--
-- Host: localhost    Database: testDB
-- ------------------------------------------------------
-- Server version	8.2.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `cleaning`
--

DROP TABLE IF EXISTS `cleaning`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cleaning` (
  `cleaningID` bigint unsigned NOT NULL AUTO_INCREMENT,
  `cleaningTypeID` tinyint unsigned NOT NULL,
  `place` varchar(128) NOT NULL,
  `year_month` varchar(8) NOT NULL,
  `day` tinyint unsigned NOT NULL,
  `times` tinyint unsigned NOT NULL,
  `status` tinyint unsigned NOT NULL DEFAULT '0',
  `_monthly` varchar(8) GENERATED ALWAYS AS ((case when (`cleaningTypeID` = 2) then `year_month` else NULL end)) VIRTUAL,
  PRIMARY KEY (`cleaningID`),
  UNIQUE KEY `cleaningTypeID` (`cleaningTypeID`,`place`,`year_month`,`times`),
  UNIQUE KEY `_monthly` (`_monthly`,`day`),
  UNIQUE KEY `_monthly_2` (`_monthly`,`times`),
  CONSTRAINT `cleaning_ibfk_1` FOREIGN KEY (`cleaningTypeID`) REFERENCES `cleaningType` (`cleaningTypeID`) ON UPDATE CASCADE,
  CONSTRAINT `cleaning_chk_1` CHECK (regexp_like(`year_month`,_utf8mb4'^[0-9]{4}-[012][0-9]$')),
  CONSTRAINT `cleaning_chk_2` CHECK ((`day` <= 31))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cleaning`
--

LOCK TABLES `cleaning` WRITE;
/*!40000 ALTER TABLE `cleaning` DISABLE KEYS */;
/*!40000 ALTER TABLE `cleaning` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cleaningDuty`
--

DROP TABLE IF EXISTS `cleaningDuty`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cleaningDuty` (
  `cleaningDutyID` bigint unsigned NOT NULL AUTO_INCREMENT,
  `studentID` varchar(8) NOT NULL,
  `cleaningID` bigint unsigned NOT NULL,
  `cleaningStatusID` tinyint unsigned NOT NULL DEFAULT '4',
  `registeredStudentID` varchar(8) NOT NULL,
  `registeredTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`cleaningDutyID`),
  UNIQUE KEY `studentID` (`studentID`,`cleaningID`),
  KEY `cleaningStatusID` (`cleaningStatusID`),
  KEY `cleaningID` (`cleaningID`),
  KEY `registeredStudentID` (`registeredStudentID`),
  CONSTRAINT `cleaningduty_ibfk_1` FOREIGN KEY (`cleaningStatusID`) REFERENCES `cleaningStatus` (`cleaningStatusID`) ON UPDATE CASCADE,
  CONSTRAINT `cleaningduty_ibfk_2` FOREIGN KEY (`cleaningID`) REFERENCES `cleaning` (`cleaningID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `cleaningduty_ibfk_3` FOREIGN KEY (`studentID`) REFERENCES `student` (`studentID`) ON UPDATE CASCADE,
  CONSTRAINT `cleaningduty_ibfk_4` FOREIGN KEY (`registeredStudentID`) REFERENCES `student` (`studentID`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cleaningDuty`
--

LOCK TABLES `cleaningDuty` WRITE;
/*!40000 ALTER TABLE `cleaningDuty` DISABLE KEYS */;
/*!40000 ALTER TABLE `cleaningDuty` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cleaningDutyAgent`
--

DROP TABLE IF EXISTS `cleaningDutyAgent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cleaningDutyAgent` (
  `cleaningDutyID` bigint unsigned NOT NULL,
  `studentID` varchar(8) NOT NULL,
  PRIMARY KEY (`cleaningDutyID`),
  KEY `studentID` (`studentID`),
  CONSTRAINT `cleaningdutyagent_ibfk_1` FOREIGN KEY (`cleaningDutyID`) REFERENCES `cleaningDuty` (`cleaningDutyID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `cleaningdutyagent_ibfk_2` FOREIGN KEY (`studentID`) REFERENCES `student` (`studentID`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cleaningDutyAgent`
--

LOCK TABLES `cleaningDutyAgent` WRITE;
/*!40000 ALTER TABLE `cleaningDutyAgent` DISABLE KEYS */;
/*!40000 ALTER TABLE `cleaningDutyAgent` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cleaningStatus`
--

DROP TABLE IF EXISTS `cleaningStatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cleaningStatus` (
  `cleaningStatusID` tinyint unsigned NOT NULL,
  `cleaningStatus` varchar(16) NOT NULL,
  PRIMARY KEY (`cleaningStatusID`),
  UNIQUE KEY `cleaningStatus` (`cleaningStatus`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cleaningStatus`
--

LOCK TABLES `cleaningStatus` WRITE;
/*!40000 ALTER TABLE `cleaningStatus` DISABLE KEYS */;
INSERT INTO `cleaningStatus` VALUES (2,'absence'),(1,'attend'),(3,'substitute'),(4,'unconfirmed');
/*!40000 ALTER TABLE `cleaningStatus` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cleaningType`
--

DROP TABLE IF EXISTS `cleaningType`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cleaningType` (
  `cleaningTypeID` tinyint unsigned NOT NULL,
  `cleaningType` varchar(8) NOT NULL,
  PRIMARY KEY (`cleaningTypeID`),
  UNIQUE KEY `cleaningType` (`cleaningType`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cleaningType`
--

LOCK TABLES `cleaningType` WRITE;
/*!40000 ALTER TABLE `cleaningType` DISABLE KEYS */;
INSERT INTO `cleaningType` VALUES (2,'monthly'),(3,'special'),(1,'weekly');
/*!40000 ALTER TABLE `cleaningType` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `courses`
--

DROP TABLE IF EXISTS `courses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `courses` (
  `courseID` tinyint unsigned NOT NULL,
  `course` varchar(2) NOT NULL,
  PRIMARY KEY (`courseID`),
  UNIQUE KEY `course` (`course`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `courses`
--

LOCK TABLES `courses` WRITE;
/*!40000 ALTER TABLE `courses` DISABLE KEYS */;
INSERT INTO `courses` VALUES (4,'A'),(7,'AC'),(5,'C'),(2,'E'),(6,'EM'),(3,'I'),(1,'M');
/*!40000 ALTER TABLE `courses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dormitory`
--

DROP TABLE IF EXISTS `dormitory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dormitory` (
  `dormitoryID` tinyint unsigned NOT NULL,
  `dormitory` varchar(4) NOT NULL,
  PRIMARY KEY (`dormitoryID`),
  UNIQUE KEY `dormitory` (`dormitory`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dormitory`
--

LOCK TABLES `dormitory` WRITE;
/*!40000 ALTER TABLE `dormitory` DISABLE KEYS */;
INSERT INTO `dormitory` VALUES (2,'CEN'),(1,'MOU'),(3,'SEA'),(4,'SPA');
/*!40000 ALTER TABLE `dormitory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dormitoryPlace`
--

DROP TABLE IF EXISTS `dormitoryPlace`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dormitoryPlace` (
  `dormitoryPlaceID` tinyint unsigned NOT NULL,
  `dormitoryID` tinyint unsigned NOT NULL,
  `floor` tinyint unsigned NOT NULL,
  `place` varchar(128) NOT NULL,
  PRIMARY KEY (`dormitoryPlaceID`),
  UNIQUE KEY `place` (`place`),
  UNIQUE KEY `dormitoryID` (`dormitoryID`,`floor`),
  CONSTRAINT `dormitoryplace_ibfk_1` FOREIGN KEY (`dormitoryID`) REFERENCES `dormitory` (`dormitoryID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dormitoryPlace`
--

LOCK TABLES `dormitoryPlace` WRITE;
/*!40000 ALTER TABLE `dormitoryPlace` DISABLE KEYS */;
INSERT INTO `dormitoryPlace` VALUES (1,1,1,'MOU_1'),(2,1,2,'MOU_2'),(3,1,3,'MOU_3'),(4,2,1,'CEN_1'),(5,2,2,'CEN_2'),(6,2,3,'CEN_3'),(7,3,1,'SEA_1'),(8,3,2,'SEA_2'),(9,3,3,'SEA_3'),(10,4,1,'SPA_1'),(11,4,2,'SPA_2'),(12,4,3,'SPA_3'),(13,4,4,'SPA_4'),(14,4,5,'SPA_5');
/*!40000 ALTER TABLE `dormitoryPlace` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `IoT_Data`
--

DROP TABLE IF EXISTS `IoT_Data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `IoT_Data` (
  `IoT_DataID` bigint unsigned NOT NULL AUTO_INCREMENT,
  `IoTID` varchar(8) NOT NULL,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `dataStatus` tinyint unsigned NOT NULL,
  PRIMARY KEY (`IoT_DataID`),
  KEY `IoTID` (`IoTID`),
  CONSTRAINT `iot_data_ibfk_1` FOREIGN KEY (`IoTID`) REFERENCES `IoT_IP` (`IoTID`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `IoT_Data`
--

LOCK TABLES `IoT_Data` WRITE;
/*!40000 ALTER TABLE `IoT_Data` DISABLE KEYS */;
/*!40000 ALTER TABLE `IoT_Data` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `IoT_IP`
--

DROP TABLE IF EXISTS `IoT_IP`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `IoT_IP` (
  `IoTID` varchar(8) NOT NULL,
  `IoTIP` varchar(32) NOT NULL,
  PRIMARY KEY (`IoTID`),
  UNIQUE KEY `IoTIP` (`IoTIP`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `IoT_IP`
--

LOCK TABLES `IoT_IP` WRITE;
/*!40000 ALTER TABLE `IoT_IP` DISABLE KEYS */;
/*!40000 ALTER TABLE `IoT_IP` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rollCall`
--

DROP TABLE IF EXISTS `rollCall`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rollCall` (
  `rollCallID` bigint unsigned NOT NULL AUTO_INCREMENT,
  `dormitoryID` tinyint unsigned NOT NULL,
  `studentID` varchar(8) NOT NULL,
  `day` date NOT NULL,
  `registeredStudentID` varchar(8) NOT NULL,
  `registeredTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`rollCallID`),
  UNIQUE KEY `dormitoryID` (`dormitoryID`,`day`,`studentID`),
  KEY `studentID` (`studentID`),
  KEY `registeredStudentID` (`registeredStudentID`),
  CONSTRAINT `rollcall_ibfk_1` FOREIGN KEY (`dormitoryID`) REFERENCES `dormitory` (`dormitoryID`) ON UPDATE CASCADE,
  CONSTRAINT `rollcall_ibfk_2` FOREIGN KEY (`studentID`) REFERENCES `student` (`studentID`) ON UPDATE CASCADE,
  CONSTRAINT `rollcall_ibfk_3` FOREIGN KEY (`registeredStudentID`) REFERENCES `student` (`studentID`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rollCall`
--

LOCK TABLES `rollCall` WRITE;
/*!40000 ALTER TABLE `rollCall` DISABLE KEYS */;
/*!40000 ALTER TABLE `rollCall` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student`
--

DROP TABLE IF EXISTS `student`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student` (
  `studentID` varchar(8) NOT NULL,
  `grade` tinyint unsigned NOT NULL,
  `courseID` tinyint unsigned NOT NULL,
  `name` varchar(128) NOT NULL,
  `pass` varchar(256) DEFAULT NULL,
  `access` tinyint(1) NOT NULL DEFAULT '0',
  `dormitoryPlaceID` tinyint unsigned DEFAULT NULL,
  `studentStatusID` tinyint unsigned NOT NULL DEFAULT '1',
  `wcma` tinyint unsigned NOT NULL DEFAULT '0',
  `mcma` tinyint unsigned NOT NULL DEFAULT '0',
  `scma` tinyint unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`studentID`),
  UNIQUE KEY `grade` (`grade`,`courseID`,`name`),
  KEY `courseID` (`courseID`),
  KEY `studentStatusID` (`studentStatusID`),
  KEY `dormitoryPlaceID` (`dormitoryPlaceID`),
  CONSTRAINT `student_ibfk_1` FOREIGN KEY (`courseID`) REFERENCES `courses` (`courseID`) ON UPDATE CASCADE,
  CONSTRAINT `student_ibfk_2` FOREIGN KEY (`studentStatusID`) REFERENCES `studentStatus` (`studentStatusID`) ON UPDATE CASCADE,
  CONSTRAINT `student_ibfk_3` FOREIGN KEY (`dormitoryPlaceID`) REFERENCES `dormitoryPlace` (`dormitoryPlaceID`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student`
--

LOCK TABLES `student` WRITE;
/*!40000 ALTER TABLE `student` DISABLE KEYS */;
/*!40000 ALTER TABLE `student` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `studentReport`
--

DROP TABLE IF EXISTS `studentReport`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `studentReport` (
  `cleaningID` bigint unsigned NOT NULL,
  `studentID` varchar(8) NOT NULL,
  `report` json NOT NULL,
  `reportedTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`cleaningID`),
  KEY `studentID` (`studentID`),
  CONSTRAINT `studentreport_ibfk_1` FOREIGN KEY (`studentID`) REFERENCES `student` (`studentID`) ON UPDATE CASCADE,
  CONSTRAINT `studentreport_ibfk_2` FOREIGN KEY (`cleaningID`) REFERENCES `cleaning` (`cleaningID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `studentReport`
--

LOCK TABLES `studentReport` WRITE;
/*!40000 ALTER TABLE `studentReport` DISABLE KEYS */;
/*!40000 ALTER TABLE `studentReport` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `studentStatus`
--

DROP TABLE IF EXISTS `studentStatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `studentStatus` (
  `studentStatusID` tinyint unsigned NOT NULL,
  `studentStatus` varchar(8) NOT NULL,
  PRIMARY KEY (`studentStatusID`),
  UNIQUE KEY `studentStatus` (`studentStatus`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `studentStatus`
--

LOCK TABLES `studentStatus` WRITE;
/*!40000 ALTER TABLE `studentStatus` DISABLE KEYS */;
INSERT INTO `studentStatus` VALUES (1,'exist'),(3,'retire'),(2,'stop');
/*!40000 ALTER TABLE `studentStatus` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teacher`
--

DROP TABLE IF EXISTS `teacher`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teacher` (
  `teacherID` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `pass` varchar(256) NOT NULL,
  PRIMARY KEY (`teacherID`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teacher`
--

LOCK TABLES `teacher` WRITE;
/*!40000 ALTER TABLE `teacher` DISABLE KEYS */;
/*!40000 ALTER TABLE `teacher` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teacherReport`
--

DROP TABLE IF EXISTS `teacherReport`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teacherReport` (
  `cleaningID` bigint unsigned NOT NULL,
  `teacherID` int unsigned NOT NULL,
  `report` json NOT NULL,
  `reportedTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`cleaningID`),
  KEY `teacherID` (`teacherID`),
  CONSTRAINT `teacherreport_ibfk_1` FOREIGN KEY (`cleaningID`) REFERENCES `studentReport` (`cleaningID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `teacherreport_ibfk_2` FOREIGN KEY (`teacherID`) REFERENCES `teacher` (`teacherID`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teacherReport`
--

LOCK TABLES `teacherReport` WRITE;
/*!40000 ALTER TABLE `teacherReport` DISABLE KEYS */;
/*!40000 ALTER TABLE `teacherReport` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-01-26 13:04:20
