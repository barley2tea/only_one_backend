INSERT INTO `sendIoTDevices`(`sendIoTDevicesID`, `IP`, `mac`) VALUES
('WD_000', '127.0.0.1', '00:00:00:00'), ('WD_311', '172.17.127.8', 'E8:9F:6D:08:98:26');

UPDATE `IoT` set `sendIoTDevicesID` = 'WD_000';
UPDATE `IoT` set `sendIoTDevicesID` = 'WD_311' WHERE `IoTID` LIKE 'DR_31%';
UPDATE `IoT` set `sendIoTDevicesID` = 'WD_311' WHERE `IoTID` LIKE 'WA_31%';

