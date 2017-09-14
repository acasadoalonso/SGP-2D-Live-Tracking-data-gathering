-- phpMyAdmin SQL Dump
-- version 4.5.4.1deb2ubuntu2
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: May 24, 2017 at 05:02 PM
-- Server version: 5.7.18-0ubuntu0.16.04.1
-- PHP Version: 7.0.15-0ubuntu0.16.04.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `APRSLOG`
--

DELIMITER $$
--
-- Functions
--
CREATE DEFINER=`ogn`@`%` FUNCTION `GETBEARING` (`lat1` DOUBLE, `lon1` DOUBLE, `lat2` DOUBLE, `lon2` DOUBLE) RETURNS DOUBLE NO SQL
    DETERMINISTIC
    COMMENT 'Returns the initial bearing, in degrees, to follow the great circle route             from point (lat1,lon1), to point (lat2,lon2)'
BEGIN
	DECLARE bearing FLOAT;
    SET bearing= (360.0 + 
      DEGREES(ATAN2(
       SIN(RADIANS(lon2-lon1))*COS(RADIANS(lat2)),
       COS(RADIANS(lat1))*SIN(RADIANS(lat2))-SIN(RADIANS(lat1))*COS(RADIANS(lat2))*
            COS(RADIANS(lon2-lon1))
      ))
     ) % 360.0;
     RETURN bearing;
END$$

CREATE DEFINER=`ogn`@`%` FUNCTION `GETBEARINGROSE` (`lat1` DOUBLE, `lon1` DOUBLE, `lat2` DOUBLE, `lon2` DOUBLE) RETURNS VARCHAR(5) CHARSET utf8 NO SQL
    DETERMINISTIC
    COMMENT 'Returns the initial bearing, in degrees, to follow the great circle route             from point (lat1,lon1), to point (lat2,lon2)'
BEGIN
	DECLARE bearing FLOAT;
	DECLARE bearingRose VARCHAR(5);
    SET bearing= (360.0 + 
      DEGREES(ATAN2(
       SIN(RADIANS(lon2-lon1))*COS(RADIANS(lat2)),
       COS(RADIANS(lat1))*SIN(RADIANS(lat2))-SIN(RADIANS(lat1))*COS(RADIANS(lat2))*
            COS(RADIANS(lon2-lon1))
      ))
     ) % 360.0;
     SET bearingRose='N';
     IF bearing>=0 AND bearing<11.5 THEN SET bearingRose='N';
     ELSEIF bearing>=11.5 AND bearing<34 THEN SET bearingRose='NNE';
     ELSEIF bearing>=34 AND bearing<56.5 THEN SET bearingRose='NE';
     ELSEIF bearing>=56.5 AND bearing<79 THEN SET bearingRose='ENE';
     ELSEIF bearing>=79 AND bearing<101.5 THEN SET bearingRose='E';
     ELSEIF bearing>=101.5 AND bearing<124 THEN SET bearingRose='ESE';
     ELSEIF bearing>=124 AND bearing<146.5 THEN SET bearingRose='SE';
     ELSEIF bearing>=146.5 AND bearing<169 THEN SET bearingRose='SSE';
     ELSEIF bearing>=169 AND bearing<191.5 THEN SET bearingRose='S';
     ELSEIF bearing>=191.5 AND bearing<214 THEN SET bearingRose='SSW';
     ELSEIF bearing>=214 AND bearing<236.5 THEN SET bearingRose='SW';
     ELSEIF bearing>=236.5 AND bearing<259 THEN SET bearingRose='WSW';
     ELSEIF bearing>=259 AND bearing<281.5 THEN SET bearingRose='W';
     ELSEIF bearing>=281.5 AND bearing<304 THEN SET bearingRose='WNW';
     ELSEIF bearing>=304 AND bearing<326.5 THEN SET bearingRose='NW';
     ELSEIF bearing>=326.5 AND bearing<349 THEN SET bearingRose='NNW';
     ELSE SET bearingRose='N';
     END IF;
     
     RETURN bearingRose;
