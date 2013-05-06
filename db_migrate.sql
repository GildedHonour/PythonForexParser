delimiter $$

CREATE DATABASE `Forex` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci */$$

delimiter $$

CREATE TABLE `ForexCurrencies` (
  `Id` int(11) NOT NULL AUTO_INCREMENT COMMENT '  ',
  `Date` datetime DEFAULT NULL,
  `Currency` char(3) COLLATE utf8_unicode_ci DEFAULT NULL,
  `Event` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `Importance` varchar(45) COLLATE utf8_unicode_ci DEFAULT NULL,
  `Actual` varchar(10) COLLATE utf8_unicode_ci DEFAULT NULL,
  `Forecast` varchar(10) COLLATE utf8_unicode_ci DEFAULT NULL,
  `Previous` varchar(10) COLLATE utf8_unicode_ci DEFAULT NULL,
  `Notes` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=23410 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci$$

