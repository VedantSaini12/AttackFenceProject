-- MySQL dump 10.13  Distrib 8.0.36, for Win64 (x86_64)
--
-- Host: localhost    Database: newset
-- ------------------------------------------------------
-- Server version	8.0.37

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
-- Table structure for table `blocked_users`
--

DROP TABLE IF EXISTS `blocked_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `blocked_users` (
  `email` varchar(255) NOT NULL,
  `blocked_at` datetime NOT NULL,
  PRIMARY KEY (`email`),
  CONSTRAINT `blocked_users_ibfk_1` FOREIGN KEY (`email`) REFERENCES `users` (`email`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `blocked_users`
--

LOCK TABLES `blocked_users` WRITE;
/*!40000 ALTER TABLE `blocked_users` DISABLE KEYS */;
/*!40000 ALTER TABLE `blocked_users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `evaluation_comments`
--

DROP TABLE IF EXISTS `evaluation_comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `evaluation_comments` (
  `comment_id` int NOT NULL AUTO_INCREMENT,
  `rating_id` int NOT NULL,
  `commenter_email` varchar(255) NOT NULL,
  `comment_text` text NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`comment_id`),
  KEY `rating_id` (`rating_id`),
  KEY `commenter_email` (`commenter_email`),
  CONSTRAINT `evaluation_comments_ibfk_1` FOREIGN KEY (`rating_id`) REFERENCES `user_ratings` (`id`) ON DELETE CASCADE,
  CONSTRAINT `evaluation_comments_ibfk_2` FOREIGN KEY (`commenter_email`) REFERENCES `users` (`email`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `evaluation_comments`
--

LOCK TABLES `evaluation_comments` WRITE;
/*!40000 ALTER TABLE `evaluation_comments` DISABLE KEYS */;
INSERT INTO `evaluation_comments` VALUES (1,286,'lazross@evaluationportal.in','blah blah','2025-07-29 07:34:58'),(2,305,'lazross@evaluationportal.in','oiannkn','2025-07-29 07:34:58'),(3,287,'lazross@evaluationportal.in','jdncjd','2025-07-29 07:34:58'),(4,306,'lazross@evaluationportal.in','kllknl','2025-07-29 07:34:58'),(5,288,'lazross@evaluationportal.in','dinvidnvn','2025-07-29 07:34:58'),(6,307,'lazross@evaluationportal.in','inodvnkn','2025-07-29 07:34:58'),(7,289,'lazross@evaluationportal.in','divmspdmpsd','2025-07-29 07:34:58'),(8,316,'lazross@evaluationportal.in','pmdvpom','2025-07-29 07:34:58'),(9,290,'lazross@evaluationportal.in','fpokomod','2025-07-29 07:34:58'),(10,317,'lazross@evaluationportal.in','pfvomofvm','2025-07-29 07:34:58'),(11,291,'lazross@evaluationportal.in','okofvkovm','2025-07-29 07:34:58'),(12,318,'lazross@evaluationportal.in','odmvomovm','2025-07-29 07:34:58'),(13,292,'lazross@evaluationportal.in','dovmodvmo','2025-07-29 07:34:58'),(14,308,'lazross@evaluationportal.in','omdvomvomv','2025-07-29 07:34:58'),(15,293,'lazross@evaluationportal.in','qeomeo','2025-07-29 07:34:58'),(16,309,'lazross@evaluationportal.in','oemoememv','2025-07-29 07:34:58'),(17,294,'lazross@evaluationportal.in','kfffjf','2025-07-29 07:34:58'),(18,310,'lazross@evaluationportal.in','djbvjnvj','2025-07-29 07:34:58'),(19,295,'lazross@evaluationportal.in','divnivnivn','2025-07-29 07:34:58'),(20,311,'lazross@evaluationportal.in','idvmivivnin','2025-07-29 07:34:58'),(21,296,'lazross@evaluationportal.in','divnidvnivn','2025-07-29 07:34:58'),(22,312,'lazross@evaluationportal.in','dvj djvkvm','2025-07-29 07:34:58'),(23,297,'lazross@evaluationportal.in','djvnvmvm','2025-07-29 07:34:58'),(24,313,'lazross@evaluationportal.in','ikmdvomvomvmo','2025-07-29 07:34:58'),(25,298,'lazross@evaluationportal.in','dj vnvim','2025-07-29 07:34:58'),(26,314,'lazross@evaluationportal.in','omvovom eomoevm','2025-07-29 07:34:58'),(27,299,'lazross@evaluationportal.in','dodvmovmo domovm','2025-07-29 07:34:58'),(28,315,'lazross@evaluationportal.in',' omvmovmovm','2025-07-29 07:34:58'),(29,300,'lazross@evaluationportal.in','imvimv','2025-07-29 07:34:58'),(30,319,'lazross@evaluationportal.in','midmvimvim','2025-07-29 07:34:58'),(31,301,'lazross@evaluationportal.in','midvmvmo','2025-07-29 07:34:58'),(32,320,'lazross@evaluationportal.in','jfvnjvnjvnnv','2025-07-29 07:34:58'),(33,302,'lazross@evaluationportal.in','dvnjvnvnviun','2025-07-29 07:34:58'),(34,321,'lazross@evaluationportal.in','jenvineineine','2025-07-29 07:34:58'),(35,303,'lazross@evaluationportal.in','idnibnivniovm','2025-07-29 07:34:58'),(36,322,'lazross@evaluationportal.in','ieenvvnievn','2025-07-29 07:34:58'),(37,304,'lazross@evaluationportal.in','dinvinvivn','2025-07-29 07:34:58'),(38,323,'lazross@evaluationportal.in','invinivnv','2025-07-29 07:34:58');
/*!40000 ALTER TABLE `evaluation_comments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `login_attempts`
--

