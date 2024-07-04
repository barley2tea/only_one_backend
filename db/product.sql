DROP DATABASE testDB;
CREATE DATABASE testDB;
USE testDB;

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
  FOREIGN KEY (`sendIoTDevicesID`) REFERENCES `sendIoTDevices`(`sendIoTDevicesID`) ON UPDATE CASCADE,
  FOREIGN KEY (`dormitoryPlaceID`) REFERENCES `dormitoryPlace`(`dormitoryPlaceID`) ON UPDATE CASCADE
);

INSERT INTO `IoT`(`IoTID`, `dormitoryPlaceID`, `No`) VALUES
('PB_12', NULL, 1), ('PB_34', NULL, 2), ('PB_56', NULL, 3), ('SW_21', 1, 1), ('SW_22', 1, 2), ('SW_31', 7, 1),
('SW_32', 7, 2), ('WA_211', 1, 1), ('WA_212', 1, 2), ('WA_221', 2, 1), ('WA_222', 2, 1),
('WA_223', 2, 3), ('WA_231', 3, 1), ('WA_232', 3, 2), ('WA_233', 3, 3), ('WA_311', 7, 1),
('WA_312', 7, 2), ('WA_313', 7, 3), ('WA_314', 7, 4), ('WA_321', 8, 1),
('WA_322', 8, 2), ('WA_323', 8, 3), ('WA_324', 8, 4), ('WA_331', 9, 1),
('WA_332', 9, 2), ('WA_333', 9, 3), ('WA_334', 9, 4), ('DR_211', 1, 1),
('DR_212', 1, 2), ('DR_221', 2, 1), ('DR_222', 2, 2), ('DR_223', 2, 3),
('DR_231', 3, 1), ('DR_232', 3, 2), ('DR_233', 3, 3), ('DR_311', 7, 1),
('DR_312', 7, 2), ('DR_313', 7, 3), ('DR_314', 7, 4), ('DR_321', 8, 1),
('DR_322', 8, 2), ('DR_323', 8, 3), ('DR_324', 8, 4), ('DR_331', 9, 1),
('DR_332', 9, 2), ('DR_333', 9, 3), ('DR_334', 9, 4);

CREATE TABLE `IoTData` (
  `IoTDataID` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `IoTID` VARCHAR(8) NOT NULL,
  `time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `dataStatus` TINYINT UNSIGNED NOT NULL,
  FOREIGN KEY (`IoTID`) REFERENCES `IoT`(`IoTID`) ON UPDATE CASCADE
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
    ) AS T2 ON T1.IoTID = T2.IoTID
    INNER JOIN `IoT` AS T3 ON T1.IoTID = T3.IoTID
    LEFT OUTER JOIN `dormitoryPlace` AS T4 ON T3.dormitoryPlaceID = T4.dormitoryPlaceID
  )
);

INSERT INTO `IoTData`(`IoTID`, `dataStatus`) SELECT T.IoTID, 1 FROM IoT AS T;
