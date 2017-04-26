-- phpMyAdmin SQL Dump
-- version 4.0.10.14
-- http://www.phpmyadmin.net
--
-- Host: localhost:3306
-- Generation Time: Apr 25, 2017 at 10:28 PM
-- Server version: 5.6.32-78.1-log
-- PHP Version: 5.6.20

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `batcave1_corelex`
--

-- --------------------------------------------------------

--
-- Table structure for table `basic_types`
--

CREATE TABLE IF NOT EXISTS `basic_types` (
  `basic_type` varchar(10) NOT NULL,
  `synset_number` int(11) NOT NULL,
  `synset_elements` varchar(255) NOT NULL,
  KEY `basic_type` (`basic_type`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `corelex_types`
--

CREATE TABLE IF NOT EXISTS `corelex_types` (
  `corelex_type` varchar(5) NOT NULL,
  `polysemous_type` varchar(25) NOT NULL,
  KEY `basic_types` (`polysemous_type`),
  KEY `corelex_type` (`corelex_type`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `nouns`
--

CREATE TABLE IF NOT EXISTS `nouns` (
  `noun` varchar(255) NOT NULL,
  `corelex_type` varchar(5) NOT NULL,
  `polysemous_type` varchar(25) NOT NULL,
  PRIMARY KEY (`noun`),
  KEY `corelex_type` (`corelex_type`),
  KEY `polysemous_type` (`polysemous_type`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