DROP TABLE IF EXISTS `login_attempts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `login_attempts` (
  `email` varchar(255) DEFAULT NULL,
  `attempt_time` datetime DEFAULT NULL,
  KEY `email` (`email`),
  CONSTRAINT `login_attempts_ibfk_1` FOREIGN KEY (`email`) REFERENCES `users` (`email`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `login_attempts`
--

LOCK TABLES `login_attempts` WRITE;
/*!40000 ALTER TABLE `login_attempts` DISABLE KEYS */;
INSERT INTO `login_attempts` VALUES ('claire@example.com','2025-07-07 18:00:24'),('silverhand@example.com','2025-07-23 18:41:21'),('silverhand@example.com','2025-07-23 18:41:29'),('domino@example.com','2025-07-24 11:54:57'),('sarthak12@example.com','2025-07-24 11:55:11'),('sarthak12@example.com','2025-07-24 11:55:28'),('claire@example.com','2025-07-25 20:54:11');
/*!40000 ALTER TABLE `login_attempts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notifications` (
  `id` int NOT NULL AUTO_INCREMENT,
  `recipient` varchar(255) NOT NULL,
  `sender` varchar(255) DEFAULT NULL,
  `message` text NOT NULL,
  `notification_type` varchar(50) NOT NULL,
  `is_read` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `related_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_recipient` (`recipient`),
  KEY `idx_is_read` (`is_read`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications`
--

