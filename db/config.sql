
/*user setting*/
CREATE USER 'only1'@'localhost' IDENTIFIED BY 'password1';
CREATE USER 'iot_inserter'@'localhost' IDENTIFIED BY 'password2';

GRANT SELECT ON `only1DB`.`latest_dashboard` TO 'only1'@'localhost';
GRANT SELECT ON `only1DB`.`dormitoryPlace` TO 'only1'@'localhost';
GRANT SELECT ON `only1DB`.`dormitory` TO 'only1'@'localhost';
GRANT SELECT ON `only1DB`.`IoTData` TO 'only1'@'localhost';
GRANT SELECT ON `only1DB`.`IoT` TO 'only1'@'localhost';

GRANT SELECT ON `only1DB`.`send_iot_info` 'iot_inserter'@'localhost';
GRANT INSERT ON `only1DB`.`IoTData` 'iot_inserter'@'localhost';

/*event setting*/
SET GLOBAL event_scheduler = ON;
CREATE EVENT IoT_Data_delete ON SCHEDULE EVERY 1 MONTH DO DELETE FROM `IoTData` AS T WHERE T.time < DATE_SUB(CURDATE(), INTERVAL 6 MONTH);

