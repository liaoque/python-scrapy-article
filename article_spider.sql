/*
Navicat MySQL Data Transfer

Source Server         : localhost
Source Server Version : 50717
Source Host           : localhost:3306
Source Database       : article_spider

Target Server Type    : MYSQL
Target Server Version : 50717
File Encoding         : 65001

Date: 2017-11-20 00:48:44
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for mc_article
-- ----------------------------
DROP TABLE IF EXISTS `mc_article`;
CREATE TABLE `mc_article` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL COMMENT '标题',
  `thumbnail` varchar(255) DEFAULT NULL COMMENT '缩略图',
  `ctime` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `status` tinyint(4) DEFAULT '1' COMMENT '1.发布, 2, 未发布',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of mc_article
-- ----------------------------

-- ----------------------------
-- Table structure for mc_article_body
-- ----------------------------
DROP TABLE IF EXISTS `mc_article_body`;
CREATE TABLE `mc_article_body` (
  `aid` int(11) NOT NULL DEFAULT '0' COMMENT 'article表id',
  `body` text COMMENT '内容',
  PRIMARY KEY (`aid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of mc_article_body
-- ----------------------------

-- ----------------------------
-- Table structure for mc_duanzi
-- ----------------------------
DROP TABLE IF EXISTS `mc_duanzi`;
CREATE TABLE `mc_duanzi` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `body` text,
  `fingerprint` char(32) DEFAULT NULL COMMENT 'body的md5签名',
  `ctime` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `status` tinyint(4) DEFAULT '1' COMMENT '1.发布, -1未发布',
  PRIMARY KEY (`id`),
  UNIQUE KEY `fingerprint` (`fingerprint`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of mc_duanzi
-- ----------------------------

-- ----------------------------
-- Table structure for mc_gif
-- ----------------------------
DROP TABLE IF EXISTS `mc_gif`;
CREATE TABLE `mc_gif` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL,
  `src` varchar(255) DEFAULT NULL,
  `fingerprint` char(32) DEFAULT NULL,
  `ctime` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `status` tinyint(4) DEFAULT '1' COMMENT '1.发布, -1未发布',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of mc_gif
-- ----------------------------

-- ----------------------------
-- Table structure for mc_image_list
-- ----------------------------
DROP TABLE IF EXISTS `mc_image_list`;
CREATE TABLE `mc_image_list` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `pid` int(11) DEFAULT NULL COMMENT '对应表id',
  `src` varchar(255) DEFAULT NULL,
  `type` tinyint(255) DEFAULT '1' COMMENT '1.表示写真表',
  PRIMARY KEY (`id`),
  KEY `pid` (`pid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of mc_image_list
-- ----------------------------

-- ----------------------------
-- Table structure for mc_video
-- ----------------------------
DROP TABLE IF EXISTS `mc_video`;
CREATE TABLE `mc_video` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL,
  `src` varchar(255) DEFAULT NULL COMMENT '视频连接',
  `thumbnail` varchar(255) DEFAULT NULL COMMENT '缩略图',
  `ctime` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `status` tinyint(4) DEFAULT '1' COMMENT '1.发布, 2, 未发布',
  `fingerprint` char(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `fingerprint` (`fingerprint`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of mc_video
-- ----------------------------

-- ----------------------------
-- Table structure for mc_xiezhen
-- ----------------------------
DROP TABLE IF EXISTS `mc_xiezhen`;
CREATE TABLE `mc_xiezhen` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL,
  `thumbnail` varchar(255) DEFAULT NULL COMMENT '缩略图',
  `status` tinyint(4) DEFAULT '1' COMMENT '1发布， -1未发布',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of mc_xiezhen
-- ----------------------------

-- ----------------------------
-- Table structure for unique_baisibudejie
-- ----------------------------
DROP TABLE IF EXISTS `unique_baisibudejie`;
CREATE TABLE `unique_baisibudejie` (
  `fingerprint` char(32) NOT NULL,
  PRIMARY KEY (`fingerprint`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of unique_baisibudejie
-- ----------------------------

-- ----------------------------
-- Table structure for unique_baozouribao
-- ----------------------------
DROP TABLE IF EXISTS `unique_baozouribao`;
CREATE TABLE `unique_baozouribao` (
  `id` int(11) NOT NULL DEFAULT '0',
  `view_url` varchar(255) DEFAULT NULL COMMENT '实际文档url',
  `type` tinyint(4) DEFAULT NULL COMMENT '类型',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of unique_baozouribao
-- ----------------------------

-- ----------------------------
-- Table structure for unique_qiushibaike
-- ----------------------------
DROP TABLE IF EXISTS `unique_qiushibaike`;
CREATE TABLE `unique_qiushibaike` (
  `id` int(11) NOT NULL DEFAULT '0',
  `view_url` varchar(255) DEFAULT NULL COMMENT '实际文档url',
  `type` tinyint(4) DEFAULT NULL COMMENT '类型',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of unique_qiushibaike
-- ----------------------------

-- ----------------------------
-- Table structure for unique_xiezhen
-- ----------------------------
DROP TABLE IF EXISTS `unique_xiezhen`;
CREATE TABLE `unique_xiezhen` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `view_url` varchar(255) DEFAULT NULL COMMENT '实际文档url',
  `type` tinyint(4) DEFAULT '1' COMMENT '类型',
  `fingerprint` char(32) DEFAULT NULL COMMENT 'md5的值',
  PRIMARY KEY (`id`),
  UNIQUE KEY `fingerprint` (`fingerprint`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of unique_xiezhen
-- ----------------------------
