-- Create database
CREATE DATABASE IF NOT EXISTS `proctor`;
USE `proctor`;

-- Example table: admin
CREATE TABLE `admin` (
  `admin_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`admin_id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `complaints` (
  `complaint_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `authority_id` int DEFAULT NULL,
  `complaint_text` text NOT NULL,
  `reply_text` text,
  `status` varchar(20) DEFAULT 'Pending',
  `submission_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`complaint_id`),
  KEY `user_id` (`user_id`),
  KEY `authority_id` (`authority_id`),
  CONSTRAINT `complaints_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `complaints_ibfk_2` FOREIGN KEY (`authority_id`) REFERENCES `exam_authority` (`authority_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `exam_authority` (
  `authority_id` int NOT NULL AUTO_INCREMENT,
  `fullname` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `username` varchar(50) NOT NULL,
  `contact` varchar(15) DEFAULT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`authority_id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `exam_details` (
  `question_id` int NOT NULL AUTO_INCREMENT,
  `exam_id` int NOT NULL,
  `authority_id` int NOT NULL,
  `exam_title` varchar(255) NOT NULL,
  `exam_type` enum('subjective','objective') NOT NULL,
  `question_text` text,
  `question_image` longblob,
  `marks` int DEFAULT '0',
  `options` text,
  `exam_duration` int DEFAULT NULL,
  `exam_rules` text,
  `exam_date` date DEFAULT NULL,
  `exam_time` time DEFAULT NULL,
  `exam_link` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`question_id`),
  KEY `authority_id` (`authority_id`),
  KEY `exam_id` (`exam_id`),
  CONSTRAINT `exam_details_ibfk_1` FOREIGN KEY (`authority_id`) REFERENCES `exam_authority` (`authority_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=118 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `exam_info` (
  `exam_id` int NOT NULL,
  `authority_id` int NOT NULL,
  `exam_title` varchar(255) NOT NULL,
  `exam_duration` int DEFAULT NULL,
  `exam_rules` text,
  `exam_date` date DEFAULT NULL,
  `exam_time` time DEFAULT NULL,
  `exam_link` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`exam_id`),
  KEY `authority_id` (`authority_id`),
  CONSTRAINT `exam_info_ibfk_1` FOREIGN KEY (`authority_id`) REFERENCES `exam_authority` (`authority_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `exam_questions` (
  `question_id` int NOT NULL AUTO_INCREMENT,
  `exam_id` int NOT NULL,
  `authority_id` int NOT NULL,
  `exam_title` varchar(255) NOT NULL,
  `exam_type` enum('subjective','objective') NOT NULL,
  `question_text` text,
  `question_image` longblob,
  `marks` int DEFAULT '0',
  `options` text,
  `correct_answer` int DEFAULT NULL,
  PRIMARY KEY (`question_id`),
  KEY `exam_id` (`exam_id`),
  KEY `authority_id` (`authority_id`),
  CONSTRAINT `exam_questions_ibfk_1` FOREIGN KEY (`exam_id`) REFERENCES `exam_info` (`exam_id`) ON DELETE CASCADE,
  CONSTRAINT `exam_questions_ibfk_2` FOREIGN KEY (`authority_id`) REFERENCES `exam_authority` (`authority_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=113 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `exam_reference_images` (
  `ref_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `exam_id` int NOT NULL,
  `image1` longblob NOT NULL,
  `image2` longblob NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ref_id`),
  UNIQUE KEY `unique_user_exam` (`user_id`,`exam_id`),
  KEY `exam_id` (`exam_id`),
  CONSTRAINT `exam_reference_images_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `exam_reference_images_ibfk_2` FOREIGN KEY (`exam_id`) REFERENCES `exam_info` (`exam_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `exam_violations` (
  `violation_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `exam_id` int NOT NULL,
  `fullname` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `violation_type` varchar(50) NOT NULL,
  `face_count` int NOT NULL,
  `violation_image` mediumblob,
  `timestamp` datetime NOT NULL,
  PRIMARY KEY (`violation_id`),
  KEY `user_id` (`user_id`),
  KEY `exam_id` (`exam_id`),
  CONSTRAINT `exam_violations_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `exam_violations_ibfk_2` FOREIGN KEY (`exam_id`) REFERENCES `exam_info` (`exam_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4560 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `student_academic_info` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `course` varchar(100) NOT NULL,
  `year` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `student_academic_info_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `student_answers` (
  `answer_id` int NOT NULL,
  `question_id` int NOT NULL,
  `answer` text NOT NULL,
  PRIMARY KEY (`answer_id`,`question_id`),
  KEY `question_id` (`question_id`),
  CONSTRAINT `student_answers_ibfk_1` FOREIGN KEY (`answer_id`) REFERENCES `student_result` (`answer_id`) ON DELETE CASCADE,
  CONSTRAINT `student_answers_ibfk_2` FOREIGN KEY (`question_id`) REFERENCES `exam_questions` (`question_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `student_answers_details` (
  `answer_id` int NOT NULL,
  `question_id` int NOT NULL,
  `answer` text NOT NULL,
  PRIMARY KEY (`answer_id`,`question_id`),
  KEY `question_id` (`question_id`),
  CONSTRAINT `student_answers_details_ibfk_1` FOREIGN KEY (`answer_id`) REFERENCES `student_answers_summary` (`answer_id`) ON DELETE CASCADE,
  CONSTRAINT `student_answers_details_ibfk_2` FOREIGN KEY (`question_id`) REFERENCES `exam_questions` (`question_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `student_answers_summary` (
  `answer_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `exam_id` int NOT NULL,
  `submitted_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `fullname` varchar(100) NOT NULL,
  `exam_title` varchar(255) NOT NULL,
  `score` int DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`answer_id`),
  UNIQUE KEY `unique_submission` (`user_id`,`exam_id`),
  KEY `exam_id` (`exam_id`),
  CONSTRAINT `student_answers_summary_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `student_answers_summary_ibfk_2` FOREIGN KEY (`exam_id`) REFERENCES `exam_info` (`exam_id`)
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `student_personal_info` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `fullname` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `phone` varchar(15) NOT NULL,
  `address` text NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `student_personal_info_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `student_profiles` (
  `id` int NOT NULL,
  `profile_image` longblob,
  `face_encoding` blob,
  PRIMARY KEY (`id`),
  CONSTRAINT `student_profiles_ibfk_1` FOREIGN KEY (`id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `student_result` (
  `answer_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `exam_id` int NOT NULL,
  `submitted_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `fullname` varchar(100) NOT NULL,
  `exam_title` varchar(255) NOT NULL,
  `score` int DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`answer_id`),
  UNIQUE KEY `unique_submission` (`user_id`,`exam_id`),
  KEY `exam_id` (`exam_id`),
  CONSTRAINT `student_result_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `student_result_ibfk_2` FOREIGN KEY (`exam_id`) REFERENCES `exam_info` (`exam_id`)
) ENGINE=InnoDB AUTO_INCREMENT=205 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `submit_exam` (
  `submission_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `exam_id` int NOT NULL,
  `question_id` int NOT NULL,
  `answer` text,
  `submission_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`submission_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `teacher_profiles` (
  `id` int NOT NULL,
  `profile_image` longblob,
  `class` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `fullname` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `username` varchar(100) NOT NULL,
  `contact` varchar(15) NOT NULL,
  `password` varchar(255) NOT NULL,
  `session_id` varchar(255) DEFAULT NULL,
  `last_activity` datetime DEFAULT NULL,
  `is_hashed` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `contact` (`contact`)
) ENGINE=InnoDB AUTO_INCREMENT=73 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `verified_faces` (
  `user_id` int NOT NULL,
  `exam_id` int NOT NULL,
  `face_image` longtext NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`,`exam_id`),
  KEY `exam_id` (`exam_id`),
  CONSTRAINT `verified_faces_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `verified_faces_ibfk_2` FOREIGN KEY (`exam_id`) REFERENCES `exam_info` (`exam_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `violations` (
  `violation_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `exam_id` int NOT NULL,
  `timestamp` datetime NOT NULL,
  `violation_type` varchar(50) NOT NULL,
  `num_faces` int DEFAULT NULL,
  `image` blob,
  PRIMARY KEY (`violation_id`),
  KEY `user_id` (`user_id`),
  KEY `exam_id` (`exam_id`),
  CONSTRAINT `violations_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `violations_ibfk_2` FOREIGN KEY (`exam_id`) REFERENCES `exam_info` (`exam_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci


