CREATE TABLE `dormitory` (
  `dormitoryID` TINYINT UNSIGNED PRIMARY KEY,
  `dormitory` VARCHAR(4) UNIQUE NOT NULL
);

INSERT INTO `dormitory`(`dormitoryID`, `dormitory`) VALUES
  (1, 'MOU'), (2, 'CEN'), (3, 'SEA'), (4, 'SPA');

CREATE TABLE `courses` (
  `courseID` TINYINT UNSIGNED PRIMARY KEY,
  `course` VARCHAR(2) UNIQUE NOT NULL
);

INSERT INTO `courses`(`courseID`, `course`) VALUES
  (1, 'M'), (2, 'E'), (3, 'I'), (4, 'A'), (5, 'C'), (6, 'EM'), (7, 'AC');

CREATE TABLE `studentStatus` (
   `studentStatusID` TINYINT UNSIGNED PRIMARY KEY,
   `studentStatus` VARCHAR(8) UNIQUE NOT NULL
);

INSERT INTO `studentStatus`(`studentStatusID`, `studentStatus`) VALUES
(1, 'exist'), (2, 'stop'), (3, 'retire');

CREATE TABLE `cleaningType` (
  `cleaningTypeID` TINYINT UNSIGNED PRIMARY KEY,
  `cleaningType` VARCHAR(8) UNIQUE NOT NULL
);

INSERT INTO `cleaningType`(`cleaningTypeID`, `cleaningType`) VALUES
(1, 'weekly'), (2, 'monthly'), (3, 'special');

CREATE TABLE `cleaningStatus` (
  `cleaningStatusID` TINYINT UNSIGNED PRIMARY KEY,
  `cleaningStatus` VARCHAR(16) UNIQUE NOT NULL
);

INSERT INTO `cleaningStatus`(`cleaningStatusID`, `cleaningStatus`) VALUES
(1, 'attend'), (2, 'absence'), (3, 'substitute'), (4, 'unconfirmed');

CREATE TABLE `teacher` (
  `teacherID` INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  `name` VARCHAR(128) NOT NULL UNIQUE,
  `pass` VARCHAR(256) NOT NULL
);

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

CREATE TABLE `student` (
  `studentID` VARCHAR(8) PRIMARY KEY,
  `grade` TINYINT UNSIGNED NOT NULL,
  `courseID` TINYINT UNSIGNED NOT NULL,
  `name` VARCHAR(128) NOT NULL,
  `pass` VARCHAR(256),
  `access` BOOLEAN NOT NULL DEFAULT 0,
  FOREIGN KEY (`courseID`) REFERENCES `courses`(`courseID`) ON UPDATE CASCADE,
  UNIQUE (`grade`, `courseID`, `name`)
);

CREATE TABLE `penalty` (
  `studentID` VARCHAR(8) PRIMARY KEY,
  `wcma` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  `mcma` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  `scma` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  FOREIGN KEY (`studentID`) REFERENCES `student`(`studentID`) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE `dormitoryBelong` (
  `studentID` VARCHAR(8) PRIMARY KEY,
  `dormitoryPlaceID` TINYINT UNSIGNED,
  `studentStatusID` TINYINT UNSIGNED DEFAULT 1,
  FOREIGN KEY (`studentID`) REFERENCES `student`(`studentID`) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (`studentStatusID`) REFERENCES `studentStatus`(`studentStatusID`) ON UPDATE CASCADE
);

CREATE TABLE `rollCall` (
  `rollCallID` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `dormitoryID` TINYINT UNSIGNED NOT NULL,
  `studentID` VARCHAR(8) NOT NULL,
  `day` DATE NOT NULL,
  `registeredStudentID` VARCHAR(8) NOT NULL,
  `registeredTime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE(`dormitoryID`, `day`, `studentID`),
  FOREIGN KEY (`dormitoryID`) REFERENCES `dormitory`(`dormitoryID`) ON UPDATE CASCADE,
  FOREIGN KEY (`studentID`) REFERENCES `student`(`studentID`) ON UPDATE CASCADE,
  FOREIGN KEY (`registeredStudentID`) REFERENCES `student`(`studentID`) ON UPDATE CASCADE
);

CREATE TABLE `cleaning` (
  `cleaningID` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `cleaningTypeID` TINYINT UNSIGNED NOT NULL,
  `place` VARCHAR(128) NOT NULL,
  `year_month` VARCHAR(8) NOT NULL CHECK(`year_month` REGEXP '^[0-9]{4}-[012][0-9]$'),
  `day` TINYINT UNSIGNED NOT NULL CHECK(`day` <= 31),
  `times` TINYINT UNSIGNED NOT NULL,
  `status` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  `_monthly` VARCHAR(8) GENERATED ALWAYS AS (
    CASE
      WHEN(`cleaningTypeID` = 2) THEN `year_month`
      ELSE NULL
    END
  ) VIRTUAL,
  UNIQUE(`cleaningTypeID`, `place`, `year_month`, `times`),
  UNIQUE(`_monthly`, `day`),
  UNIQUE(`_monthly`, `times`),
  FOREIGN KEY (`cleaningTypeID`) REFERENCES `cleaningType`(`cleaningTypeID`) ON UPDATE CASCADE
);

CREATE TABLE `cleaningDuty` (
  `cleaningDutyID` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `studentID` VARCHAR(8) NOT NULL,
  `cleaningID` BIGINT UNSIGNED NOT NULL,
  `cleaningStatusID` TINYINT UNSIGNED NOT NULL DEFAULT 4,
  `registeredStudentID` VARCHAR(8) NOT NULL,
  `registeredTime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE(`studentID`, `cleaningID`),
  FOREIGN KEY (`cleaningStatusID`) REFERENCES `cleaningStatus`(`cleaningStatusID`) ON UPDATE CASCADE,
  FOREIGN KEY (`cleaningID`) REFERENCES `cleaning`(`cleaningID`) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (`studentID`) REFERENCES `student`(`studentID`) ON UPDATE CASCADE,
  FOREIGN KEY (`registeredStudentID`) REFERENCES `student`(`studentID`) ON UPDATE CASCADE
);

CREATE TABLE `cleaningDutyAgent` (
  `cleaningDutyID` BIGINT UNSIGNED PRIMARY KEY,
  `studentID` VARCHAR(8) NOT NULL,
  FOREIGN KEY (`cleaningDutyID`) REFERENCES `cleaningDuty`(`cleaningDutyID`) ON UPDATE CASCADE,
  FOREIGN KEY (`studentID`) REFERENCES `student`(`studentID`) ON UPDATE CASCADE
);

CREATE TABLE `studentReport` (
  `cleaningID` BIGINT UNSIGNED PRIMARY KEY,
  `studentID` VARCHAR(8) NOT NULL,
  `report` JSON NOT NULL,
  `reportedTime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`studentID`) REFERENCES `student`(`studentID`) ON UPDATE CASCADE,
  FOREIGN KEY (`cleaningID`) REFERENCES `cleaning`(`cleaningID`) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE `teacherReport` (
  `cleaningID` BIGINT UNSIGNED PRIMARY KEY,
  `teacherID` INT UNSIGNED NOT NULL,
  `report` JSON NOT NULL,
  `reportedTime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`cleaningID`) REFERENCES `studentReport`(`cleaningID`) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (`teacherID`) REFERENCES `teacher`(`teacherID`) ON UPDATE CASCADE
);

CREATE TABLE `IoT_IP` (
  `IoTID` VARCHAR(8) PRIMARY KEY,
  `IoTIP` VARCHAR(32) UNIQUE NOT NULL
);

CREATE TABLE `IoT_Data` (
  `IoTID` VARCHAR(8),
  `time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `dataStatus` TINYINT UNSIGNED NOT NULL,
  PRIMARY KEY(`IoTID`, `time`),
  FOREIGN KEY (`IoTID`) REFERENCES `IoT_IP`(`IoTID`) ON UPDATE CASCADE
);
