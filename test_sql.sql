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

INSERT INTO `IoT_IP`(`IoTID`, `IoTIP`) VALUES
('PB_12', 'ip0'), ('PB_34', 'ip1'), ('PB_56', 'ip2'), ('SW_21', 'ip3'), ('SW_22', 'ip4'), ('SW_31', 'ip5'),
('SW_32', 'ip6'), ('WA_211', 'ip7'), ('WA_212', 'ip8'), ('WA_221', 'ip9'), ('WA_222', 'ip10'),
('WA_223', 'ip11'), ('WA_231', 'ip12'), ('WA_232', 'ip13'), ('WA_233', 'ip14'), ('WA_311', 'ip15'),
('WA_312', 'ip16'), ('WA_313', 'ip17'), ('WA_314', 'ip18'), ('WA_321', 'ip19'),
('WA_322', 'ip20'), ('WA_323', 'ip21'), ('WA_324', 'ip22'), ('WA_331', 'ip23'),
('WA_332', 'ip24'), ('WA_333', 'ip25'), ('WA_334', 'ip26'), ('DR_211', 'ip27'),
('DR_212', 'ip28'), ('DR_221', 'ip29'), ('DR_222', 'ip30'), ('DR_223', 'ip31'),
('DR_231', 'ip32'), ('DR_232', 'ip33'), ('DR_233', 'ip34'), ('DR_311', 'ip35'),
('DR_312', 'ip36'), ('DR_313', 'ip37'), ('DR_314', 'ip38'), ('DR_321', 'ip39'),
('DR_322', 'ip40'), ('DR_323', 'ip41'), ('DR_324', 'ip42'), ('DR_331', 'ip43'),
('DR_332', 'ip44'), ('DR_333', 'ip45'), ('DR_334', 'ip46');

/* test */
INSERT INTO `IoT_Data`(`IoTID`, `dataStatus`) VALUES
('PB_12', 0), ('PB_34', 0), ('PB_56', 0), ('SW_21', 0), ('SW_22', 0), ('SW_31', 0),
('SW_32', 0), ('WA_211', 0), ('WA_212', 0), ('WA_221', 0), ('WA_222', 0),
('WA_223', 0), ('WA_231', 0), ('WA_232', 0), ('WA_233', 0), ('WA_311', 0),
('WA_312', 0), ('WA_313', 0), ('WA_314', 0), ('WA_321', 0),
('WA_322', 0), ('WA_323', 0), ('WA_324', 0), ('WA_331', 0),
('WA_332', 0), ('WA_333', 0), ('WA_334', 0), ('DR_211', 0),
('DR_212', 0), ('DR_221', 0), ('DR_222', 0), ('DR_223', 0),
('DR_231', 0), ('DR_232', 0), ('DR_233', 0), ('DR_311', 0),
('DR_312', 0), ('DR_313', 0), ('DR_314', 0), ('DR_321', 0),
('DR_322', 0), ('DR_323', 0), ('DR_324', 0), ('DR_331', 0),
('DR_332', 0), ('DR_333', 0), ('DR_334', 0);

INSERT INTO `teacher`(`name`, `pass`) VALUES
('tt1', 'tt_pass1'), ('tt2', 'tt_pass2'), ('tt3', 'tt_pass3'), ('tt4', 'tt_pass4');

INSERT INTO `student`(`studentID`, `grade`, `courseID`, `name`) VALUES
  ('t1', 1, 1, 'n1'), ('t2', 1, 1, 'n2'), ('t3', 1, 1, 'n3'), ('t4', 1, 2, 'n4'), ('t5', 1, 2, 'n5'),
  ('t6', 1, 2, 'n6'), ('t7', 1, 3, 'n7'), ('t8', 1, 3, 'n8'), ('t9', 1, 3, 'n9'), ('t10', 1, 4, 'n10'),
  ('t11', 1, 4, 'n11'), ('t12', 1, 4, 'n12'), ('t13', 1, 5, 'n13'), ('t14', 1, 5, 'n14'), ('t15', 1, 5, 'n15'),
  ('t16', 2, 2, 'n16'), ('t17', 2, 2, 'n17'), ('t18', 2, 2, 'n18'), ('t19', 2, 3, 'n19'), ('t20', 2, 3, 'n20'),
  ('t21', 2, 3, 'n21'), ('t22', 2, 4, 'n22'), ('t23', 2, 4, 'n23'), ('t24', 2, 4, 'n24'), ('t25', 2, 5, 'n25'),
  ('t26', 2, 5, 'n26'), ('t27', 2, 5, 'n27'), ('t28', 3, 1, 'n28'), ('t29', 3, 1, 'n29'), ('t30', 3, 1, 'n30'),
  ('t31', 3, 2, 'n31'), ('t32', 3, 2, 'n32'), ('t33', 3, 2, 'n33'), ('t34', 3, 3, 'n34'), ('t35', 3, 3, 'n35'),
  ('t36', 3, 3, 'n36'), ('t37', 3, 4, 'n37'), ('t38', 3, 4, 'n38'), ('t39', 3, 4, 'n39'), ('t40', 3, 5, 'n40'),
  ('t41', 3, 5, 'n41'), ('t42', 3, 5, 'n42'), ('t43', 4, 1, 'n43'), ('t44', 4, 1, 'n44'), ('t45', 4, 1, 'n45'),
  ('t46', 4, 2, 'n46'), ('t47', 4, 2, 'n47'), ('t48', 4, 2, 'n48'), ('t49', 4, 3, 'n49'), ('t50', 4, 3, 'n50'),
  ('t51', 4, 3, 'n51'), ('t52', 4, 4, 'n52'), ('t53', 4, 4, 'n53'), ('t54', 4, 4, 'n54'), ('t55', 4, 5, 'n55'),
  ('t56', 4, 5, 'n56'), ('t57', 4, 5, 'n57'), ('t58', 5, 1, 'n58'), ('t59', 5, 1, 'n59'), ('t60', 5, 1, 'n60'),
  ('t61', 5, 2, 'n61'), ('t62', 5, 2, 'n62'), ('t63', 5, 2, 'n63'), ('t64', 5, 3, 'n64'), ('t65', 5, 3, 'n65'),
  ('t66', 5, 3, 'n66'), ('t67', 5, 4, 'n67'), ('t68', 5, 4, 'n68'), ('t69', 5, 4, 'n69'), ('t70', 5, 5, 'n70'),
  ('t71', 5, 5, 'n71'), ('t72', 5, 5, 'n72'), ('t73', 1, 6, 'n72'), ('t74', 1, 6, 'n73'), ('t75', 1, 6, 'n74'),
  ('t76', 1, 7, 'n75'), ('t77', 1, 7, 'n76'), ('t78', 1, 7, 'n77'), ('t79', 2, 6, 'n78'), ('t80', 2, 6, 'n79'),
  ('t81', 2, 6, 'n80'), ('t82', 2, 7, 'n81'), ('t83', 2, 7, 'n82'), ('t84', 2, 7, 'n83');

INSERT INTO `penalty`(`studentID`, `wcma`, `mcma`, `scma`) VALUES
('t1', 0, 0, 0), ('t2', 0, 0, 0), ('t3', 0, 0, 0), ('t4', 0, 0, 0), ('t5', 0, 0, 0), ('t6', 0, 0, 0), ('t7', 0, 0, 0), ('t8', 0, 0, 0), ('t9', 0, 0, 0), ('t10', 0, 0, 0),
('t11', 0, 0, 0), ('t12', 0, 0, 0), ('t13', 0, 0, 0), ('t14', 0, 0, 0), ('t15', 0, 0, 0), ('t16', 0, 0, 0), ('t17', 0, 0, 0), ('t18', 0, 0, 0), ('t19', 0, 0, 0), ('t20', 0, 0, 0),
('t21', 0, 0, 0), ('t22', 0, 0, 0), ('t23', 0, 0, 0), ('t24', 0, 0, 0), ('t25', 0, 0, 0), ('t26', 0, 0, 0), ('t27', 0, 0, 0), ('t28', 0, 0, 0), ('t29', 0, 0, 0), ('t30', 0, 0, 0),
('t31', 0, 0, 0), ('t32', 0, 0, 0), ('t33', 0, 0, 0), ('t34', 0, 0, 0), ('t35', 0, 0, 0), ('t36', 0, 0, 0), ('t37', 0, 0, 0), ('t38', 0, 0, 0), ('t39', 0, 0, 0), ('t40', 0, 0, 0),
('t41', 0, 0, 0), ('t42', 0, 0, 0), ('t43', 0, 0, 0), ('t44', 0, 0, 0), ('t45', 0, 0, 0), ('t46', 0, 0, 0), ('t47', 0, 0, 0), ('t48', 0, 0, 0), ('t49', 0, 0, 0), ('t50', 0, 0, 0),
('t51', 0, 0, 0), ('t52', 0, 0, 0), ('t53', 0, 0, 0), ('t54', 0, 0, 0), ('t55', 0, 0, 0), ('t56', 0, 0, 0), ('t57', 0, 0, 0), ('t58', 0, 0, 0), ('t59', 0, 0, 0), ('t60', 0, 0, 0),
('t61', 0, 0, 0), ('t62', 0, 0, 0), ('t63', 0, 0, 0), ('t64', 0, 0, 0), ('t65', 0, 0, 0), ('t66', 0, 0, 0), ('t67', 0, 0, 0), ('t68', 0, 0, 0), ('t69', 0, 0, 0), ('t70', 0, 0, 0),
('t71', 0, 0, 0), ('t72', 0, 0, 0), ('t73', 0, 0, 0), ('t74', 0, 0, 0), ('t75', 0, 0, 0), ('t76', 0, 0, 0), ('t77', 0, 0, 0), ('t78', 0, 0, 0), ('t79', 0, 0, 0), ('t80', 0, 0, 0),
('t81', 0, 0, 0), ('t82', 0, 0, 0), ('t83', 0, 0, 0), ('t84', 0, 0, 0);

INSERT INTO `dormitoryBelong`(`studentID`, `dormitoryPlaceID`, `studentStatusID`) VALUES
('t1', 1, 1), ('t2', 1, 1), ('t3', 1, 2), ('t4', 1, 1), ('t5', 1, 1), ('t6', 2, 1), ('t7', 2, 1), ('t8', 2, 1), ('t9', 2, 1), ('t10', 2, 1),
('t11', 3, 1), ('t12', 3, 1), ('t13', 3, 1), ('t14', 3, 1), ('t15', 3, 1), ('t16', 4, 1), ('t17', 4, 1), ('t18', 4, 2), ('t19', 4, 1), ('t20', 4, 1),
('t21', 5, 1), ('t22', 5, 1), ('t23', 5, 1), ('t24', 5, 1), ('t25', 5, 2), ('t26', 6, 1), ('t27', 6, 1), ('t28', 6, 1), ('t29', 6, 1), ('t30', 6, 1),
('t31', 7, 1), ('t32', 7, 1), ('t33', 7, 2), ('t34', 7, 1), ('t35', 7, 1), ('t36', 8, 1), ('t37', 8, 1), ('t38', 8, 1), ('t39', 8, 1), ('t40', 8, 1),
('t41', 9, 1), ('t42', 9, 2), ('t43', 9, 1), ('t44', 9, 1), ('t45', 9, 1), ('t46', 10, 1), ('t47', 10, 1), ('t48', 10, 1), ('t49', 10, 1), ('t50', 10, 1),
('t51', 11, 1), ('t52', 11, 1), ('t53', 11, 1), ('t54', 11, 1), ('t55', 11, 1), ('t56', 12, 1), ('t57', 12, 1), ('t58', 12, 2), ('t59', 12, 1), ('t60', 12, 1),
('t61', 13, 1), ('t62', 13, 1), ('t63', 13, 1), ('t64', 13, 1), ('t65', 13, 1), ('t66', 14, 1), ('t67', 14, 1), ('t68', 14, 1), ('t69', 14, 2), ('t70', 14, 1),
('t81', 1, 2), ('t82', 2, 1), ('t83', 3, 1), ('t84', 1, 1);

INSERT INTO `rollCall`(`dormitoryID`, `studentID`, `day`, `registeredStudentID`) VALUES
(1, 't1', '2023-01-01', 't1'), (1, 't2', '2023-01-02', 't1'), (1, 't3', '2023-01-03', 't1'), (1, 't4', '2023-01-04', 't2'), (1, 't5', '2023-01-05', 't1'),
(2, 't16', '2023-01-01', 't1'), (2, 't17', '2023-01-02', 't1'), (2, 't18', '2023-01-03', 't2'), (2, 't19', '2023-01-04', 't1'), (2, 't20', '2023-01-05', 't1'),
(3, 't31', '2023-01-01', 't1'), (3, 't32', '2023-01-02', 't1'), (3, 't33', '2023-01-03', 't2'), (3, 't34', '2023-01-04', 't1'), (3, 't35', '2023-01-05', 't1'),
(4, 't46', '2023-01-01', 't1'), (4, 't47', '2023-01-02', 't1'), (4, 't48', '2023-01-03', 't2'), (4, 't49', '2023-01-04', 't1'), (4, 't50', '2023-01-05', 't1');

INSERT INTO `cleaning`(`cleaningTypeID`, `place`, `year_month`, `day`, `times`) VALUES
(1, 'MOU_1', '2023-01', 1, 1), (1, 'MOU_2', '2023-01', 1, 1), (1, 'MOU_3', '2023-01', 1, 1), (1, 'CEN_1', '2023-01', 1, 1), (1, 'CEN_2', '2023-01', 1, 1),
(1, 'CEN_3', '2023-01', 1, 1), (1, 'SEA_1', '2023-01', 1, 1), (1, 'SEA_2', '2023-01', 1, 1), (1, 'SEA_3', '2023-01', 1, 1), (1, 'SPA_1', '2023-01', 1, 1),
(1, 'SPA_2', '2023-01', 1, 1), (1, 'SPA_3', '2023-01', 1, 1), (1, 'SPA_4', '2023-01', 1, 1), (1, 'SPA_5', '2023-01', 1, 1), (2, 'MOU_1', '2023-01', 1, 1),
(2, 'SPA_1', '2023-01', 2, 2), (1, 'MOU_1', '2023-01', 8, 2), (1, 'MOU_2', '2023-01', 8, 2), (1, 'MOU_3', '2023-01', 8, 2), (1, 'CEN_1', '2023-01', 8, 2),
(1, 'CEN_2', '2023-01', 8, 2), (1, 'CEN_3', '2023-01', 8, 2), (1, 'SEA_1', '2023-01', 8, 2), (1, 'SEA_2', '2023-01', 8, 2), (1, 'SEA_3', '2023-01', 8, 2),
(1, 'SPA_1', '2023-01', 8, 2);

INSERT INTO `cleaningDuty`(`studentID`, `cleaningID`, `registeredStudentID`) VALUES
('t1', 1, 't1'), ('t2', 1, 't1'), ('t3', 1, 't1'), ('t4', 2, 't2'), ('t5', 2, 't1'), ('t6', 3, 't2'), ('t7', 3, 't2'), ('t8', 4, 't1'), ('t9', 4, 't1'), ('t10', 4, 't2'),
('t11', 5, 't2'), ('t12', 5, 't1'), ('t13', 5, 't1'), ('t14', 6, 't2'), ('t15', 6, 't1'), ('t16', 6, 't1'), ('t17', 7, 't2'), ('t18', 7, 't1'), ('t19', 7, 't2'), ('t20', 8, 't1'),
('t21', 8, 't2'), ('t22', 8, 't1'), ('t23', 9, 't1'), ('t24', 9, 't1'), ('t25', 9, 't1'), ('t26', 10, 't4'), ('t27', 10, 't1'), ('t28', 11, 't1'), ('t29', 12, 't1'), ('t30', 12, 't1'),
('t31', 13, 't3'), ('t32', 14, 't1'), ('t33', 15, 't1'), ('t34', 16, 't1'), ('t35', 17, 't1'), ('t36', 18, 't1'), ('t37', 19, 't1'), ('t38', 20, 't3'), ('t39', 21, 't1'), ('t40', 22, 't1'),
('t41', 23, 't1'), ('t42', 24, 't1'), ('t43', 25, 't1'), ('t44', 26, 't1'), ('t45', 26, 't2');

