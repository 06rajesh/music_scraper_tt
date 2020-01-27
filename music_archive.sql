-- Adminer 4.7.3 MySQL dump

SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';

DROP DATABASE IF EXISTS `music_archive`;
CREATE DATABASE `music_archive` /*!40100 DEFAULT CHARACTER SET latin1 */;
USE `music_archive`;

DROP TABLE IF EXISTS `albums`;
CREATE TABLE `albums` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` text COLLATE utf8_bin NOT NULL,
  `artist` text COLLATE utf8_bin NOT NULL,
  `url` text COLLATE utf8_bin NOT NULL,
  `image` text COLLATE utf8_bin,
  `length` tinytext COLLATE utf8_bin,
  `released` date DEFAULT NULL,
  `label` text COLLATE utf8_bin,
  `desc` text COLLATE utf8_bin,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;


DROP TABLE IF EXISTS `album_genres`;
CREATE TABLE `album_genres` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `album` int(11) NOT NULL,
  `genre` text COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`id`),
  KEY `album` (`album`),
  CONSTRAINT `album_genres_ibfk_1` FOREIGN KEY (`album`) REFERENCES `albums` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;


DROP TABLE IF EXISTS `musics`;
CREATE TABLE `musics` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` text COLLATE utf8_bin NOT NULL,
  `artist` text COLLATE utf8_bin NOT NULL,
  `duration` tinytext COLLATE utf8_bin NOT NULL,
  `uploaded` date DEFAULT NULL,
  `listens` int(11) DEFAULT NULL,
  `starred` int(11) DEFAULT NULL,
  `comments` int(11) DEFAULT NULL,
  `downloads` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;


DROP TABLE IF EXISTS `music_genres`;
CREATE TABLE `music_genres` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `music` int(11) NOT NULL,
  `genre` text COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`id`),
  KEY `music` (`music`),
  CONSTRAINT `music_genres_ibfk_1` FOREIGN KEY (`music`) REFERENCES `musics` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;


-- 2020-01-27 19:19:38
