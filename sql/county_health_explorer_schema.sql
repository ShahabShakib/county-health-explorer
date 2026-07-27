-- County Health Explorer
-- Database Schema
-- Author: Shahab Shakib
-- Purpose: Defines the database tables, relationships, constraints, indexes, and views used by the County Health Explorer.

CREATE DATABASE  IF NOT EXISTS `mydb` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `mydb`;
-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: mydb
-- ------------------------------------------------------
-- Server version	5.7.24

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
-- Table structure for table `category`
--

DROP TABLE IF EXISTS `category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `category` (
  `category_id` int(11) NOT NULL AUTO_INCREMENT,
  `category_name` varchar(100) NOT NULL,
  PRIMARY KEY (`category_id`),
  UNIQUE KEY `category_name_UNIQUE` (`category_name`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `county`
--

DROP TABLE IF EXISTS `county`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `county` (
  `county_id` int(11) NOT NULL AUTO_INCREMENT,
  `location_id` varchar(5) NOT NULL,
  `county_name` varchar(150) NOT NULL,
  `state_id` int(11) NOT NULL,
  `total_population` int(11) DEFAULT NULL,
  `total_pop_18plus` int(11) DEFAULT NULL,
  `latitude` decimal(9,6) DEFAULT NULL,
  `longitude` decimal(9,6) DEFAULT NULL,
  PRIMARY KEY (`county_id`),
  UNIQUE KEY `location_id_UNIQUE` (`location_id`),
  KEY `fk_County_State1_idx` (`state_id`),
  CONSTRAINT `fk_County_State1` FOREIGN KEY (`state_id`) REFERENCES `state` (`state_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=3145 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `countyhealthrecord`
--

