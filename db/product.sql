DROP DATABASE only1DB;
CREATE DATABASE only1DB;
USE only1DB;

CREATE TABLE `dormitory` (
  `dormitoryID` TINYINT UNSIGNED PRIMARY KEY,
  `dormitory` VARCHAR(4) UNIQUE NOT NULL
);

INSERT INTO `dormitory`(`dormitoryID`, `dormitory`) VALUES
  (1, 'MOU'), (2, 'CEN'), (3, 'SEA'), (4, 'SPA');

CREATE TABLE `dormitoryPlace` (
  `dormitoryPlaceID` TINYINT UNSIGNED PRIMARY KEY,
  `dormitoryID` TINYINT UNSIGNED NOT NULL,
  `floor` TINYINT UNSIGNED NOT NULL,
  `place` VARCHAR(128) UNIQUE NOT NULL,
  FOREIGN KEY (`dormitoryID`) REFERENCES `dormitory`(`dormitoryID`) ON DELETE CASCADE ON UPDATE CASCADE,
  UNIQUE(`dormitoryID`, `floor`)
);

INSERT INTO `dormitoryPlace`(`dormitoryPlaceID`, `dormitoryID`, `floor`, `place`) VALUES
(1, 1, 1, 'MOU_1'), (2, 1, 2, 'MOU_2'), (3, 1, 3, 'MOU_3'), (4, 2, 1, 'CEN_1'), (5, 2, 2, 'CEN_2'), (6, 2, 3, 'CEN_3'),
(7, 3, 1, 'SEA_1'), (8, 3, 2, 'SEA_2'), (9, 3, 3, 'SEA_3'), (10, 4, 1, 'SPA_1'), (11, 4, 2, 'SPA_2'), (12, 4, 3, 'SPA_3'),
(13, 4, 4, 'SPA_4'), (14, 4, 5, 'SPA_5');

CREATE TABLE `IoTType` (
  `IoTTypeID` TINYINT UNSIGNED PRIMARY KEY,
  `type` VARCHAR(2) UNIQUE NOT NULL
);

INSERT INTO `IoTType`(`IoTTypeID`, `type`) VALUES
  (1, 'WA'), (2, 'DR'), (3, 'SW'), (4, 'PB');

CREATE TABLE `sendIoTDevices` (
  `sendIoTDevicesID` VARCHAR(8) PRIMARY KEY,
  `IP` VARCHAR(32) UNIQUE NOT NULL,
  `mac` VARCHAR(32) UNIQUE NOT NULL
);

CREATE TABLE `IoT` (
  `IoTID` VARCHAR(8) PRIMARY KEY,
  `sendIoTDevicesID` VARCHAR(32),
  `dormitoryPlaceID` TINYINT UNSIGNED,
  `No` TINYINT UNSIGNED NOT NULL,
  `IoTTypeID` TINYINT UNSIGNED NOT NULL,
  FOREIGN KEY (`sendIoTDevicesID`) REFERENCES `sendIoTDevices`(`sendIoTDevicesID`) ON UPDATE CASCADE,
  FOREIGN KEY (`dormitoryPlaceID`) REFERENCES `dormitoryPlace`(`dormitoryPlaceID`) ON UPDATE CASCADE,
  FOREIGN KEY (`IoTTypeID`) REFERENCES `IoTType`(`IoTTypeID`) ON UPDATE CASCADE
);

INSERT INTO `IoT`(`IoTID`, `dormitoryPlaceID`, `No`, `IoTTypeID`) VALUES
('PB_12', NULL, 1, 4), ('PB_34', NULL, 2, 4), ('PB_56', NULL, 3, 4),
('SW_21', 1, 1, 3), ('SW_22', 1, 2, 3), ('SW_31', 7, 1, 3), ('SW_32', 7, 2, 3),
('WA_211', 1, 1, 1), ('WA_212', 1, 2, 1), ('WA_221', 2, 1, 1), ('WA_222', 2, 2, 1),
('WA_223', 2, 3, 1), ('WA_231', 3, 1, 1), ('WA_232', 3, 2, 1), ('WA_233', 3, 3, 1),
('WA_311', 7, 1, 1), ('WA_312', 7, 2, 1), ('WA_313', 7, 3, 1), ('WA_314', 7, 4, 1),
('WA_321', 8, 1, 1), ('WA_322', 8, 2, 1), ('WA_323', 8, 3, 1), ('WA_324', 8, 4, 1),
('WA_331', 9, 1, 1), ('WA_332', 9, 2, 1), ('WA_333', 9, 3, 1), ('WA_334', 9, 4, 1),
('DR_211', 1, 1, 2), ('DR_212', 1, 2, 2), ('DR_221', 2, 1, 2), ('DR_222', 2, 2, 2),
('DR_223', 2, 3, 2), ('DR_231', 3, 1, 2), ('DR_232', 3, 2, 2), ('DR_233', 3, 3, 2),
('DR_311', 7, 1, 2), ('DR_312', 7, 2, 2), ('DR_313', 7, 3, 2), ('DR_314', 7, 4, 2),
('DR_321', 8, 1, 2), ('DR_322', 8, 2, 2), ('DR_323', 8, 3, 2), ('DR_324', 8, 4, 2),
('DR_331', 9, 1, 2), ('DR_332', 9, 2, 2), ('DR_333', 9, 3, 2), ('DR_334', 9, 4, 2);

CREATE TABLE `IoTData` (
  `IoTDataID` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `IoTID` VARCHAR(8) NOT NULL,
  `time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `dataStatus` TINYINT UNSIGNED NOT NULL,
  FOREIGN KEY (`IoTID`) REFERENCES `IoT`(`IoTID`) ON UPDATE CASCADE
);

CREATE TABLE `parsedIoTData` (
  `time` DATETIME CHECK ( MINUTE(`time`) % 5 = 0 ),
  `IoTID` VARCHAR(8),
  `value` FLOAT UNSIGNED NOT NULL,
  `sector` SMALLINT UNSIGNED NOT NULL DEFAULT (FLOOR((HOUR(`time`) * 60 + MINUTE(`time`)) / 5)),
  `week` TINYINT UNSIGNED NOT NULL DEFAULT (WEEKDAY(`time`)) CHECK ( `week` < 7 ),
  FOREIGN KEY (`IoTID`) REFERENCES `IoT`(`IoTID`) ON UPDATE CASCADE,
  PRIMARY KEY(`time`, `IoTID`)
);

CREATE VIEW `send_iot_info` AS (
  SELECT T2.sendIoTDevicesID AS sendIoTID, T2.IP AS sendIoTIP, T1.IoTID AS IoTID
  FROM `IoT` AS T1 INNER JOIN `sendIoTDevices` AS T2 ON T1.sendIoTDevicesID = T2.sendIoTDevicesID
);

CREATE VIEW `latest_dashboard` AS (
  SELECT T1.IoTID AS ID, T1.dataStatus AS stat, T4.place AS place, T3.No AS num, T1.time AS time
  FROM (
    `IoTData` AS T1
    INNER JOIN (
      SELECT ST1.IoTID AS IoTID, MAX(ST1.time) AS time
      FROM `IoTData` AS ST1
      GROUP BY ST1.IoTID
    ) AS T2 ON T1.IoTID = T2.IoTID AND T1.time = T2.time
    INNER JOIN `IoT` AS T3 ON T1.IoTID = T3.IoTID
    LEFT OUTER JOIN `dormitoryPlace` AS T4 ON T3.dormitoryPlaceID = T4.dormitoryPlaceID
  )
);

INSERT INTO `IoTData`(`IoTID`, `dataStatus`) SELECT T.IoTID, 1 FROM IoT AS T;