END$$

CREATE DEFINER=`ogn`@`%` FUNCTION `GETDISTANCE` (`deg_lat1` FLOAT, `deg_lng1` FLOAT, `deg_lat2` FLOAT, `deg_lng2` FLOAT) RETURNS FLOAT BEGIN 
  DECLARE distance FLOAT;
  DECLARE delta_lat FLOAT; 
  DECLARE delta_lng FLOAT; 
  DECLARE lat1 FLOAT; 
  DECLARE lat2 FLOAT;
  DECLARE a FLOAT;

  SET distance = 0;

  
  SET delta_lat = radians(deg_lat2 - deg_lat1); 
  SET delta_lng = radians(deg_lng2 - deg_lng1); 
  SET lat1 = radians(deg_lat1); 
  SET lat2 = radians(deg_lat2); 

  
  SET a = sin(delta_lat/2.0) * sin(delta_lat/2.0) + sin(delta_lng/2.0) * sin(delta_lng/2.0) * cos(lat1) * cos(lat2); 
  SET distance = 3956.6 * 2 * atan2(sqrt(a),  sqrt(1-a)); 

  RETURN distance;
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `GLIDERS`
--

CREATE TABLE `GLIDERS` (
  `idglider` char(9) DEFAULT NULL,
  `registration` char(9) DEFAULT NULL,
  `cn` char(3) DEFAULT NULL,
  `type` text,
  `source` char(1) DEFAULT NULL,
  `flarmtype` char(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `GLIDERS_POSITIONS`
--

CREATE TABLE `GLIDERS_POSITIONS` (
  `flarmId` varchar(50) NOT NULL,
  `lat` float DEFAULT '0',
  `lon` float DEFAULT '0',
  `altitude` float DEFAULT '0',
  `course` float DEFAULT '0',
  `date` char(6) DEFAULT '000000',
  `time` char(6) DEFAULT '000000',
  `rot` float DEFAULT '0',
  `speed` float DEFAULT '0',
  `distance` float DEFAULT '0',
  `climb` float DEFAULT '0',
  `station` varchar(50) DEFAULT 'NONE',
  `sensitivity` float NOT NULL DEFAULT '0',
  `gps` char(6) DEFAULT '',
  `lastFixTx` datetime DEFAULT NULL,
  `ground` int(11) NOT NULL DEFAULT '-1',
  `source` varchar(8) CHARACTER SET utf16 NOT NULL DEFAULT 'OGN'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `OGNDATA`
--

CREATE TABLE `OGNDATA` (
  `idflarm` char(9) DEFAULT NULL,
  `date` char(6) DEFAULT NULL,
  `time` char(6) DEFAULT NULL,
  `station` char(9) DEFAULT NULL,
  `latitude` float DEFAULT NULL,
  `longitude` float DEFAULT NULL,
  `altitude` int(11) DEFAULT NULL,
  `speed` float DEFAULT NULL,
  `course` int(11) DEFAULT NULL,
  `roclimb` int(11) DEFAULT NULL,
  `rot` float DEFAULT NULL,
  `sensitivity` float DEFAULT NULL,
  `gps` char(6) DEFAULT NULL,
  `uniqueid` char(16) DEFAULT NULL,
  `distance` float DEFAULT NULL,
  `extpos` char(5) DEFAULT NULL,
  `source` varchar(8) NOT NULL DEFAULT 'OGN'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Triggers `OGNDATA`
--
DELIMITER $$
CREATE TRIGGER `INSERTGLIDERPOSITION` AFTER INSERT ON `OGNDATA` FOR EACH ROW IF ((SELECT count(flarmId) FROM GLIDERS_POSITIONS WHERE flarmId=NEW.idflarm)=0) THEN
	INSERT INTO GLIDERS_POSITIONS  (flarmId, lat, lon, altitude, course, date, time, rot, speed, climb, station, sensitivity, gps, lastFixTx, source) VALUES (NEW.idflarm, NEW.latitude, NEW.longitude, NEW.altitude, NEW.course, NEW.date, NEW.time, NEW.rot, NEW.speed, NEW.roclimb, NEW.station, NEW.sensitivity, NEW.gps, NOW(), NEW.source);
	   
ELSE
   UPDATE GLIDERS_POSITIONS SET lat=NEW.latitude, lon=NEW.longitude, altitude=NEW.altitude, course=NEW.course, date=NEW.date, time=NEW.time, rot=NEW.rot, speed=NEW.speed, distance=NEW.distance, climb=NEW.roclimb, station=NEW.station, gps=NEW.gps, sensitivity=NEW.sensitivity, lastFixTx=NOW(), source=NEW.source where flarmId=NEW.idflarm;

	if(NEW.speed=0) THEN
      UPDATE GLIDERS_POSITIONS set climb=0  where flarmId=NEW.idflarm;
    END IF;
    UPDATE RECEIVERS_STATUS set lastFixRx=NOW(), maxDistance=(select ifnull(max(distance),0) from OGNDATA where station=NEW.station and date=DATE_FORMAT(NOW(), '%y%m%d')) where idrec=NEW.station;
	
END IF
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `OGNDATAARCHIVE`
--

CREATE TABLE `OGNDATAARCHIVE` (
  `idflarm` char(9) DEFAULT NULL,
  `date` char(6) DEFAULT NULL,
  `time` char(6) DEFAULT NULL,
  `station` char(9) DEFAULT NULL,
  `latitude` float DEFAULT NULL,
  `longitude` float DEFAULT NULL,
  `altitude` int(11) DEFAULT NULL,
  `speed` float DEFAULT NULL,
  `course` int(11) DEFAULT NULL,
  `roclimb` int(11) DEFAULT NULL,
  `rot` float DEFAULT NULL,
  `sensitivity` float DEFAULT NULL,
  `gps` char(6) DEFAULT NULL,
  `uniqueid` char(16) DEFAULT NULL,
  `distance` float DEFAULT NULL,
  `extpos` char(5) DEFAULT NULL,
  `source` varchar(8) NOT NULL DEFAULT 'OGN'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `RECEIVERS`
--

CREATE TABLE `RECEIVERS` (
  `idrec` char(9) DEFAULT NULL COMMENT 'Id of station',
  `lati` double DEFAULT NULL,
  `longi` double DEFAULT NULL,
  `alti` double DEFAULT NULL,
  `otime` datetime(6) DEFAULT NULL,
  `version` varchar(20) DEFAULT NULL,
  `cpu` float DEFAULT NULL,
  `temp` float DEFAULT NULL,
  `rf` varchar(20) DEFAULT NULL,
  `status` varchar(255) DEFAULT NULL COMMENT 'Station status'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Triggers `RECEIVERS`
--
DELIMITER $$
CREATE TRIGGER `UPDATERECEIVERSSTATUS` AFTER INSERT ON `RECEIVERS` FOR EACH ROW IF ((SELECT count(idrec) FROM RECEIVERS_STATUS WHERE idrec=NEW.idrec)=0) THEN
	INSERT INTO RECEIVERS_STATUS  (alti, cpu, idrec, lati, longi, otime, rf, status, temp, version, lastFixRx) VALUES (NEW.alti, NEW.cpu, NEW.idrec, NEW.lati, NEW.longi, NEW.otime, NEW.rf, NEW.status, NEW.temp, NEW.version, NOW());
	   
	ELSE
	   UPDATE RECEIVERS_STATUS SET alti=NEW.alti, cpu=NEW.cpu, lati=NEW.lati, longi=NEW.longi, otime=NEW.otime, rf=NEW.rf, status=NEW.status, temp=NEW.temp, version=NEW.version, lastFixRx=NOW() where idrec=NEW.idrec;
 END IF
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `RECEIVERS_STATUS`
--

CREATE TABLE `RECEIVERS_STATUS` (
  `idrec` char(9) DEFAULT NULL COMMENT 'Id of station',
  `lati` double DEFAULT NULL,
  `longi` double DEFAULT NULL,
  `alti` double DEFAULT NULL,
  `lastFixRx` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `otime` datetime(6) DEFAULT NULL,
  `version` varchar(20) DEFAULT NULL,
  `cpu` float DEFAULT NULL,
  `temp` float DEFAULT NULL,
  `rf` varchar(20) DEFAULT NULL,
  `status` varchar(255) DEFAULT NULL COMMENT 'Station status',
  `maxDistance` float NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `TRKDEVICES`
--

CREATE TABLE `TRKDEVICES` (
  `id` varchar(16) NOT NULL,
  `owner` varchar(64) NOT NULL,
  `spotid` varchar(36) NOT NULL,
  `spotpasswd` varchar(16) DEFAULT NULL,
  `compid` varchar(3) NOT NULL,
  `model` varchar(16) NOT NULL,
  `registration` varchar(9) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `devicetype` varchar(6) NOT NULL DEFAULT 'SPOT',
  `flarmid` varchar(9) DEFAULT NULL COMMENT 'Flarmid to link'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `WAYPOINTS`
--

CREATE TABLE `WAYPOINTS` (
  `idWaypoint` int(11) NOT NULL,
  `waypoint` varchar(100) NOT NULL,
  `waypointType` varchar(15) NOT NULL,
  `waypointCountry` varchar(5) NOT NULL,
  `waypointLat` float NOT NULL,
  `waypointLon` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `GLIDERS`
--
ALTER TABLE `GLIDERS`
  ADD UNIQUE KEY `idglider` (`idglider`),
  ADD UNIQUE KEY `GLIDERIDX` (`idglider`);

--
-- Indexes for table `GLIDERS_POSITIONS`
--
ALTER TABLE `GLIDERS_POSITIONS`
  ADD KEY `flarmId` (`flarmId`) USING BTREE;

--
-- Indexes for table `OGNDATA`
--
ALTER TABLE `OGNDATA`
  ADD KEY `Flr` (`idflarm`),
  ADD KEY `Sta` (`station`);

--
-- Indexes for table `OGNDATAARCHIVE`
--
ALTER TABLE `OGNDATAARCHIVE`
  ADD KEY `Flr` (`idflarm`),
  ADD KEY `Sta` (`station`);

--
-- Indexes for table `RECEIVERS`
--
ALTER TABLE `RECEIVERS`
  ADD UNIQUE KEY `RECEIVERSIDX` (`idrec`,`otime`) USING BTREE;

--
-- Indexes for table `RECEIVERS_STATUS`
--
ALTER TABLE `RECEIVERS_STATUS`
  ADD UNIQUE KEY `RECEIVERS_STATUSIDX` (`idrec`,`otime`) USING BTREE;

--
-- Indexes for table `TRKDEVICES`
--
ALTER TABLE `TRKDEVICES`
  ADD UNIQUE KEY `id` (`id`),
  ADD KEY `spotid` (`spotid`);

--
-- Indexes for table `WAYPOINTS`
--
ALTER TABLE `WAYPOINTS`
  ADD PRIMARY KEY (`idWaypoint`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `WAYPOINTS`
--
ALTER TABLE `WAYPOINTS`
  MODIFY `idWaypoint` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=491;
DELIMITER $$
--
-- Events
--
CREATE DEFINER=`ogn`@`%` EVENT `restore_max_distance` ON SCHEDULE EVERY 1 DAY STARTS '2016-12-20 00:30:00' ON COMPLETION NOT PRESERVE ENABLE DO UPDATE RECEIVERS_STATUS SET maxDistance=0 where maxDistance<>0 AND ((select count(*) from OGNDATA where station=idrec and date=CONCAT(RIGHT(YEAR(NOW()),2), MONTH(NOW()), DAY(NOW())))=0)$$

DELIMITER ;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