DROP TABLE IF EXISTS `countyhealthrecord`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `countyhealthrecord` (
  `record_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `county_id` int(11) NOT NULL,
  `measure_id` varchar(50) NOT NULL,
  `data_value_type_id` varchar(20) NOT NULL,
  `year` smallint(6) NOT NULL,
  `data_source` varchar(50) DEFAULT NULL,
  `data_value` decimal(6,2) DEFAULT NULL,
  `low_confidence_limit` decimal(6,2) DEFAULT NULL,
  `high_confidence_limit` decimal(6,2) DEFAULT NULL,
  PRIMARY KEY (`record_id`),
  UNIQUE KEY `uq_county_measure_type_year` (`county_id`,`measure_id`,`data_value_type_id`,`year`),
  KEY `fk_CountyHealthRecord_Measure1_idx` (`measure_id`),
  KEY `fk_CountyHealthRecord_DataValueType1_idx` (`data_value_type_id`),
  KEY `fk_CountyHealthRecord_County1_idx` (`county_id`),
  CONSTRAINT `fk_CountyHealthRecord_County1` FOREIGN KEY (`county_id`) REFERENCES `county` (`county_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_CountyHealthRecord_DataValueType1` FOREIGN KEY (`data_value_type_id`) REFERENCES `datavaluetype` (`data_value_type_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_CountyHealthRecord_Measure1` FOREIGN KEY (`measure_id`) REFERENCES `measure` (`measure_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=229219 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datavaluetype`
--

DROP TABLE IF EXISTS `datavaluetype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `datavaluetype` (
  `data_value_type_id` varchar(20) NOT NULL,
  `data_value_type_name` varchar(100) NOT NULL,
  `data_value_unit` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`data_value_type_id`),
  UNIQUE KEY `data_value_type_name_UNIQUE` (`data_value_type_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `measure`
--

DROP TABLE IF EXISTS `measure`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `measure` (
  `measure_id` varchar(50) NOT NULL,
  `measure_name` varchar(500) NOT NULL,
  `short_question_text` varchar(255) DEFAULT NULL,
  `category_id` int(11) NOT NULL,
  PRIMARY KEY (`measure_id`),
  KEY `fk_Measure_Category1_idx` (`category_id`),
  CONSTRAINT `fk_Measure_Category1` FOREIGN KEY (`category_id`) REFERENCES `category` (`category_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `places_county_staging`
--

DROP TABLE IF EXISTS `places_county_staging`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `places_county_staging` (
  `Year` int(11) DEFAULT NULL,
  `StateAbbr` varchar(10) DEFAULT NULL,
  `StateDesc` varchar(100) DEFAULT NULL,
  `LocationName` varchar(150) DEFAULT NULL,
  `DataSource` varchar(50) DEFAULT NULL,
  `Category` varchar(150) DEFAULT NULL,
  `Measure` varchar(500) DEFAULT NULL,
  `Data_Value_Unit` varchar(20) DEFAULT NULL,
  `Data_Value_Type` varchar(100) DEFAULT NULL,
  `Data_Value` varchar(50) DEFAULT NULL,
  `Data_Value_Footnote_Symbol` varchar(20) DEFAULT NULL,
  `Data_Value_Footnote` text,
  `Low_Confidence_Limit` varchar(50) DEFAULT NULL,
  `High_Confidence_Limit` varchar(50) DEFAULT NULL,
  `TotalPopulation` varchar(50) DEFAULT NULL,
  `TotalPop18plus` varchar(50) DEFAULT NULL,
  `LocationID` varchar(10) DEFAULT NULL,
  `CategoryID` varchar(50) DEFAULT NULL,
  `MeasureId` varchar(100) DEFAULT NULL,
  `DataValueTypeID` varchar(50) DEFAULT NULL,
  `Short_Question_Text` varchar(255) DEFAULT NULL,
  `Geolocation` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `state`
--

DROP TABLE IF EXISTS `state`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `state` (
  `state_id` int(11) NOT NULL AUTO_INCREMENT,
  `state_abbr` varchar(2) NOT NULL,
  `state_name` varchar(100) NOT NULL,
  PRIMARY KEY (`state_id`),
  UNIQUE KEY `state_abbr_UNIQUE` (`state_abbr`)
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `usernote`
--

DROP TABLE IF EXISTS `usernote`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usernote` (
  `note_id` int(11) NOT NULL AUTO_INCREMENT,
  `county_id` int(11) NOT NULL,
  `measure_id` varchar(50) DEFAULT NULL,
  `note_text` text NOT NULL,
  `priority_level` enum('Low','Medium','High') DEFAULT NULL,
  `status` enum('Open','In Progress','Closed') DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`note_id`),
  KEY `fk_UserNote_Measure1_idx` (`measure_id`),
  KEY `fk_UserNote_County1_idx` (`county_id`),
  CONSTRAINT `fk_UserNote_County1` FOREIGN KEY (`county_id`) REFERENCES `county` (`county_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_UserNote_Measure1` FOREIGN KEY (`measure_id`) REFERENCES `measure` (`measure_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `vw_county_health_details`
--

DROP TABLE IF EXISTS `vw_county_health_details`;
/*!50001 DROP VIEW IF EXISTS `vw_county_health_details`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vw_county_health_details` AS SELECT 
 1 AS `record_id`,
 1 AS `year`,
 1 AS `state_abbr`,
 1 AS `state_name`,
 1 AS `location_id`,
 1 AS `county_name`,
 1 AS `total_population`,
 1 AS `total_pop_18plus`,
 1 AS `latitude`,
 1 AS `longitude`,
 1 AS `category_name`,
 1 AS `measure_id`,
 1 AS `measure_name`,
 1 AS `short_question_text`,
 1 AS `data_value_type_name`,
 1 AS `data_value_unit`,
 1 AS `data_source`,
 1 AS `data_value`,
 1 AS `low_confidence_limit`,
 1 AS `high_confidence_limit`*/;
SET character_set_client = @saved_cs_client;

--
-- Final view structure for view `vw_county_health_details`
--

/*!50001 DROP VIEW IF EXISTS `vw_county_health_details`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 SQL SECURITY INVOKER */
/*!50001 VIEW `vw_county_health_details` AS select `chr`.`record_id` AS `record_id`,`chr`.`year` AS `year`,`s`.`state_abbr` AS `state_abbr`,`s`.`state_name` AS `state_name`,`c`.`location_id` AS `location_id`,`c`.`county_name` AS `county_name`,`c`.`total_population` AS `total_population`,`c`.`total_pop_18plus` AS `total_pop_18plus`,`c`.`latitude` AS `latitude`,`c`.`longitude` AS `longitude`,`cat`.`category_name` AS `category_name`,`m`.`measure_id` AS `measure_id`,`m`.`measure_name` AS `measure_name`,`m`.`short_question_text` AS `short_question_text`,`dvt`.`data_value_type_name` AS `data_value_type_name`,`dvt`.`data_value_unit` AS `data_value_unit`,`chr`.`data_source` AS `data_source`,`chr`.`data_value` AS `data_value`,`chr`.`low_confidence_limit` AS `low_confidence_limit`,`chr`.`high_confidence_limit` AS `high_confidence_limit` from (((((`countyhealthrecord` `chr` join `county` `c` on((`chr`.`county_id` = `c`.`county_id`))) join `state` `s` on((`c`.`state_id` = `s`.`state_id`))) join `measure` `m` on((`chr`.`measure_id` = `m`.`measure_id`))) join `category` `cat` on((`m`.`category_id` = `cat`.`category_id`))) join `datavaluetype` `dvt` on((`chr`.`data_value_type_id` = `dvt`.`data_value_type_id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-07-26 14:51:41