LOCK TABLES `notifications` WRITE;
/*!40000 ALTER TABLE `notifications` DISABLE KEYS */;
INSERT INTO `notifications` VALUES (2,'vedant@example.com','one@example.com','One has completed their self-evaluation. Please complete your review.','self_evaluation_completed',1,'2025-06-30 07:50:33',NULL),(3,'one@example.com','vedant@example.com','Your manager, Vedant, has completed your evaluation.','evaluation_completed',1,'2025-06-30 07:56:57',NULL),(8,'vedant@example.com','adam@exampke.com','Adam has completed their self-evaluation. Please complete your review.','self_evaluation_completed',1,'2025-07-07 12:07:07',NULL),(9,'vedant@example.com','five@example.com','Five has completed their self-evaluation. Please complete your review.','self_evaluation_completed',1,'2025-07-07 12:21:50',NULL),(10,'vedant@example.com','silverhand@example.com','Silverhand has completed their self-evaluation. Please complete your review.','self_evaluation_completed',1,'2025-07-07 12:33:03',NULL),(11,'silverhand@example.com','vedant@example.com','Your manager, Vedant, has completed your evaluation.','evaluation_completed',0,'2025-07-07 12:34:06',NULL),(12,'silverhand@example.com','vedant@example.com','Your manager, Vedant, has completed your evaluation.','evaluation_completed',0,'2025-07-07 12:34:37',NULL),(13,'vedant@example.com','bob@example.com','Bob has completed their self-evaluation. Please complete your review.','self_evaluation_completed',1,'2025-07-09 11:42:00',NULL),(14,'bob@example.com','vedant@example.com','Your manager, Vedant, has completed your evaluation for Quarter 3.','evaluation_completed',0,'2025-07-09 11:44:23',NULL),(15,'john@example.com','sarthak12@example.com','Sarthak has completed their self-evaluation. Please complete your review.','self_evaluation_completed',1,'2025-07-11 07:52:49',NULL),(16,'sarthak12@example.com','john@example.com','Your manager, Jack, has completed your evaluation for Quarter 3.','evaluation_completed',1,'2025-07-11 07:54:30',NULL),(17,'john@example.com','clarkkent@example.com','Clark Kent has completed their self-evaluation. Please complete your review.','self_evaluation_completed',0,'2025-07-15 10:23:19',NULL),(18,'clarkkent@example.com','john@example.com','Your manager, Jack, has completed your evaluation for Quarter 3.','evaluation_completed',1,'2025-07-15 10:24:38',NULL),(19,'vedant@example.com','test123@example.com','Test123 has completed their self-evaluation. Please complete your review.','self_evaluation_completed',1,'2025-07-18 09:44:29',NULL),(20,'test123@example.com','vedant@example.com','Your manager, Vedant, has completed your evaluation for Quarter 3.','evaluation_completed',1,'2025-07-18 09:59:11',NULL),(21,'vedant@example.com','test123@example.com','Test123 has completed their self-evaluation. Please complete your review.','self_evaluation_completed',1,'2025-07-23 09:47:15',NULL),(22,'vedant@example.com','test123@example.com','Test123 has completed their self-evaluation. Please complete your review.','self_evaluation_completed',1,'2025-07-23 09:49:56',NULL),(23,'john@example.com','clarkkent@example.com','Clark Kent has completed their self-evaluation. Please complete your review.','self_evaluation_completed',0,'2025-07-23 13:13:08',NULL),(24,'vedant@example.com','five@example.com','Five has completed their self-evaluation for Q3 2025.','self_evaluation_completed',1,'2025-07-24 06:36:22',NULL),(25,'vedant@example.com','Mark','Mark has completed their self-evaluation for Q3 2025.','self_evaluation_completed',1,'2025-07-24 07:28:12',NULL),(26,'vedant@example.com','harry@example.com','Harry Bron has completed their self-evaluation for Q3 2025.','self_evaluation_completed',1,'2025-07-27 09:45:59',NULL);
/*!40000 ALTER TABLE `notifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `remarks`
--

DROP TABLE IF EXISTS `remarks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `remarks` (
  `id` int NOT NULL AUTO_INCREMENT,
  `rater` varchar(255) NOT NULL,
  `ratee` varchar(255) NOT NULL,
  `rating_type` varchar(50) NOT NULL,
  `remark` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `quarter` int NOT NULL DEFAULT '3',
  `year` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `remarks`
--

LOCK TABLES `remarks` WRITE;
/*!40000 ALTER TABLE `remarks` DISABLE KEYS */;
INSERT INTO `remarks` VALUES (1,'vedant@example.com','test123@example.com','manager','Abcdefghijklmnopqrstuvwxyz','2025-07-23 10:31:47',3,2025),(2,'vedant@example.com','five@example.com','manager','work on collaboration.','2025-07-24 07:24:21',3,2025),(6,'vedant@example.com','harry@example.com','manager','Eight in all!\n8!','2025-07-27 09:47:58',3,2025),(7,'vedant@example.com','test123@example.com','manager','Above Medium!! have fun','2025-07-29 07:15:03',2,2025);
/*!40000 ALTER TABLE `remarks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_ratings`
--

DROP TABLE IF EXISTS `user_ratings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_ratings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `rater` varchar(255) NOT NULL,
  `ratee` varchar(255) NOT NULL,
  `role` varchar(50) NOT NULL,
  `criteria` varchar(100) NOT NULL,
  `score` int DEFAULT '0',
  `rating_type` varchar(50) NOT NULL,
  `timestamp` datetime DEFAULT CURRENT_TIMESTAMP,
  `quarter` int NOT NULL DEFAULT '3',
  `year` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=381 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_ratings`
--

LOCK TABLES `user_ratings` WRITE;
/*!40000 ALTER TABLE `user_ratings` DISABLE KEYS */;
INSERT INTO `user_ratings` VALUES (1,'test123@example.com','test123@example.com','employee','Quality of Work',7,'self','2025-07-23 15:19:56',3,2025),(2,'test123@example.com','test123@example.com','employee','Task Completion',9,'self','2025-07-23 15:19:56',3,2025),(3,'test123@example.com','test123@example.com','employee','Timeline Adherence',8,'self','2025-07-23 15:19:56',3,2025),(4,'test123@example.com','test123@example.com','employee','Collaboration',8,'self','2025-07-23 15:19:56',3,2025),(5,'test123@example.com','test123@example.com','employee','Innovation',8,'self','2025-07-23 15:19:56',3,2025),(6,'test123@example.com','test123@example.com','employee','Special Situation',8,'self','2025-07-23 15:19:56',3,2025),(7,'test123@example.com','test123@example.com','employee','Humility',7,'self','2025-07-23 15:19:56',3,2025),(8,'test123@example.com','test123@example.com','employee','Integrity',6,'self','2025-07-23 15:19:56',3,2025),(9,'test123@example.com','test123@example.com','employee','Collegiality',8,'self','2025-07-23 15:19:56',3,2025),(10,'test123@example.com','test123@example.com','employee','Attitude',7,'self','2025-07-23 15:19:56',3,2025),(11,'test123@example.com','test123@example.com','employee','Time Management',9,'self','2025-07-23 15:19:56',3,2025),(12,'test123@example.com','test123@example.com','employee','Initiative',6,'self','2025-07-23 15:19:56',3,2025),(13,'test123@example.com','test123@example.com','employee','Communication',9,'self','2025-07-23 15:19:56',3,2025),(14,'test123@example.com','test123@example.com','employee','Compassion',9,'self','2025-07-23 15:19:56',3,2025),(15,'test123@example.com','test123@example.com','employee','Knowledge & Awareness',10,'self','2025-07-23 15:19:56',3,2025),(16,'test123@example.com','test123@example.com','employee','Future readiness',8,'self','2025-07-23 15:19:56',3,2025),(17,'test123@example.com','test123@example.com','employee','Informal leadership',6,'self','2025-07-23 15:19:56',3,2025),(18,'test123@example.com','test123@example.com','employee','Team Development',9,'self','2025-07-23 15:19:56',3,2025),(19,'test123@example.com','test123@example.com','employee','Process adherence',7,'self','2025-07-23 15:19:56',3,2025),(20,'vedant@example.com','test123@example.com','manager','Quality of Work',6,'manager','2025-07-23 16:01:47',3,2025),(21,'vedant@example.com','test123@example.com','manager','Task Completion',7,'manager','2025-07-23 16:01:47',3,2025),(22,'vedant@example.com','test123@example.com','manager','Timeline Adherence',9,'manager','2025-07-23 16:01:47',3,2025),(23,'vedant@example.com','test123@example.com','manager','Humility',4,'manager','2025-07-23 16:01:47',3,2025),(24,'vedant@example.com','test123@example.com','manager','Integrity',7,'manager','2025-07-23 16:01:47',3,2025),(25,'vedant@example.com','test123@example.com','manager','Collegiality',6,'manager','2025-07-23 16:01:47',3,2025),(26,'vedant@example.com','test123@example.com','manager','Attitude',9,'manager','2025-07-23 16:01:47',3,2025),(27,'vedant@example.com','test123@example.com','manager','Time Management',6,'manager','2025-07-23 16:01:47',3,2025),(28,'vedant@example.com','test123@example.com','manager','Initiative',8,'manager','2025-07-23 16:01:47',3,2025),(29,'vedant@example.com','test123@example.com','manager','Communication',6,'manager','2025-07-23 16:01:47',3,2025),(30,'vedant@example.com','test123@example.com','manager','Compassion',9,'manager','2025-07-23 16:01:47',3,2025),(31,'vedant@example.com','test123@example.com','manager','Collaboration',8,'manager','2025-07-23 16:01:47',3,2025),(32,'vedant@example.com','test123@example.com','manager','Innovation',6,'manager','2025-07-23 16:01:47',3,2025),(33,'vedant@example.com','test123@example.com','manager','Special Situation',0,'manager','2025-07-23 16:01:47',3,2025),(34,'vedant@example.com','test123@example.com','manager','Knowledge & Awareness',9,'manager','2025-07-23 16:01:47',3,2025),(35,'vedant@example.com','test123@example.com','manager','Future readiness',7,'manager','2025-07-23 16:01:47',3,2025),(36,'vedant@example.com','test123@example.com','manager','Informal leadership',0,'manager','2025-07-23 16:01:47',3,2025),(37,'vedant@example.com','test123@example.com','manager','Team Development',8,'manager','2025-07-23 16:01:47',3,2025),(38,'vedant@example.com','test123@example.com','manager','Process adherence',0,'manager','2025-07-23 16:01:47',3,2025),(39,'clarkkent@example.com','clarkkent@example.com','employee','Quality of Work',7,'self','2025-07-23 18:43:08',3,2025),(40,'clarkkent@example.com','clarkkent@example.com','employee','Task Completion',4,'self','2025-07-23 18:43:08',3,2025),(41,'clarkkent@example.com','clarkkent@example.com','employee','Timeline Adherence',9,'self','2025-07-23 18:43:08',3,2025),(42,'clarkkent@example.com','clarkkent@example.com','employee','Collaboration',9,'self','2025-07-23 18:43:08',3,2025),(43,'clarkkent@example.com','clarkkent@example.com','employee','Innovation',8,'self','2025-07-23 18:43:08',3,2025),(44,'clarkkent@example.com','clarkkent@example.com','employee','Special Situation',8,'self','2025-07-23 18:43:08',3,2025),(45,'clarkkent@example.com','clarkkent@example.com','employee','Humility',7,'self','2025-07-23 18:43:08',3,2025),(46,'clarkkent@example.com','clarkkent@example.com','employee','Integrity',9,'self','2025-07-23 18:43:08',3,2025),(47,'clarkkent@example.com','clarkkent@example.com','employee','Collegiality',8,'self','2025-07-23 18:43:08',3,2025),(48,'clarkkent@example.com','clarkkent@example.com','employee','Attitude',10,'self','2025-07-23 18:43:08',3,2025),(49,'clarkkent@example.com','clarkkent@example.com','employee','Time Management',9,'self','2025-07-23 18:43:08',3,2025),(50,'clarkkent@example.com','clarkkent@example.com','employee','Initiative',6,'self','2025-07-23 18:43:08',3,2025),(51,'clarkkent@example.com','clarkkent@example.com','employee','Communication',9,'self','2025-07-23 18:43:08',3,2025),(52,'clarkkent@example.com','clarkkent@example.com','employee','Compassion',9,'self','2025-07-23 18:43:08',3,2025),(53,'clarkkent@example.com','clarkkent@example.com','employee','Knowledge & Awareness',10,'self','2025-07-23 18:43:08',3,2025),(54,'clarkkent@example.com','clarkkent@example.com','employee','Future readiness',8,'self','2025-07-23 18:43:08',3,2025),(55,'clarkkent@example.com','clarkkent@example.com','employee','Informal leadership',9,'self','2025-07-23 18:43:08',3,2025),(56,'clarkkent@example.com','clarkkent@example.com','employee','Team Development',10,'self','2025-07-23 18:43:08',3,2025),(57,'clarkkent@example.com','clarkkent@example.com','employee','Process adherence',9,'self','2025-07-23 18:43:08',3,2025),(58,'five@example.com','five@example.com','employee','Quality of Work',10,'self','2025-07-24 12:06:22',3,2025),(59,'five@example.com','five@example.com','employee','Task Completion',5,'self','2025-07-24 12:06:22',3,2025),(60,'five@example.com','five@example.com','employee','Timeline Adherence',6,'self','2025-07-24 12:06:22',3,2025),(61,'five@example.com','five@example.com','employee','Collaboration',4,'self','2025-07-24 12:06:22',3,2025),(62,'five@example.com','five@example.com','employee','Innovation',3,'self','2025-07-24 12:06:22',3,2025),(63,'five@example.com','five@example.com','employee','Special Situation',5,'self','2025-07-24 12:06:22',3,2025),(64,'five@example.com','five@example.com','employee','Humility',10,'self','2025-07-24 12:06:22',3,2025),(65,'five@example.com','five@example.com','employee','Integrity',8,'self','2025-07-24 12:06:22',3,2025),(66,'five@example.com','five@example.com','employee','Collegiality',6,'self','2025-07-24 12:06:22',3,2025),(67,'five@example.com','five@example.com','employee','Attitude',5,'self','2025-07-24 12:06:22',3,2025),(68,'five@example.com','five@example.com','employee','Time Management',3,'self','2025-07-24 12:06:22',3,2025),(69,'five@example.com','five@example.com','employee','Initiative',7,'self','2025-07-24 12:06:22',3,2025),(70,'five@example.com','five@example.com','employee','Communication',5,'self','2025-07-24 12:06:22',3,2025),(71,'five@example.com','five@example.com','employee','Compassion',3,'self','2025-07-24 12:06:22',3,2025),(72,'five@example.com','five@example.com','employee','Knowledge & Awareness',7,'self','2025-07-24 12:06:22',3,2025),(73,'five@example.com','five@example.com','employee','Future readiness',9,'self','2025-07-24 12:06:22',3,2025),(74,'five@example.com','five@example.com','employee','Informal leadership',8,'self','2025-07-24 12:06:22',3,2025),(75,'five@example.com','five@example.com','employee','Team Development',8,'self','2025-07-24 12:06:22',3,2025),(76,'five@example.com','five@example.com','employee','Process adherence',8,'self','2025-07-24 12:06:22',3,2025),(77,'vedant@example.com','five@example.com','manager','Quality of Work',8,'manager','2025-07-24 12:54:21',3,2025),(78,'vedant@example.com','five@example.com','manager','Task Completion',8,'manager','2025-07-24 12:54:21',3,2025),(79,'vedant@example.com','five@example.com','manager','Timeline Adherence',6,'manager','2025-07-24 12:54:21',3,2025),(80,'vedant@example.com','five@example.com','manager','Humility',9,'manager','2025-07-24 12:54:21',3,2025),(81,'vedant@example.com','five@example.com','manager','Integrity',9,'manager','2025-07-24 12:54:21',3,2025),(82,'vedant@example.com','five@example.com','manager','Collegiality',0,'manager','2025-07-24 12:54:21',3,2025),(83,'vedant@example.com','five@example.com','manager','Attitude',0,'manager','2025-07-24 12:54:21',3,2025),(84,'vedant@example.com','five@example.com','manager','Time Management',9,'manager','2025-07-24 12:54:21',3,2025),(85,'vedant@example.com','five@example.com','manager','Initiative',8,'manager','2025-07-24 12:54:21',3,2025),(86,'vedant@example.com','five@example.com','manager','Communication',8,'manager','2025-07-24 12:54:21',3,2025),(87,'vedant@example.com','five@example.com','manager','Compassion',8,'manager','2025-07-24 12:54:21',3,2025),(88,'vedant@example.com','five@example.com','manager','Collaboration',8,'manager','2025-07-24 12:54:21',3,2025),(89,'vedant@example.com','five@example.com','manager','Innovation',7,'manager','2025-07-24 12:54:21',3,2025),(90,'vedant@example.com','five@example.com','manager','Special Situation',7,'manager','2025-07-24 12:54:21',3,2025),(91,'vedant@example.com','five@example.com','manager','Knowledge & Awareness',7,'manager','2025-07-24 12:54:21',3,2025),(92,'vedant@example.com','five@example.com','manager','Future readiness',7,'manager','2025-07-24 12:54:21',3,2025),(93,'vedant@example.com','five@example.com','manager','Informal leadership',8,'manager','2025-07-24 12:54:21',3,2025),(94,'vedant@example.com','five@example.com','manager','Team Development',7,'manager','2025-07-24 12:54:21',3,2025),(95,'vedant@example.com','five@example.com','manager','Process adherence',7,'manager','2025-07-24 12:54:21',3,2025),(248,'harry@example.com','harry@example.com','employee','Quality of Work',5,'self','2025-07-27 15:15:59',3,2025),(249,'harry@example.com','harry@example.com','employee','Task Completion',3,'self','2025-07-27 15:15:59',3,2025),(250,'harry@example.com','harry@example.com','employee','Timeline Adherence',8,'self','2025-07-27 15:15:59',3,2025),(251,'harry@example.com','harry@example.com','employee','Collaboration',8,'self','2025-07-27 15:15:59',3,2025),(252,'harry@example.com','harry@example.com','employee','Innovation',7,'self','2025-07-27 15:15:59',3,2025),(253,'harry@example.com','harry@example.com','employee','Special Situation',7,'self','2025-07-27 15:15:59',3,2025),(254,'harry@example.com','harry@example.com','employee','Humility',7,'self','2025-07-27 15:15:59',3,2025),(255,'harry@example.com','harry@example.com','employee','Integrity',7,'self','2025-07-27 15:15:59',3,2025),(256,'harry@example.com','harry@example.com','employee','Collegiality',7,'self','2025-07-27 15:15:59',3,2025),(257,'harry@example.com','harry@example.com','employee','Attitude',7,'self','2025-07-27 15:15:59',3,2025),(258,'harry@example.com','harry@example.com','employee','Time Management',7,'self','2025-07-27 15:15:59',3,2025),(259,'harry@example.com','harry@example.com','employee','Initiative',7,'self','2025-07-27 15:15:59',3,2025),(260,'harry@example.com','harry@example.com','employee','Communication',7,'self','2025-07-27 15:15:59',3,2025),(261,'harry@example.com','harry@example.com','employee','Compassion',7,'self','2025-07-27 15:15:59',3,2025),(262,'harry@example.com','harry@example.com','employee','Knowledge & Awareness',7,'self','2025-07-27 15:15:59',3,2025),(263,'harry@example.com','harry@example.com','employee','Future readiness',7,'self','2025-07-27 15:15:59',3,2025),(264,'harry@example.com','harry@example.com','employee','Informal leadership',7,'self','2025-07-27 15:15:59',3,2025),(265,'harry@example.com','harry@example.com','employee','Team Development',7,'self','2025-07-27 15:15:59',3,2025),(266,'harry@example.com','harry@example.com','employee','Process adherence',7,'self','2025-07-27 15:15:59',3,2025),(267,'vedant@example.com','harry@example.com','manager','Quality of Work',8,'manager','2025-07-27 15:17:58',3,2025),(268,'vedant@example.com','harry@example.com','manager','Task Completion',8,'manager','2025-07-27 15:17:58',3,2025),(269,'vedant@example.com','harry@example.com','manager','Timeline Adherence',8,'manager','2025-07-27 15:17:58',3,2025),(270,'vedant@example.com','harry@example.com','manager','Humility',8,'manager','2025-07-27 15:17:58',3,2025),(271,'vedant@example.com','harry@example.com','manager','Integrity',8,'manager','2025-07-27 15:17:58',3,2025),(272,'vedant@example.com','harry@example.com','manager','Collegiality',8,'manager','2025-07-27 15:17:58',3,2025),(273,'vedant@example.com','harry@example.com','manager','Attitude',8,'manager','2025-07-27 15:17:58',3,2025),(274,'vedant@example.com','harry@example.com','manager','Time Management',8,'manager','2025-07-27 15:17:58',3,2025),(275,'vedant@example.com','harry@example.com','manager','Initiative',8,'manager','2025-07-27 15:17:58',3,2025),(276,'vedant@example.com','harry@example.com','manager','Communication',8,'manager','2025-07-27 15:17:58',3,2025),(277,'vedant@example.com','harry@example.com','manager','Compassion',8,'manager','2025-07-27 15:17:58',3,2025),(278,'vedant@example.com','harry@example.com','manager','Collaboration',8,'manager','2025-07-27 15:17:58',3,2025),(279,'vedant@example.com','harry@example.com','manager','Innovation',8,'manager','2025-07-27 15:17:58',3,2025),(280,'vedant@example.com','harry@example.com','manager','Special Situation',8,'manager','2025-07-27 15:17:58',3,2025),(281,'vedant@example.com','harry@example.com','manager','Knowledge & Awareness',8,'manager','2025-07-27 15:17:58',3,2025),(282,'vedant@example.com','harry@example.com','manager','Future readiness',8,'manager','2025-07-27 15:17:58',3,2025),(283,'vedant@example.com','harry@example.com','manager','Informal leadership',8,'manager','2025-07-27 15:17:58',3,2025),(284,'vedant@example.com','harry@example.com','manager','Team Development',8,'manager','2025-07-27 15:17:58',3,2025),(285,'vedant@example.com','harry@example.com','manager','Process adherence',8,'manager','2025-07-27 15:17:58',3,2025),(286,'test123@example.com','test123@example.com','employee','Quality of Work',8,'self','2025-07-29 12:41:18',2,2025),(287,'test123@example.com','test123@example.com','employee','Task Completion',9,'self','2025-07-29 12:41:18',2,2025),(288,'test123@example.com','test123@example.com','employee','Timeline Adherence',7,'self','2025-07-29 12:41:18',2,2025),(289,'test123@example.com','test123@example.com','employee','Collaboration',8,'self','2025-07-29 12:41:18',2,2025),(290,'test123@example.com','test123@example.com','employee','Innovation',7,'self','2025-07-29 12:41:18',2,2025),(291,'test123@example.com','test123@example.com','employee','Special Situation',8,'self','2025-07-29 12:41:18',2,2025),(292,'test123@example.com','test123@example.com','employee','Humility',9,'self','2025-07-29 12:41:18',2,2025),(293,'test123@example.com','test123@example.com','employee','Integrity',9,'self','2025-07-29 12:41:18',2,2025),(294,'test123@example.com','test123@example.com','employee','Collegiality',8,'self','2025-07-29 12:41:18',2,2025),(295,'test123@example.com','test123@example.com','employee','Attitude',8,'self','2025-07-29 12:41:18',2,2025),(296,'test123@example.com','test123@example.com','employee','Time Management',7,'self','2025-07-29 12:41:18',2,2025),(297,'test123@example.com','test123@example.com','employee','Initiative',8,'self','2025-07-29 12:41:18',2,2025),(298,'test123@example.com','test123@example.com','employee','Communication',9,'self','2025-07-29 12:41:18',2,2025),(299,'test123@example.com','test123@example.com','employee','Compassion',8,'self','2025-07-29 12:41:18',2,2025),(300,'test123@example.com','test123@example.com','employee','Knowledge & Awareness',8,'self','2025-07-29 12:41:18',2,2025),(301,'test123@example.com','test123@example.com','employee','Future readiness',7,'self','2025-07-29 12:41:18',2,2025),(302,'test123@example.com','test123@example.com','employee','Informal leadership',7,'self','2025-07-29 12:41:18',2,2025),(303,'test123@example.com','test123@example.com','employee','Team Development',8,'self','2025-07-29 12:41:18',2,2025),(304,'test123@example.com','test123@example.com','employee','Process adherence',9,'self','2025-07-29 12:41:18',2,2025),(305,'vedant@example.com','test123@example.com','manager','Quality of Work',6,'manager','2025-07-29 12:45:03',2,2025),(306,'vedant@example.com','test123@example.com','manager','Task Completion',3,'manager','2025-07-29 12:45:03',2,2025),(307,'vedant@example.com','test123@example.com','manager','Timeline Adherence',0,'manager','2025-07-29 12:45:03',2,2025),(308,'vedant@example.com','test123@example.com','manager','Humility',6,'manager','2025-07-29 12:45:03',2,2025),(309,'vedant@example.com','test123@example.com','manager','Integrity',6,'manager','2025-07-29 12:45:03',2,2025),(310,'vedant@example.com','test123@example.com','manager','Collegiality',6,'manager','2025-07-29 12:45:03',2,2025),(311,'vedant@example.com','test123@example.com','manager','Attitude',6,'manager','2025-07-29 12:45:03',2,2025),(312,'vedant@example.com','test123@example.com','manager','Time Management',6,'manager','2025-07-29 12:45:03',2,2025),(313,'vedant@example.com','test123@example.com','manager','Initiative',6,'manager','2025-07-29 12:45:03',2,2025),(314,'vedant@example.com','test123@example.com','manager','Communication',6,'manager','2025-07-29 12:45:03',2,2025),(315,'vedant@example.com','test123@example.com','manager','Compassion',6,'manager','2025-07-29 12:45:03',2,2025),(316,'vedant@example.com','test123@example.com','manager','Collaboration',6,'manager','2025-07-29 12:45:03',2,2025),(317,'vedant@example.com','test123@example.com','manager','Innovation',6,'manager','2025-07-29 12:45:03',2,2025),(318,'vedant@example.com','test123@example.com','manager','Special Situation',6,'manager','2025-07-29 12:45:03',2,2025),(319,'vedant@example.com','test123@example.com','manager','Knowledge & Awareness',6,'manager','2025-07-29 12:45:03',2,2025),(320,'vedant@example.com','test123@example.com','manager','Future readiness',6,'manager','2025-07-29 12:45:03',2,2025),(321,'vedant@example.com','test123@example.com','manager','Informal leadership',6,'manager','2025-07-29 12:45:03',2,2025),(322,'vedant@example.com','test123@example.com','manager','Team Development',6,'manager','2025-07-29 12:45:03',2,2025),(323,'vedant@example.com','test123@example.com','manager','Process adherence',6,'manager','2025-07-29 12:45:03',2,2025),(324,'lazross@evaluationportal.in','test123@example.com','super_manager','Quality of Work',10,'super_manager','2025-07-29 13:04:58',2,2025),(325,'lazross@evaluationportal.in','test123@example.com','super_manager','Task Completion',10,'super_manager','2025-07-29 13:04:58',2,2025),(326,'lazross@evaluationportal.in','test123@example.com','super_manager','Timeline Adherence',10,'super_manager','2025-07-29 13:04:58',2,2025),(327,'lazross@evaluationportal.in','test123@example.com','super_manager','Collaboration',10,'super_manager','2025-07-29 13:04:58',2,2025),(328,'lazross@evaluationportal.in','test123@example.com','super_manager','Innovation',10,'super_manager','2025-07-29 13:04:58',2,2025),(329,'lazross@evaluationportal.in','test123@example.com','super_manager','Special Situation',10,'super_manager','2025-07-29 13:04:58',2,2025),(330,'lazross@evaluationportal.in','test123@example.com','super_manager','Humility',10,'super_manager','2025-07-29 13:04:58',2,2025),(331,'lazross@evaluationportal.in','test123@example.com','super_manager','Integrity',10,'super_manager','2025-07-29 13:04:58',2,2025),(332,'lazross@evaluationportal.in','test123@example.com','super_manager','Collegiality',10,'super_manager','2025-07-29 13:04:58',2,2025),(333,'lazross@evaluationportal.in','test123@example.com','super_manager','Attitude',10,'super_manager','2025-07-29 13:04:58',2,2025),(334,'lazross@evaluationportal.in','test123@example.com','super_manager','Time Management',10,'super_manager','2025-07-29 13:04:58',2,2025),(335,'lazross@evaluationportal.in','test123@example.com','super_manager','Initiative',10,'super_manager','2025-07-29 13:04:58',2,2025),(336,'lazross@evaluationportal.in','test123@example.com','super_manager','Communication',10,'super_manager','2025-07-29 13:04:58',2,2025),(337,'lazross@evaluationportal.in','test123@example.com','super_manager','Compassion',10,'super_manager','2025-07-29 13:04:58',2,2025),(338,'lazross@evaluationportal.in','test123@example.com','super_manager','Knowledge & Awareness',10,'super_manager','2025-07-29 13:04:58',2,2025),(339,'lazross@evaluationportal.in','test123@example.com','super_manager','Future readiness',8,'super_manager','2025-07-29 13:04:58',2,2025),(340,'lazross@evaluationportal.in','test123@example.com','super_manager','Informal leadership',10,'super_manager','2025-07-29 13:04:58',2,2025),(341,'lazross@evaluationportal.in','test123@example.com','super_manager','Team Development',10,'super_manager','2025-07-29 13:04:58',2,2025),(342,'lazross@evaluationportal.in','test123@example.com','super_manager','Process adherence',0,'super_manager','2025-07-29 13:04:58',2,2025),(343,'vedant@example.com','vedant@example.com','manager','Quality of Work',8,'self','2025-07-29 13:42:56',2,2025),(344,'vedant@example.com','vedant@example.com','manager','Task Completion',9,'self','2025-07-29 13:42:56',2,2025),(345,'vedant@example.com','vedant@example.com','manager','Timeline Adherence',8,'self','2025-07-29 13:42:56',2,2025),(346,'vedant@example.com','vedant@example.com','manager','Collaboration',9,'self','2025-07-29 13:42:56',2,2025),(347,'vedant@example.com','vedant@example.com','manager','Innovation',7,'self','2025-07-29 13:42:56',2,2025),(348,'vedant@example.com','vedant@example.com','manager','Special Situation',8,'self','2025-07-29 13:42:56',2,2025),(349,'vedant@example.com','vedant@example.com','manager','Humility',8,'self','2025-07-29 13:42:56',2,2025),(350,'vedant@example.com','vedant@example.com','manager','Integrity',9,'self','2025-07-29 13:42:56',2,2025),(351,'vedant@example.com','vedant@example.com','manager','Collegiality',9,'self','2025-07-29 13:42:56',2,2025),(352,'vedant@example.com','vedant@example.com','manager','Attitude',8,'self','2025-07-29 13:42:56',2,2025),(353,'vedant@example.com','vedant@example.com','manager','Time Management',8,'self','2025-07-29 13:42:56',2,2025),(354,'vedant@example.com','vedant@example.com','manager','Initiative',9,'self','2025-07-29 13:42:56',2,2025),(355,'vedant@example.com','vedant@example.com','manager','Communication',9,'self','2025-07-29 13:42:56',2,2025),(356,'vedant@example.com','vedant@example.com','manager','Compassion',8,'self','2025-07-29 13:42:56',2,2025),(357,'vedant@example.com','vedant@example.com','manager','Knowledge & Awareness',9,'self','2025-07-29 13:42:56',2,2025),(358,'vedant@example.com','vedant@example.com','manager','Future readiness',8,'self','2025-07-29 13:42:56',2,2025),(359,'vedant@example.com','vedant@example.com','manager','Informal leadership',8,'self','2025-07-29 13:42:56',2,2025),(360,'vedant@example.com','vedant@example.com','manager','Team Development',9,'self','2025-07-29 13:42:56',2,2025),(361,'vedant@example.com','vedant@example.com','manager','Process adherence',8,'self','2025-07-29 13:42:56',2,2025),(362,'lazross@evaluationportal.in','vedant@example.com','super_manager','Quality of Work',7,'super_manager','2025-07-29 13:46:16',2,2025),(363,'lazross@evaluationportal.in','vedant@example.com','super_manager','Task Completion',7,'super_manager','2025-07-29 13:46:16',2,2025),(364,'lazross@evaluationportal.in','vedant@example.com','super_manager','Timeline Adherence',7,'super_manager','2025-07-29 13:46:16',2,2025),(365,'lazross@evaluationportal.in','vedant@example.com','super_manager','Collaboration',7,'super_manager','2025-07-29 13:46:16',2,2025),(366,'lazross@evaluationportal.in','vedant@example.com','super_manager','Innovation',7,'super_manager','2025-07-29 13:46:16',2,2025),(367,'lazross@evaluationportal.in','vedant@example.com','super_manager','Special Situation',7,'super_manager','2025-07-29 13:46:16',2,2025),(368,'lazross@evaluationportal.in','vedant@example.com','super_manager','Humility',0,'super_manager','2025-07-29 13:46:16',2,2025),(369,'lazross@evaluationportal.in','vedant@example.com','super_manager','Integrity',7,'super_manager','2025-07-29 13:46:16',2,2025),(370,'lazross@evaluationportal.in','vedant@example.com','super_manager','Collegiality',7,'super_manager','2025-07-29 13:46:16',2,2025),(371,'lazross@evaluationportal.in','vedant@example.com','super_manager','Attitude',7,'super_manager','2025-07-29 13:46:16',2,2025),(372,'lazross@evaluationportal.in','vedant@example.com','super_manager','Time Management',7,'super_manager','2025-07-29 13:46:16',2,2025),(373,'lazross@evaluationportal.in','vedant@example.com','super_manager','Initiative',7,'super_manager','2025-07-29 13:46:16',2,2025),(374,'lazross@evaluationportal.in','vedant@example.com','super_manager','Communication',7,'super_manager','2025-07-29 13:46:16',2,2025),(375,'lazross@evaluationportal.in','vedant@example.com','super_manager','Compassion',7,'super_manager','2025-07-29 13:46:16',2,2025),(376,'lazross@evaluationportal.in','vedant@example.com','super_manager','Knowledge & Awareness',7,'super_manager','2025-07-29 13:46:16',2,2025),(377,'lazross@evaluationportal.in','vedant@example.com','super_manager','Future readiness',7,'super_manager','2025-07-29 13:46:16',2,2025),(378,'lazross@evaluationportal.in','vedant@example.com','super_manager','Informal leadership',7,'super_manager','2025-07-29 13:46:16',2,2025),(379,'lazross@evaluationportal.in','vedant@example.com','super_manager','Team Development',7,'super_manager','2025-07-29 13:46:16',2,2025),(380,'lazross@evaluationportal.in','vedant@example.com','super_manager','Process adherence',7,'super_manager','2025-07-29 13:46:16',2,2025);
/*!40000 ALTER TABLE `user_ratings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('employee','manager','hr','admin','super_manager') NOT NULL,
  `managed_by` text,
  `username` text NOT NULL,
  `is_dormant` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=52 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'john@example.com','$2b$12$Bopv02SJuTL6v6riXZF0dOfAEmSPO0G/Wsnjv55bZ7muSiXmqkGuy','manager','Laz Ross','Jack',0),(2,'vedant@example.com','$2a$12$j.xjgahJlWt171n2VyVttOGg0YI63Qmsf79XUzhY0Op0PQFbI1QBe','manager','Laz Ross','Vedant',0),(4,'alice@example.com','$2a$12$UPB/.lEcYR/pzPD2mOjdPOuLV8c8DxaoH4qF8LHqRwbastUitMxhW','employee',NULL,'Alice',0),(5,'bob@example.com','$2a$12$g7r679cFZqDGDej1Kvwaxu8m9BBHAG9ECtVpkd6w9ENsuOhWZKj4K','employee','Vedant','Bob',0),(6,'claire@example.com','$2b$12$YMpDXvnp7ehC5prC0Hzune50euGzx0XbLM6cWWaUGuFDIdNi9tvXG','employee','Vedant','Claire',0),(7,'admin@example.com','$2a$12$gHbgzms80uL0jFtNyTiAveP31tlbyPqmCw8IhJDM3hfsAwMcr1dp2','admin','XYZ','XYZ',0),(8,'riya@example.com','$2b$12$CnbOmRXEnEpvxETK9EijouKtxQzkMQuIRo7cLdTmEl8hg5wCueG..','hr','XYZ','Riya',0),(9,'james@example.com','$2b$12$BqJOYgrL6AJf2gp07fNCTuWi1l5Mh0YZh9LTwVXGh4r11FOsjVsGi','employee','Vedant','James',0),(10,'lol@example.com','$2b$12$aC5yQcP6RcuG3OHlLPGDGeVSt75KLuy8QjffpL9DKmJq0MvCjHbdO','employee',NULL,'LolLol',0),(11,'chen@example.com','$2b$12$sNFv0mGrDlgZ4R6ZQpeCwugSL82ir5BgW/6qI1cQv9rX6dSKDAwzO','employee',NULL,'Chen',0),(13,'adam@exampke.com','$2b$12$jliYqOFJPI3GM1v3CqwIw.GU3E64p05116c8KuRcOOSO6f7kzTk0a','employee','Vedant','Adam',0),(15,'test1234@example.com','$2b$12$eDNpx3sepJ/RBo8zIQiS4.zYidlZA06Up8kO1nnO/.Qwc0dGIkR76','employee','Vedant','Testfour',0),(16,'one@example.com','$2b$12$HQwKQpeBQ.W23fxrmUAuveU1.4xbOd.dbvOVP.2f8ymnGwJQ4LquK','employee','Vedant','One',0),(17,'two@example.com','$2b$12$wVxH3UKy1Vz9QNg02Zctb.8r4OL2JAreAAfv6gltlF.0iAMYp73Si','employee',NULL,'Two',0),(18,'three@example.com','$2b$12$jo4NHZID4mN8IWsd7U7dvOJ1ETZoz0mRFxsy.sF.itMCeEdPEaxCG','employee',NULL,'Three',0),(19,'four@example.com','$2b$12$NljuoT8V1wUOdlMP7ZZQtOZaqqFMiKDCPHN3E7HKl6BYD.UXjInce','employee',NULL,'Four',0),(20,'five@example.com','$2b$12$peV31LcCzxLS3Hzmopy9OORfQ8l8OsswunacdtKw9vc80WVGYuBKW','employee','Vedant','Five',0),(21,'six@example.com','$2b$12$pv9J9vvyNpi20mGCl5peH.phFjLROO0/Ul6nmslRrfWzjSMkObrXa','employee',NULL,'Six',0),(28,'plane@example.com','$2b$12$rqKOGBS3vDy0A0sxigqVUOTfFUnRS191t1lju0vSNHKyZhjLJfoR6','employee',NULL,'Plane',0),(30,'kangkang@78.llo','$2b$12$UJVuVQ0FWTLQ72FjwEiSZOxIo5LKa0CwvqONvk37KoZsa8k0sc.oq','manager',NULL,'KingKOng',0),(32,'silverhand@example.com','$2b$12$taA8c2qn7POYDhJXQpvm0eKLNOckwrvQiEVz7mdTZutU5Pw2.Zx3C','employee','Vedant','Silverhand',0),(38,'razer@example.com','$2b$12$vd2v3mC01CXFSfoZ0pzad.6C5PUPjt9fYV1yJR1zmNe5sqi7VRLOG','employee',NULL,'Razer',0),(39,'razer2@example.com','$2b$12$GCjKM64kLpIKD2ao9DdLxOnkP/eHehwVncqtPvBD0SyOOL2Bpknyi','employee',NULL,'RazerTwo',0),(40,'domino@example.com','$2b$12$ksLh1CbJjU2BwMrz5uoWHecH77Qn8l3KzjQzE4cvwEX.MyLtGdOLK','employee','Jack','Domino',0),(41,'domino2@example.com','$2b$12$ZwmJ9yLBz5UTzYLBTX1bZuAh/eZh.us3V6CJ9Y7J3gpea4Ph0rPGW','employee','Jack','Domino',0),(42,'kangaroo@example.com','$2b$12$7rXMdVXgSPv/t1HR9gTen.NumgQ4CYVsjiR7fRj2MI3LbrKYf1mym','employee','Jack','Kangaroo',0),(43,'present@example.com','$2b$12$ICUZv0zGs5PYKzmR6Nu8AeHtyNw68a3BWteaYFQ1QBGx5iG0A/EYa','employee','Jack','5050',0),(44,'sarthak12@example.com','$2b$12$QHuYixmPs6G6mUzqjw/WL./g.fhWezcY4F6S2NthkPJXHMYyMu28e','employee','Jack','Sarthak',0),(45,'clarkkent@example.com','$2b$12$w3zDeD1e8Q26m7gQxwaGaeT06/ii/Ig.diTVcZTVTSbiaVo.nZaUC','employee','Jack','Clark Kent',0),(47,'test123@example.com','$2b$12$CQQ69Km.Y0XGrqAXNZM.q.6WbGMaEuLZ8OB6/AGpFPOvmVDnT47iy','employee','Vedant','Test123',0),(48,'cargo123@example.com','$2b$12$eMvhJg4sv0uKqsda.xUm2u0Dy//KsxcBf1jz.3MqLGymNO3gvRMqy','employee','Jack','Cargo',0),(50,'harry@example.com','$2b$12$ZLVOvD72G2rNXLmNCTRtLO5r1afgbBpjGPpb0E46VmMw73ToELITe','employee','Vedant','Harry Bron',0),(51,'lazross@evaluationportal.in','$2b$12$Xv6yYTUVfJO9PJ0If0.u0OgXRd.Nx9kUPsu6crJjsrZaOSN7ksnaO','super_manager','','Laz Ross',0);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-07-29 16:38:47
