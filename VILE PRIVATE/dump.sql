-- MariaDB dump 10.19  Distrib 10.6.12-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: vilebot
-- ------------------------------------------------------
-- Server version	10.6.12-MariaDB-0ubuntu0.22.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `vilebot`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `vilebot` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;

USE `vilebot`;

--
-- Table structure for table `afk`
--

DROP TABLE IF EXISTS `afk`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `afk` (
  `guild_id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `status` varchar(512) DEFAULT NULL,
  `left_at` datetime DEFAULT NULL,
  PRIMARY KEY (`guild_id`,`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `afk`
--

LOCK TABLES `afk` WRITE;
/*!40000 ALTER TABLE `afk` DISABLE KEYS */;
/*!40000 ALTER TABLE `afk` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `album_image_cache`
--

DROP TABLE IF EXISTS `album_image_cache`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `album_image_cache` (
  `artist_name` varchar(255) NOT NULL,
  `album_name` varchar(255) NOT NULL,
  `image_hash` varchar(32) DEFAULT NULL,
  `scrape_date` datetime DEFAULT NULL,
  PRIMARY KEY (`artist_name`,`album_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `album_image_cache`
--

LOCK TABLES `album_image_cache` WRITE;
/*!40000 ALTER TABLE `album_image_cache` DISABLE KEYS */;
/*!40000 ALTER TABLE `album_image_cache` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `aliases`
--

DROP TABLE IF EXISTS `aliases`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `aliases` (
  `guild_id` bigint(20) NOT NULL,
  `command_name` varchar(64) NOT NULL,
  `alias` varchar(64) NOT NULL,
  PRIMARY KEY (`guild_id`,`command_name`,`alias`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `aliases`
--

LOCK TABLES `aliases` WRITE;
/*!40000 ALTER TABLE `aliases` DISABLE KEYS */;
/*!40000 ALTER TABLE `aliases` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `artist_crown`
--

DROP TABLE IF EXISTS `artist_crown`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `artist_crown` (
  `guild_id` bigint(20) NOT NULL,
  `user_id` bigint(20) DEFAULT NULL,
  `artist_name` varchar(256) NOT NULL,
  `cached_playcount` int(11) DEFAULT NULL,
  PRIMARY KEY (`guild_id`,`artist_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `artist_crown`
--

LOCK TABLES `artist_crown` WRITE;
/*!40000 ALTER TABLE `artist_crown` DISABLE KEYS */;
/*!40000 ALTER TABLE `artist_crown` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `artist_image_cache`
--

DROP TABLE IF EXISTS `artist_image_cache`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `artist_image_cache` (
  `artist_name` varchar(255) NOT NULL,
  `image_hash` varchar(32) DEFAULT NULL,
  `scrape_date` datetime DEFAULT NULL,
  PRIMARY KEY (`artist_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `artist_image_cache`
--

LOCK TABLES `artist_image_cache` WRITE;
/*!40000 ALTER TABLE `artist_image_cache` DISABLE KEYS */;
/*!40000 ALTER TABLE `artist_image_cache` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `autoreact`
--

DROP TABLE IF EXISTS `autoreact`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `autoreact` (
  `guild_id` bigint(20) NOT NULL,
  `keyword` varchar(32) NOT NULL,
  `reaction` varchar(128) NOT NULL,
  PRIMARY KEY (`guild_id`,`keyword`,`reaction`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `autoreact`
--

LOCK TABLES `autoreact` WRITE;
/*!40000 ALTER TABLE `autoreact` DISABLE KEYS */;
/*!40000 ALTER TABLE `autoreact` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `autoreact_event`
--

DROP TABLE IF EXISTS `autoreact_event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `autoreact_event` (
  `guild_id` bigint(20) NOT NULL,
  `event` varchar(32) NOT NULL,
  `reaction` varchar(128) NOT NULL,
  PRIMARY KEY (`guild_id`,`event`,`reaction`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `autoreact_event`
--

LOCK TABLES `autoreact_event` WRITE;
/*!40000 ALTER TABLE `autoreact_event` DISABLE KEYS */;
INSERT INTO `autoreact_event` VALUES (1031650118375571537,'images','🤮'),(1053462941996953650,'images','👏'),(1111324554212683857,'images','🤮');
/*!40000 ALTER TABLE `autoreact_event` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `autoresponder`
--

DROP TABLE IF EXISTS `autoresponder`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `autoresponder` (
  `guild_id` bigint(20) NOT NULL,
  `keyword` varchar(32) NOT NULL,
  `response` varchar(1024) NOT NULL,
  `created_by` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`guild_id`,`keyword`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `autoresponder`
--

LOCK TABLES `autoresponder` WRITE;
/*!40000 ALTER TABLE `autoresponder` DISABLE KEYS */;
INSERT INTO `autoresponder` VALUES (936316939322654840,'hi','{content: ok}',1109861649910874274),(1114533132893438063,'penis','{content: test}',249769117194649612);
/*!40000 ALTER TABLE `autoresponder` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `autoresponder_event`
--

DROP TABLE IF EXISTS `autoresponder_event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `autoresponder_event` (
  `guild_id` bigint(20) NOT NULL,
  `event` varchar(32) NOT NULL,
  `response` varchar(1024) NOT NULL,
  PRIMARY KEY (`guild_id`,`event`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `autoresponder_event`
--

LOCK TABLES `autoresponder_event` WRITE;
/*!40000 ALTER TABLE `autoresponder_event` DISABLE KEYS */;
INSERT INTO `autoresponder_event` VALUES (1031650118375571537,'images','{content: ur ugly}'),(1053462941996953650,'images','{content: suck}'),(1111324554212683857,'images','{content: ew}');
/*!40000 ALTER TABLE `autoresponder_event` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `autorole`
--

DROP TABLE IF EXISTS `autorole`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `autorole` (
  `guild_id` bigint(20) NOT NULL,
  `role_id` bigint(20) NOT NULL,
  PRIMARY KEY (`guild_id`,`role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `autorole`
--

LOCK TABLES `autorole` WRITE;
/*!40000 ALTER TABLE `autorole` DISABLE KEYS */;
/*!40000 ALTER TABLE `autorole` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `blacklisted_command`
--

DROP TABLE IF EXISTS `blacklisted_command`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `blacklisted_command` (
  `guild_id` bigint(20) NOT NULL,
  `command_name` varchar(32) NOT NULL,
  PRIMARY KEY (`guild_id`,`command_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `blacklisted_command`
--

LOCK TABLES `blacklisted_command` WRITE;
/*!40000 ALTER TABLE `blacklisted_command` DISABLE KEYS */;
/*!40000 ALTER TABLE `blacklisted_command` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `blacklisted_object`
--

DROP TABLE IF EXISTS `blacklisted_object`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `blacklisted_object` (
  `object_id` bigint(20) NOT NULL,
  `reason` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`object_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `blacklisted_object`
--

LOCK TABLES `blacklisted_object` WRITE;
/*!40000 ALTER TABLE `blacklisted_object` DISABLE KEYS */;
INSERT INTO `blacklisted_object` VALUES (236931919063941121,'Copying Vile\'s services or features'),(994896336040239114,'Abusing or exploiting Vile bot'),(1078962964662591528,'Abusing or exploiting Vile bot'),(1105886170300301345,'Abusing or exploiting Vile bot'),(1108028507243687956,'Abusing or exploiting Vile bot');
/*!40000 ALTER TABLE `blacklisted_object` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `boost_settings`
--

DROP TABLE IF EXISTS `boost_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `boost_settings` (
  `guild_id` bigint(20) NOT NULL,
  `channel_id` bigint(20) DEFAULT NULL,
  `is_enabled` tinyint(1) DEFAULT 1,
  `message` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`guild_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `boost_settings`
--

LOCK TABLES `boost_settings` WRITE;
/*!40000 ALTER TABLE `boost_settings` DISABLE KEYS */;
INSERT INTO `boost_settings` VALUES (1053462941996953650,1096134879894306946,1,'{content: suck my dick}'),(1109535888431661249,1109536110251610236,1,'{user.mention} ty daddy 😝😝');
/*!40000 ALTER TABLE `boost_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `booster_role`
--

DROP TABLE IF EXISTS `booster_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `booster_role` (
  `guild_id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `role_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`guild_id`,`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `booster_role`
--

LOCK TABLES `booster_role` WRITE;
/*!40000 ALTER TABLE `booster_role` DISABLE KEYS */;
/*!40000 ALTER TABLE `booster_role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `booster_role_award`
--

DROP TABLE IF EXISTS `booster_role_award`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `booster_role_award` (
  `guild_id` bigint(20) NOT NULL,
  `role_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`guild_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `booster_role_award`
--

LOCK TABLES `booster_role_award` WRITE;
/*!40000 ALTER TABLE `booster_role_award` DISABLE KEYS */;
/*!40000 ALTER TABLE `booster_role_award` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `booster_role_base`
--

DROP TABLE IF EXISTS `booster_role_base`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `booster_role_base` (
  `guild_id` bigint(20) NOT NULL,
  `role_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`guild_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `booster_role_base`
--

LOCK TABLES `booster_role_base` WRITE;
/*!40000 ALTER TABLE `booster_role_base` DISABLE KEYS */;
/*!40000 ALTER TABLE `booster_role_base` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `chatgpt_usage`
--

DROP TABLE IF EXISTS `chatgpt_usage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `chatgpt_usage` (
  `user_id` bigint(20) NOT NULL,
  `uses` int(11) DEFAULT 1,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `chatgpt_usage`
--

LOCK TABLES `chatgpt_usage` WRITE;
/*!40000 ALTER TABLE `chatgpt_usage` DISABLE KEYS */;
/*!40000 ALTER TABLE `chatgpt_usage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clownboard_settings`
--

DROP TABLE IF EXISTS `clownboard_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `clownboard_settings` (
  `guild_id` bigint(20) NOT NULL,
  `channel_id` bigint(20) DEFAULT NULL,
  `is_enabled` tinyint(1) DEFAULT 1,
  `attachments_allowed` tinyint(1) DEFAULT 1,
  `selfclown_allowed` tinyint(1) DEFAULT 1,
  `show_jumpurl` tinyint(1) DEFAULT 1,
  `embed_color` int(11) DEFAULT 11643608,
  `show_timestamp` tinyint(1) DEFAULT 1,
  `reaction_count` int(11) DEFAULT 3,
  `emoji_name` varchar(64) NOT NULL DEFAULT 'U0001F921',
  `emoji_id` bigint(20) DEFAULT NULL,
  `emoji_type` enum('unicode','custom') NOT NULL DEFAULT 'unicode',
  PRIMARY KEY (`guild_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clownboard_settings`
--

LOCK TABLES `clownboard_settings` WRITE;
/*!40000 ALTER TABLE `clownboard_settings` DISABLE KEYS */;
/*!40000 ALTER TABLE `clownboard_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `command_usage`
--

DROP TABLE IF EXISTS `command_usage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `command_usage` (
  `user_id` bigint(20) NOT NULL,
  `command_name` varchar(64) NOT NULL,
  `uses` int(11) DEFAULT 1,
  PRIMARY KEY (`user_id`,`command_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `command_usage`
--

LOCK TABLES `command_usage` WRITE;
/*!40000 ALTER TABLE `command_usage` DISABLE KEYS */;
INSERT INTO `command_usage` VALUES (205500294308560896,'boost',2),(205500294308560896,'boost add',1),(205500294308560896,'boost toggle',1),(205500294308560896,'help',1),(249769117194649612,'autoresponder',2),(249769117194649612,'autoresponder add',1),(249769117194649612,'evaluate javascript',1),(249769117194649612,'help',1),(249769117194649612,'jishaku py',1),(288748368497344513,'help',1),(288748368497344513,'welcome',1),(352190010998390796,'cum',1),(352190010998390796,'evaluate',3),(352190010998390796,'evaluate javascript',16),(352190010998390796,'evaluate lolcode',1),(352190010998390796,'evaluate rust',1),(352190010998390796,'help',2),(352190010998390796,'jishaku',1),(352190010998390796,'jishaku py',2),(352190010998390796,'jishaku shell',3),(352190010998390796,'pin',1),(371224177186963460,'filter',1),(371224177186963460,'filter add',1),(371224177186963460,'filter list',1),(371224177186963460,'filter spam',1),(371224177186963460,'help',2),(371224177186963460,'welcome remove',2),(461914901624127489,'evaluate',6),(461914901624127489,'evaluate javascript',22),(461914901624127489,'evaluate lolcode',9),(461914901624127489,'evaluate rust',24),(461914901624127489,'help',2),(461914901624127489,'jishaku',1),(461914901624127489,'jishaku debug',1),(461914901624127489,'jishaku node',8),(461914901624127489,'jishaku shell',11),(461914901624127489,'welcome',23),(490066410748248065,'cum',2),(574429626085015573,'welcome variables',6),(597696521718333445,'cum',1),(597696521718333445,'help',1),(742261436209692672,'welcome',222),(812126383077457921,'autoresponder variables',71),(812126383077457921,'welcome',12),(817619310373109761,'evaluate',7),(817619310373109761,'evaluate bash',1),(817619310373109761,'evaluate javascript',5),(817619310373109761,'evaluate lolcode',1),(817619310373109761,'evaluate rust',1),(859646668672598017,'help',1),(923175161350455336,'filter',1),(923175161350455336,'jishaku cat',3),(979978940707930143,'help',1),(1002322857604419604,'evaluate',148),(1002322857604419604,'evaluate bash',37),(1002322857604419604,'evaluate javascript',20),(1002322857604419604,'evaluate lolcode',3),(1002322857604419604,'evaluate rust',48),(1002322857604419604,'fakepermissions',9),(1002322857604419604,'help',5),(1002322857604419604,'jishaku',4),(1002322857604419604,'jishaku cancel',1),(1002322857604419604,'jishaku curl',3),(1002322857604419604,'jishaku debug',34),(1002322857604419604,'jishaku load',18),(1002322857604419604,'jishaku node',2),(1002322857604419604,'jishaku override',17),(1002322857604419604,'jishaku py',64),(1002322857604419604,'jishaku rustc',5),(1002322857604419604,'jishaku shell',81),(1002322857604419604,'prefix',1),(1002322857604419604,'prefix set',1),(1002322857604419604,'webhook create',1),(1002322857604419604,'webhook list',2),(1002322857604419604,'webhook send',4),(1002322857604419604,'welcome',11),(1055581756864077896,'help',1),(1104528798134841475,'help',2),(1104528798134841475,'prefix set',1),(1108028507243687956,'help',36),(1108880726792863824,'help',1),(1109861649910874274,'autoreact',1),(1109861649910874274,'autoreact add',1),(1109861649910874274,'autoreact add images',11),(1109861649910874274,'autoreact add stickers',1),(1109861649910874274,'autoreact clear',9),(1109861649910874274,'autoreact list',21),(1109861649910874274,'autoreact remove images',2),(1109861649910874274,'autoresponder',2),(1109861649910874274,'autoresponder add',1),(1109861649910874274,'autoresponder add images',8),(1109861649910874274,'autoresponder clear',2),(1109861649910874274,'autoresponder list',7),(1109861649910874274,'autoresponder remove images',1),(1109861649910874274,'boost add',1),(1109861649910874274,'cum',1),(1109861649910874274,'customprefix',1),(1109861649910874274,'customprefix remove',1),(1109861649910874274,'customprefix set',1),(1109861649910874274,'data',2),(1109861649910874274,'data request',7),(1109861649910874274,'evaluate',49),(1109861649910874274,'evaluate javascript',14),(1109861649910874274,'evaluate lolcode',1),(1109861649910874274,'evaluate rust',1),(1109861649910874274,'extract',1),(1109861649910874274,'extract emojis',5),(1109861649910874274,'extract stickers',1),(1109861649910874274,'filter',2),(1109861649910874274,'filter add',2),(1109861649910874274,'filter spam',7),(1109861649910874274,'filter spoilers',1),(1109861649910874274,'help',180),(1109861649910874274,'jishaku',31),(1109861649910874274,'jishaku cancel',1),(1109861649910874274,'jishaku cat',2),(1109861649910874274,'jishaku debug',57),(1109861649910874274,'jishaku load',21),(1109861649910874274,'jishaku node',1),(1109861649910874274,'jishaku override',8),(1109861649910874274,'jishaku py',1019),(1109861649910874274,'jishaku repeat',8),(1109861649910874274,'jishaku rtt',2),(1109861649910874274,'jishaku shell',327),(1109861649910874274,'kick',5),(1109861649910874274,'leave',3),(1109861649910874274,'pagination',1),(1109861649910874274,'pagination add',46),(1109861649910874274,'pagination list',4),(1109861649910874274,'pagination reset',1),(1109861649910874274,'pagination restorereactions',1),(1109861649910874274,'pin',9),(1109861649910874274,'set',1),(1109861649910874274,'set icon',13),(1109861649910874274,'tempban',36),(1109861649910874274,'test',2),(1109861649910874274,'unpin',1),(1109861649910874274,'warn',6),(1109861649910874274,'webhook create',1),(1109861649910874274,'welcome',11),(1109861649910874274,'welcome add',1),(1109861649910874274,'welcome variables',2),(1110188890989527040,'help',1);
/*!40000 ALTER TABLE `command_usage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `custom_prefix`
--

DROP TABLE IF EXISTS `custom_prefix`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `custom_prefix` (
  `user_id` bigint(20) NOT NULL,
  `prefix` varchar(32) NOT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `custom_prefix`
--

LOCK TABLES `custom_prefix` WRITE;
/*!40000 ALTER TABLE `custom_prefix` DISABLE KEYS */;
/*!40000 ALTER TABLE `custom_prefix` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `disabled_feature`
--

DROP TABLE IF EXISTS `disabled_feature`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `disabled_feature` (
  `guild_id` bigint(20) NOT NULL,
  `name` varchar(64) NOT NULL,
  `type` enum('module','command') NOT NULL,
  PRIMARY KEY (`guild_id`,`name`,`type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `disabled_feature`
--

LOCK TABLES `disabled_feature` WRITE;
/*!40000 ALTER TABLE `disabled_feature` DISABLE KEYS */;
/*!40000 ALTER TABLE `disabled_feature` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `donator`
--

DROP TABLE IF EXISTS `donator`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `donator` (
  `user_id` bigint(20) NOT NULL,
  `donation_tier` tinyint(4) DEFAULT NULL,
  `total_donated` float DEFAULT 0,
  `donating_since` datetime DEFAULT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `donator`
--

LOCK TABLES `donator` WRITE;
/*!40000 ALTER TABLE `donator` DISABLE KEYS */;
/*!40000 ALTER TABLE `donator` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fake_permissions`
--

DROP TABLE IF EXISTS `fake_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fake_permissions` (
  `guild_id` bigint(20) DEFAULT NULL,
  `role_id` bigint(20) NOT NULL,
  `permission` varchar(64) NOT NULL,
  PRIMARY KEY (`role_id`,`permission`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fake_permissions`
--

LOCK TABLES `fake_permissions` WRITE;
/*!40000 ALTER TABLE `fake_permissions` DISABLE KEYS */;
INSERT INTO `fake_permissions` VALUES (936316939322654840,1059994644882132992,'moderate_members');
/*!40000 ALTER TABLE `fake_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `filter`
--

DROP TABLE IF EXISTS `filter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `filter` (
  `guild_id` bigint(20) NOT NULL,
  `keyword` varchar(32) NOT NULL,
  PRIMARY KEY (`guild_id`,`keyword`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `filter`
--

LOCK TABLES `filter` WRITE;
/*!40000 ALTER TABLE `filter` DISABLE KEYS */;
INSERT INTO `filter` VALUES (936316939322654840,'cool'),(936316939322654840,'suck'),(1112077903744741476,'lumy');
/*!40000 ALTER TABLE `filter` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `filter_event`
--

DROP TABLE IF EXISTS `filter_event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `filter_event` (
  `guild_id` bigint(20) NOT NULL,
  `event` varchar(32) NOT NULL,
  `is_enabled` tinyint(1) DEFAULT 1,
  `threshold` tinyint(4) DEFAULT 2,
  PRIMARY KEY (`guild_id`,`event`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `filter_event`
--

LOCK TABLES `filter_event` WRITE;
/*!40000 ALTER TABLE `filter_event` DISABLE KEYS */;
INSERT INTO `filter_event` VALUES (936316939322654840,'spam',0,3),(1053462941996953650,'spam',1,5),(1111324554212683857,'spam',1,5),(1112077903744741476,'spam',0,3);
/*!40000 ALTER TABLE `filter_event` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `filter_snipe`
--

DROP TABLE IF EXISTS `filter_snipe`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `filter_snipe` (
  `guild_id` bigint(20) NOT NULL,
  `invites` tinyint(1) DEFAULT 0,
  `links` tinyint(1) DEFAULT 0,
  `images` tinyint(1) DEFAULT 0,
  `words` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`guild_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `filter_snipe`
--

LOCK TABLES `filter_snipe` WRITE;
/*!40000 ALTER TABLE `filter_snipe` DISABLE KEYS */;
/*!40000 ALTER TABLE `filter_snipe` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `filter_whitelist`
--

DROP TABLE IF EXISTS `filter_whitelist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `filter_whitelist` (
  `guild_id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`guild_id`,`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `filter_whitelist`
--

LOCK TABLES `filter_whitelist` WRITE;
/*!40000 ALTER TABLE `filter_whitelist` DISABLE KEYS */;
/*!40000 ALTER TABLE `filter_whitelist` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `guild_prefix`
--

DROP TABLE IF EXISTS `guild_prefix`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `guild_prefix` (
  `guild_id` bigint(20) NOT NULL,
  `prefix` varchar(32) NOT NULL,
  PRIMARY KEY (`guild_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `guild_prefix`
--

LOCK TABLES `guild_prefix` WRITE;
/*!40000 ALTER TABLE `guild_prefix` DISABLE KEYS */;
INSERT INTO `guild_prefix` VALUES (936316939322654840,'.'),(1108884290877522040,';');
/*!40000 ALTER TABLE `guild_prefix` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `guild_settings`
--

DROP TABLE IF EXISTS `guild_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `guild_settings` (
  `guild_id` bigint(20) NOT NULL,
  `mute_role_id` bigint(20) DEFAULT NULL,
  `levelup_messages` tinyint(1) DEFAULT 0,
  `autoresponses` tinyint(1) DEFAULT 1,
  `restrict_custom_commands` tinyint(1) DEFAULT 0,
  `delete_blacklisted_usage` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`guild_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `guild_settings`
--

LOCK TABLES `guild_settings` WRITE;
/*!40000 ALTER TABLE `guild_settings` DISABLE KEYS */;
/*!40000 ALTER TABLE `guild_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ignore_object`
--

DROP TABLE IF EXISTS `ignore_object`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ignore_object` (
  `guild_id` bigint(20) NOT NULL,
  `object_id` bigint(20) NOT NULL,
  `type` enum('member','channel','role') DEFAULT NULL,
  PRIMARY KEY (`guild_id`,`object_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ignore_object`
--

LOCK TABLES `ignore_object` WRITE;
/*!40000 ALTER TABLE `ignore_object` DISABLE KEYS */;
/*!40000 ALTER TABLE `ignore_object` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `image_color_cache`
--

DROP TABLE IF EXISTS `image_color_cache`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `image_color_cache` (
  `image_hash` varchar(32) NOT NULL,
  `color` int(11) NOT NULL,
  `hex` varchar(6) NOT NULL,
  PRIMARY KEY (`image_hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `image_color_cache`
--

LOCK TABLES `image_color_cache` WRITE;
/*!40000 ALTER TABLE `image_color_cache` DISABLE KEYS */;
INSERT INTO `image_color_cache` VALUES ('00d9039a5bb151e8',986895,'f0f0f'),('136f8adc0c6cf513',2170163,'211d33'),('2d89dee8e1e11598',394767,'6060f'),('3bc6df4b4e9cfa9a',0,'0'),('7155de0174f562ef',0,'0'),('a790fde3473cf3a6',1842204,'1c1c1c'),('c0fb6257a7c0a06f',1778484,'1b2334'),('c4fa29ac124f9b42',2765421,'2a326d'),('c75d91d140628c21',16446708,'faf4f4'),('e42aecdb727b64a8',7232846,'6e5d4e');
/*!40000 ALTER TABLE `image_color_cache` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `invoke_message`
--

DROP TABLE IF EXISTS `invoke_message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `invoke_message` (
  `guild_id` bigint(20) NOT NULL,
  `command_name` varchar(64) NOT NULL,
  `message` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`guild_id`,`command_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invoke_message`
--

LOCK TABLES `invoke_message` WRITE;
/*!40000 ALTER TABLE `invoke_message` DISABLE KEYS */;
/*!40000 ALTER TABLE `invoke_message` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lastfm_vote_setting`
--

DROP TABLE IF EXISTS `lastfm_vote_setting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `lastfm_vote_setting` (
  `user_id` bigint(20) NOT NULL,
  `is_enabled` tinyint(1) DEFAULT 1,
  `upvote_emoji` varchar(128) DEFAULT NULL,
  `downvote_emoji` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lastfm_vote_setting`
--

LOCK TABLES `lastfm_vote_setting` WRITE;
/*!40000 ALTER TABLE `lastfm_vote_setting` DISABLE KEYS */;
/*!40000 ALTER TABLE `lastfm_vote_setting` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `leave_settings`
--

DROP TABLE IF EXISTS `leave_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `leave_settings` (
  `guild_id` bigint(20) NOT NULL,
  `channel_id` bigint(20) DEFAULT NULL,
  `is_enabled` tinyint(1) DEFAULT 1,
  `message` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`guild_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `leave_settings`
--

LOCK TABLES `leave_settings` WRITE;
/*!40000 ALTER TABLE `leave_settings` DISABLE KEYS */;
/*!40000 ALTER TABLE `leave_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `logging_settings`
--

DROP TABLE IF EXISTS `logging_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `logging_settings` (
  `guild_id` bigint(20) NOT NULL,
  `member_log_channel_id` bigint(20) DEFAULT NULL,
  `ban_log_channel_id` bigint(20) DEFAULT NULL,
  `message_log_channel_id` bigint(20) DEFAULT NULL,
  `error_log_channel_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`guild_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `logging_settings`
--

LOCK TABLES `logging_settings` WRITE;
/*!40000 ALTER TABLE `logging_settings` DISABLE KEYS */;
/*!40000 ALTER TABLE `logging_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `marriage`
--

DROP TABLE IF EXISTS `marriage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `marriage` (
  `first_user_id` bigint(20) NOT NULL,
  `second_user_id` bigint(20) NOT NULL,
  `marriage_date` datetime DEFAULT NULL,
  PRIMARY KEY (`first_user_id`,`second_user_id`),
  UNIQUE KEY `first_user_id` (`first_user_id`),
  UNIQUE KEY `second_user_id` (`second_user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `marriage`
--

LOCK TABLES `marriage` WRITE;
/*!40000 ALTER TABLE `marriage` DISABLE KEYS */;
/*!40000 ALTER TABLE `marriage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `media_auto_embed_settings`
--

DROP TABLE IF EXISTS `media_auto_embed_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `media_auto_embed_settings` (
  `guild_id` bigint(20) NOT NULL,
  `medal` tinyint(1) DEFAULT 1,
  `twitter` tinyint(1) DEFAULT 1,
  `tiktok` tinyint(1) DEFAULT 1,
  `soundcloud` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`guild_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `media_auto_embed_settings`
--

LOCK TABLES `media_auto_embed_settings` WRITE;
/*!40000 ALTER TABLE `media_auto_embed_settings` DISABLE KEYS */;
/*!40000 ALTER TABLE `media_auto_embed_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `message_log_ignore`
--

DROP TABLE IF EXISTS `message_log_ignore`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `message_log_ignore` (
  `guild_id` bigint(20) DEFAULT NULL,
  `channel_id` bigint(20) NOT NULL,
  PRIMARY KEY (`channel_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `message_log_ignore`
--

LOCK TABLES `message_log_ignore` WRITE;
/*!40000 ALTER TABLE `message_log_ignore` DISABLE KEYS */;
/*!40000 ALTER TABLE `message_log_ignore` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `moderation_history`
--

DROP TABLE IF EXISTS `moderation_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `moderation_history` (
  `guild_id` bigint(20) NOT NULL,
  `moderator_id` bigint(20) NOT NULL,
  `member_id` bigint(20) NOT NULL,
  `type` varchar(64) DEFAULT NULL,
  `reason` varchar(256) DEFAULT NULL,
  `created_on` datetime NOT NULL,
  `case_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`guild_id`,`moderator_id`,`member_id`,`created_on`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `moderation_history`
--

LOCK TABLES `moderation_history` WRITE;
/*!40000 ALTER TABLE `moderation_history` DISABLE KEYS */;
INSERT INTO `moderation_history` VALUES (936316939322654840,1109861649910874274,235148962103951360,'Warn','No reason provided','2023-06-07 00:18:48',4),(936316939322654840,1109861649910874274,235148962103951360,'Warn','dumb bot','2023-06-07 00:18:56',5),(936316939322654840,1109861649910874274,235148962103951360,'Warn','suck me','2023-06-07 00:21:13',8),(936316939322654840,1109861649910874274,1109861649910874274,'Warn','dumb kid','2023-06-07 00:19:14',6),(936316939322654840,1109861649910874274,1109861649910874274,'Warn','sup lol','2023-06-07 00:19:51',7),(936316939322654840,1109861649910874274,1109861649910874274,'Warn','suck me','2023-06-07 00:21:17',9),(936316939322654840,1111760388674048121,109390881685032960,'Ban',NULL,'2023-06-07 01:15:15',19),(936316939322654840,1111760388674048121,122901490439290881,'Ban',NULL,'2023-06-07 01:14:24',12),(936316939322654840,1111760388674048121,130882548237598721,'Ban',NULL,'2023-06-07 01:14:24',14),(936316939322654840,1111760388674048121,244938419925549057,'Ban',NULL,'2023-06-07 01:15:16',31),(936316939322654840,1111760388674048121,292425305409454082,'Ban',NULL,'2023-06-07 01:15:15',25),(936316939322654840,1111760388674048121,352190010998390796,'Ban',NULL,'2023-06-07 01:15:15',22),(936316939322654840,1111760388674048121,383162108759506944,'Ban',NULL,'2023-06-07 01:14:24',17),(936316939322654840,1111760388674048121,386192601268748289,'Ban',NULL,'2023-06-07 01:15:15',30),(936316939322654840,1111760388674048121,411916947773587456,'Ban',NULL,'2023-06-07 01:15:15',23),(936316939322654840,1111760388674048121,470368849158602762,'Ban',NULL,'2023-06-07 01:15:15',23),(936316939322654840,1111760388674048121,484623554768273408,'Ban',NULL,'2023-06-07 01:14:24',16),(936316939322654840,1111760388674048121,490308138256433152,'Ban',NULL,'2023-06-07 01:15:15',25),(936316939322654840,1111760388674048121,500658624109084682,'Ban',NULL,'2023-06-07 01:15:15',24),(936316939322654840,1111760388674048121,574412707642605603,'Ban',NULL,'2023-06-07 01:14:24',13),(936316939322654840,1111760388674048121,605366607690334213,'Ban',NULL,'2023-06-07 01:15:15',20),(936316939322654840,1111760388674048121,633006895233237012,'Ban',NULL,'2023-06-07 01:14:24',15),(936316939322654840,1111760388674048121,651246668959842346,'Ban',NULL,'2023-06-07 01:15:15',28),(936316939322654840,1111760388674048121,713784919054090292,'Ban','Vile Moderation [kuromi#1337]: hi','2023-06-06 11:10:36',1),(936316939322654840,1111760388674048121,713784919054090292,'Ban','Vile Moderation [kuromi#1337]: hi','2023-06-06 11:10:57',2),(936316939322654840,1111760388674048121,713784919054090292,'Ban','Vile Moderation [kuromi#1337]: hi','2023-06-06 11:11:24',3),(936316939322654840,1111760388674048121,736461634234744834,'Ban',NULL,'2023-06-07 01:15:16',33),(936316939322654840,1111760388674048121,748384138725163019,'Ban',NULL,'2023-06-07 01:15:15',28),(936316939322654840,1111760388674048121,757322852994121888,'Ban',NULL,'2023-06-07 01:14:24',13),(936316939322654840,1111760388674048121,776128410547126322,'Ban',NULL,'2023-06-07 01:15:15',22),(936316939322654840,1111760388674048121,782789412123312138,'Ban',NULL,'2023-06-07 01:15:15',22),(936316939322654840,1111760388674048121,923180835195219991,'Ban',NULL,'2023-06-07 01:15:15',26),(936316939322654840,1111760388674048121,932378206537916466,'Ban',NULL,'2023-06-07 01:14:24',16),(936316939322654840,1111760388674048121,959307889598681108,'Ban',NULL,'2023-06-07 01:15:15',19),(936316939322654840,1111760388674048121,971004855265153024,'Ban',NULL,'2023-06-07 01:15:15',20),(936316939322654840,1111760388674048121,971032543006715934,'Ban',NULL,'2023-06-07 01:15:15',21),(936316939322654840,1111760388674048121,971047782657978458,'Ban',NULL,'2023-06-07 01:15:15',25),(936316939322654840,1111760388674048121,971387132662939688,'Ban',NULL,'2023-06-07 01:15:15',21),(936316939322654840,1111760388674048121,984917403391643768,'Ban',NULL,'2023-06-07 01:15:15',27),(936316939322654840,1111760388674048121,984917808536223804,'Ban',NULL,'2023-06-07 01:15:15',22),(936316939322654840,1111760388674048121,985279842981404703,'Ban',NULL,'2023-06-07 01:15:15',25),(936316939322654840,1111760388674048121,985279921049960498,'Ban',NULL,'2023-06-07 01:15:15',19),(936316939322654840,1111760388674048121,995047130584584293,'Ban',NULL,'2023-06-07 01:15:15',26),(936316939322654840,1111760388674048121,1002294763241885847,'Ban',NULL,'2023-06-07 01:11:08',10),(936316939322654840,1111760388674048121,1004836998151950358,'Ban',NULL,'2023-06-07 01:15:15',29),(936316939322654840,1111760388674048121,1015277730918572042,'Ban',NULL,'2023-06-07 01:14:24',11),(936316939322654840,1111760388674048121,1082429362420326421,'Ban',NULL,'2023-06-07 01:15:16',32),(936316939322654840,1111760388674048121,1092305777038995507,'Ban',NULL,'2023-06-07 01:14:24',18),(936316939322654840,1111760388674048121,1111798598821224448,'Ban',NULL,'2023-06-07 01:14:24',16),(936316939322654840,1111760388674048121,1113480426330279996,'Ban',NULL,'2023-06-07 01:15:15',28),(1031650118375571537,1002261905613799527,179746206119886848,'Kick','kick: used by kuromi#1337','2023-06-07 00:54:05',4),(1031650118375571537,1002261905613799527,939617412746215464,'Kick','\"impersonating ass hoe\" - kick: used by kuromi#1337','2023-06-07 00:54:38',5),(1031650118375571537,1109861649910874274,1048293454909800502,'Warn','test','2023-06-07 00:52:50',2),(1031650118375571537,1111760388674048121,973853046910115860,'Kick','Vile Moderation [kuromi#1337]: test','2023-06-07 00:50:40',1),(1031650118375571537,1111760388674048121,1048293454909800502,'Kick','Vile Moderation [kuromi#1337]: No reason provided','2023-06-07 00:52:56',3),(1053462941996953650,1002294763241885847,1094317549224738987,'Ban','No Reason Provided | cop#0666','2023-06-06 22:00:53',1);
/*!40000 ALTER TABLE `moderation_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `muted_user`
--

DROP TABLE IF EXISTS `muted_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `muted_user` (
  `guild_id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `channel_id` bigint(20) DEFAULT NULL,
  `unmute_on` datetime DEFAULT NULL,
  PRIMARY KEY (`guild_id`,`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `muted_user`
--

LOCK TABLES `muted_user` WRITE;
/*!40000 ALTER TABLE `muted_user` DISABLE KEYS */;
/*!40000 ALTER TABLE `muted_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `name_history`
--

DROP TABLE IF EXISTS `name_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `name_history` (
  `user_id` bigint(20) NOT NULL,
  `name` varchar(256) NOT NULL,
  `updated_on` datetime NOT NULL,
  PRIMARY KEY (`user_id`,`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `name_history`
--

LOCK TABLES `name_history` WRITE;
/*!40000 ALTER TABLE `name_history` DISABLE KEYS */;
INSERT INTO `name_history` VALUES (109390881685032960,'gAAAAABkf-bC2mhrvRZqN5YgHv-kJil3nfAl_H4MDta4twwTU80FOqdWOXnfPfJvDtvJ56JxVliaHngUp3t3pqDFkPKFWXi8pg==','2023-06-07 02:09:06'),(109390881685032960,'gAAAAABkf9EVr3XMX-vT6S_72n8kkEXy7IWMvRVJ4KfBckAN0kMIWRwHPaO2LQkW94RX1nibAw1Ufha9COZINe7i2zY0bt5hkw==','2023-06-07 00:36:37'),(109390881685032960,'gAAAAABkf_n5OS8koLP33SWTqzFG100gqAbrNGYiWYuqGUnE6tXYiQ8fxH-mL2Wsru0A6uaoeD2lst6hqzzIpFArFUUcqlHdCA==','2023-06-07 03:31:05'),(109390881685032960,'gAAAAABkgANefPhhohz_KxZtBcrcPn-f4NEI0OXhvN4blhxfFkxryQmbUiP0NsH7wzVYaOR19qUP3euPIUWem78UDECDr-jaYw==','2023-06-07 04:11:10'),(109390881685032960,'gAAAAABkgBMEJ-cVhSmKsFcJR57Oe36S06zE4fbLWRPhPZ76WKElcvKhKFiaRKrYRDGxmzFF4dXK0PORSIamlDZ0tIb21X17YQ==','2023-06-07 05:17:56'),(109390881685032960,'gAAAAABkgCQvefa5Q9j8eN0fqty4H7gDAyp-52A4ks2QeW8t711osLWjwMSx2113oYCyz6wBH03SzBl4Wiawu9SqF8mPExnURA==','2023-06-07 06:31:11'),(246779465412247553,'gAAAAABkgMoSg_qrdtNGhk2GHY5PhOBA3aQigOKbqZ5gAwsxfzlHMI_yB3QFmR89Y_1QLAjuVR6UuL8-FMxkyAizGOgVlvmFag==','2023-06-07 18:18:58'),(246779465412247553,'gAAAAABkgMXzmFdsJKTz_EWu0fnCEpln2ppsY2rt4vlYmXlSfP4v0O8f7hed2r-NA3XQf_eh3mzBdDAiZtkL4QtpWuoNll04FA==','2023-06-07 18:01:23'),(246779465412247553,'gAAAAABkgNIyqVTmeqdpWSiRoyl9ptY0wUnK8N12OH53WZMppUFkgZHU5Yg7QWra_LZzmeEi5g_SjOxniDA4W-ZPgLIn-inKXA==','2023-06-07 18:53:38'),(637346086641729537,'gAAAAABkf44KohTiHDLiw_OmbPsyq7W-y9kymZym5ssqFo6llbQ4rkdD4ITqjMUPvY-WS7ORUXMCKwlhNaiop2SZrHZfNUnWrw==','2023-06-06 19:50:34'),(637346086641729537,'gAAAAABkgOQIa1X3nQgudsPK-qhRK6_YvHzYP8szP0NsDryrsFAhM0POM_qyM63_8RcHty4uKL2WdWw1aDHgjqXatuBBasFX5Q==','2023-06-07 20:09:44'),(930614009596612688,'gAAAAABkgCDUO4wvahqIyXhy2XKUpqasqUFeMezq18im8yiTipODFbg_puJmq7tTZ9CvY5E28oFzoT4YggUxrmDXQXzcO0e8wg==','2023-06-07 06:16:52'),(948432268911865916,'gAAAAABkgKR7CQUro0BtlZyQwRdY2LhyM3tcC9i3lYkSJWw6fKhr227BpxwROV-A-bTc_Cov33M5ymUs4iIBzEI3htUS82rhKA==','2023-06-07 15:38:35'),(1062641483125100607,'gAAAAABkf_1xh4_-wPDJW5a8pCYw4uMpzJLeWSfibxSAm1DatlzAYObn7XABqYX5lQxmCOKyRX-X793VwBnGFw66A-rAyndbOg==','2023-06-07 03:45:53'),(1111760388674048121,'gAAAAABkfrYpOXH2cAEjEUc31P2Yv4X3-cn6ueX_0B4Eql1sJcdsR8id29eqZrIy1fyXpErIP8UyAwTq9IEUJxhZUD0CrC2OeA==','2023-06-06 04:29:29'),(1113480426330279996,'gAAAAABkgEaEQRhjSkC9d6Hsgh75bdsWeTlTPxNJJRzXFoBYQDsHtepBFStGjW53sLQG86zsHXU5z68oiMy_DYLUBnzzYuX56GD-Qzk_bDXgrvi55nUlBGY=','2023-06-07 08:57:40');
/*!40000 ALTER TABLE `name_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notification`
--

DROP TABLE IF EXISTS `notification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `notification` (
  `guild_id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `keyword` varchar(32) NOT NULL,
  PRIMARY KEY (`guild_id`,`user_id`,`keyword`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notification`
--

LOCK TABLES `notification` WRITE;
/*!40000 ALTER TABLE `notification` DISABLE KEYS */;
/*!40000 ALTER TABLE `notification` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pagination`
--

DROP TABLE IF EXISTS `pagination`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pagination` (
  `guild_id` bigint(20) DEFAULT NULL,
  `channel_id` bigint(20) DEFAULT NULL,
  `message_id` bigint(20) DEFAULT NULL,
  `current_page` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pagination`
--

LOCK TABLES `pagination` WRITE;
/*!40000 ALTER TABLE `pagination` DISABLE KEYS */;
INSERT INTO `pagination` VALUES (936316939322654840,1060970721280524318,1116039942695550986,2),(936316939322654840,1060970721280524318,1116039942695550986,2),(936316939322654840,1060970721280524318,1116072979986645123,1),(936316939322654840,1060970721280524318,1116072979986645123,1),(936316939322654840,1060970721280524318,1116072979986645123,1);
/*!40000 ALTER TABLE `pagination` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pagination_pages`
--

DROP TABLE IF EXISTS `pagination_pages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pagination_pages` (
  `guild_id` bigint(20) DEFAULT NULL,
  `channel_id` bigint(20) DEFAULT NULL,
  `message_id` bigint(20) DEFAULT NULL,
  `page` varchar(1024) DEFAULT NULL,
  `page_number` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pagination_pages`
--

LOCK TABLES `pagination_pages` WRITE;
/*!40000 ALTER TABLE `pagination_pages` DISABLE KEYS */;
INSERT INTO `pagination_pages` VALUES (936316939322654840,1060970721280524318,1116039942695550986,'{content: sup}',1),(936316939322654840,1060970721280524318,1116039942695550986,'{content: lol}',2),(936316939322654840,1060970721280524318,1116072979986645123,'{content: sup - page {page.current}/{page.total}}',1),(936316939322654840,1060970721280524318,1116072979986645123,'{content: get a life - page {page.current}/{page.total}}',2),(936316939322654840,1060970721280524318,1116072979986645123,'{content: ur a loser - page {page.current}/{page.total}}',3);
/*!40000 ALTER TABLE `pagination_pages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pin_archive`
--

DROP TABLE IF EXISTS `pin_archive`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pin_archive` (
  `guild_id` bigint(20) NOT NULL,
  `channel_id` bigint(20) DEFAULT NULL,
  `is_enabled` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`guild_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pin_archive`
--

LOCK TABLES `pin_archive` WRITE;
/*!40000 ALTER TABLE `pin_archive` DISABLE KEYS */;
/*!40000 ALTER TABLE `pin_archive` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reminder`
--

DROP TABLE IF EXISTS `reminder`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `reminder` (
  `guild_id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `created_on` datetime DEFAULT NULL,
  `reminder_date` datetime DEFAULT NULL,
  `content` varchar(255) NOT NULL,
  `original_message_url` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`guild_id`,`user_id`,`content`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reminder`
--

LOCK TABLES `reminder` WRITE;
/*!40000 ALTER TABLE `reminder` DISABLE KEYS */;
/*!40000 ALTER TABLE `reminder` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `starboard_blacklist`
--

DROP TABLE IF EXISTS `starboard_blacklist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `starboard_blacklist` (
  `guild_id` bigint(20) NOT NULL,
  `channel_id` bigint(20) NOT NULL,
  PRIMARY KEY (`guild_id`,`channel_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `starboard_blacklist`
--

LOCK TABLES `starboard_blacklist` WRITE;
/*!40000 ALTER TABLE `starboard_blacklist` DISABLE KEYS */;
/*!40000 ALTER TABLE `starboard_blacklist` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `starboard_message`
--

DROP TABLE IF EXISTS `starboard_message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `starboard_message` (
  `original_message_id` bigint(20) NOT NULL,
  `starboard_message_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`original_message_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `starboard_message`
--

LOCK TABLES `starboard_message` WRITE;
/*!40000 ALTER TABLE `starboard_message` DISABLE KEYS */;
/*!40000 ALTER TABLE `starboard_message` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `starboard_settings`
--

DROP TABLE IF EXISTS `starboard_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `starboard_settings` (
  `guild_id` bigint(20) NOT NULL,
  `channel_id` bigint(20) DEFAULT NULL,
  `is_enabled` tinyint(1) DEFAULT 1,
  `attachments_allowed` tinyint(1) DEFAULT 1,
  `selfstar_allowed` tinyint(1) DEFAULT 1,
  `show_jumpurl` tinyint(1) DEFAULT 1,
  `embed_color` int(11) DEFAULT 11643608,
  `show_timestamp` tinyint(1) DEFAULT 1,
  `reaction_count` int(11) DEFAULT 3,
  `emoji_name` varchar(64) NOT NULL DEFAULT 'u2b50',
  `emoji_id` bigint(20) DEFAULT NULL,
  `emoji_type` enum('unicode','custom') NOT NULL DEFAULT 'unicode',
  PRIMARY KEY (`guild_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `starboard_settings`
--

LOCK TABLES `starboard_settings` WRITE;
/*!40000 ALTER TABLE `starboard_settings` DISABLE KEYS */;
/*!40000 ALTER TABLE `starboard_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sticky_message`
--

DROP TABLE IF EXISTS `sticky_message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sticky_message` (
  `channel_id` bigint(20) NOT NULL,
  `message_id` bigint(20) NOT NULL,
  PRIMARY KEY (`channel_id`,`message_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sticky_message`
--

LOCK TABLES `sticky_message` WRITE;
/*!40000 ALTER TABLE `sticky_message` DISABLE KEYS */;
/*!40000 ALTER TABLE `sticky_message` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sticky_message_settings`
--

DROP TABLE IF EXISTS `sticky_message_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sticky_message_settings` (
  `guild_id` bigint(20) NOT NULL,
  `channel_id` bigint(20) DEFAULT NULL,
  `is_enabled` tinyint(1) DEFAULT 1,
  `message` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`guild_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sticky_message_settings`
--

LOCK TABLES `sticky_message_settings` WRITE;
/*!40000 ALTER TABLE `sticky_message_settings` DISABLE KEYS */;
/*!40000 ALTER TABLE `sticky_message_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `temporary_bans`
--

DROP TABLE IF EXISTS `temporary_bans`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `temporary_bans` (
  `guild_id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `unban_on` datetime DEFAULT NULL,
  PRIMARY KEY (`guild_id`,`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `temporary_bans`
--

LOCK TABLES `temporary_bans` WRITE;
/*!40000 ALTER TABLE `temporary_bans` DISABLE KEYS */;
/*!40000 ALTER TABLE `temporary_bans` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `unboost_settings`
--

DROP TABLE IF EXISTS `unboost_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `unboost_settings` (
  `guild_id` bigint(20) NOT NULL,
  `channel_id` bigint(20) DEFAULT NULL,
  `is_enabled` tinyint(1) DEFAULT 1,
  `message` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`guild_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `unboost_settings`
--

LOCK TABLES `unboost_settings` WRITE;
/*!40000 ALTER TABLE `unboost_settings` DISABLE KEYS */;
/*!40000 ALTER TABLE `unboost_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_settings`
--

DROP TABLE IF EXISTS `user_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_settings` (
  `user_id` bigint(20) NOT NULL,
  `lastfm_username` varchar(15) DEFAULT NULL,
  `sunsign` varchar(32) DEFAULT NULL,
  `location_string` varchar(128) DEFAULT NULL,
  `timezone` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_settings`
--

LOCK TABLES `user_settings` WRITE;
/*!40000 ALTER TABLE `user_settings` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `webhook_messages`
--

DROP TABLE IF EXISTS `webhook_messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `webhook_messages` (
  `identifier` varchar(32) DEFAULT NULL,
  `webhook_url` tinytext DEFAULT NULL,
  `message_id` bigint(20) NOT NULL,
  PRIMARY KEY (`message_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `webhook_messages`
--

LOCK TABLES `webhook_messages` WRITE;
/*!40000 ALTER TABLE `webhook_messages` DISABLE KEYS */;
INSERT INTO `webhook_messages` VALUES ('30850618c46bfe30','https://discord.com/api/webhooks/1108606988373471333/FZin7QWUyHE4WwBNQvbJdTpBeJoEq6lgvsbcO8N06i7BynzcnCDVTzxUdjQkkOJ3D9lu',1108698106012373112),('30850618c46bfe30','https://discord.com/api/webhooks/1108606988373471333/FZin7QWUyHE4WwBNQvbJdTpBeJoEq6lgvsbcO8N06i7BynzcnCDVTzxUdjQkkOJ3D9lu',1108698126186983455),('30850618c46bfe30','https://discord.com/api/webhooks/1108606988373471333/FZin7QWUyHE4WwBNQvbJdTpBeJoEq6lgvsbcO8N06i7BynzcnCDVTzxUdjQkkOJ3D9lu',1108698142410539068),('30850618c46bfe30','https://discord.com/api/webhooks/1108606988373471333/FZin7QWUyHE4WwBNQvbJdTpBeJoEq6lgvsbcO8N06i7BynzcnCDVTzxUdjQkkOJ3D9lu',1108698207636176896),('30850618c46bfe30','https://discord.com/api/webhooks/1108606988373471333/FZin7QWUyHE4WwBNQvbJdTpBeJoEq6lgvsbcO8N06i7BynzcnCDVTzxUdjQkkOJ3D9lu',1108698227261329438);
/*!40000 ALTER TABLE `webhook_messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `webhooks`
--

DROP TABLE IF EXISTS `webhooks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `webhooks` (
  `guild_id` bigint(20) NOT NULL,
  `identifier` varchar(32) NOT NULL,
  `webhook_url` tinytext DEFAULT NULL,
  `channel_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`guild_id`,`identifier`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `webhooks`
--

LOCK TABLES `webhooks` WRITE;
/*!40000 ALTER TABLE `webhooks` DISABLE KEYS */;
INSERT INTO `webhooks` VALUES (936316939322654840,'30850618c46bfe30','https://discord.com/api/webhooks/1108606988373471333/FZin7QWUyHE4WwBNQvbJdTpBeJoEq6lgvsbcO8N06i7BynzcnCDVTzxUdjQkkOJ3D9lu',1060970721280524318),(936316939322654840,'c9cc69089ef9d463','https://discord.com/api/webhooks/1111024134265245809/oii6kj6G4-_OuYMkJHkE-nxjL1y80fJy3rdysO1QgtgGNSYdbatQVwdxXfCTnuxaFVwb',1060970721280524318);
/*!40000 ALTER TABLE `webhooks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `welcome_settings`
--

DROP TABLE IF EXISTS `welcome_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `welcome_settings` (
  `guild_id` bigint(20) NOT NULL,
  `channel_id` bigint(20) DEFAULT NULL,
  `is_enabled` tinyint(1) DEFAULT 1,
  `message` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`guild_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `welcome_settings`
--

LOCK TABLES `welcome_settings` WRITE;
/*!40000 ALTER TABLE `welcome_settings` DISABLE KEYS */;
INSERT INTO `welcome_settings` VALUES (936316939322654840,1060970721280524318,1,'{embed}{author: Frequently Asked Questions}$v{description: idk}$v{field: yes && value: okay dude}'),(1053462941996953650,1096134879894306946,1,'{content: did');
/*!40000 ALTER TABLE `welcome_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `your_table_name`
--

DROP TABLE IF EXISTS `your_table_name`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `your_table_name` (
  `case_id` int(11) NOT NULL AUTO_INCREMENT,
  `customer` varchar(255) NOT NULL,
  `member` varchar(255) NOT NULL,
  PRIMARY KEY (`customer`,`member`),
  UNIQUE KEY `case_id` (`case_id`,`customer`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `your_table_name`
--

LOCK TABLES `your_table_name` WRITE;
/*!40000 ALTER TABLE `your_table_name` DISABLE KEYS */;
/*!40000 ALTER TABLE `your_table_name` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-06-07 20:56:48
