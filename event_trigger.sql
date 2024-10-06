-- 一度のクエリごとに処理が増える
DELIMITER //
CREATE TRIGGER ins_parsed AFTER INSERT ON IoTData
FOR EACH ROW
BEGIN
  DECLARE last_time DATETIME;
  DECLARE last_value TINYINT;
  DECLARE separator_time DATETIME;

  SELECT T1.time, T1.dataStatus
  INTO last_time, last_value
  FROM (
    SELECT
      T.time,
      T.dataStatus,
      ROW_NUMBER() OVER (ORDER BY time DESC) AS rn
    FROM IoTData AS T
    WHERE T.IoTID = NEW.IoTID) AS T1
  WHERE T1.rn = 2;

  IF last_time IS NULL THEN
    LEAVE;
  END IF;


  SET separator_time = DATE_FORMAT(DATE_SUB(NEW.time, INTERVAL MINUTE(NEW.time) % 5 MINUTE), '%Y-%m-%d %H:%i:00');

  
  DECLARE stime DATETIME DEFAULT last_time;
  DECLARE etime DATETIME DEFAULT separator_time;
  DECLARE sept DATETIME DEFAULT separator_time;
  IF last_time < separator_time THEN
    SET sept = DATE_SUB(separator_time, INTERVAL 5 MINUTE)
  ELSE
    SET stime = separator_time;
    SET etime = DATE_ADD(separator_time, INTERVAL 5 MINUTE)
  END IF;

  WHILE NEW.time < etime DO
    INSERT INTO parsedIoTData(`time`, `value`, `sector`, `IoTID`)
      VALUES(
        sept,
        CONVERT(last_value, FLOAT) * TIME_TO_SEC(TIMEDIFF(etime, stime)) / 300,
        FLOOR((HOUR(sept) * 60 + MINUTE(sept)) / 5),
        NEW.IoTID
      ) AS col ON DUPLICATE KEY UPDATE value = value + col.value;
    SET stime = etime;
    SET etime = DATE_ADD(etime, INTERVAL 5 MINUTE);
    SET sept = stime;
  END WHILE;
  INSERT INTO parsedIoTData(`time`, `value`, `sector`, `IoTID`)
    VALUES(
      sept,
      CONVERT(last_value, FLOAT) * TIME_TO_SEC(TIMEDIFF(NEW.time, stime) / 300,
      FLOOR((HOUR(sept) * 60 + MINUTE(sept)) / 5),
      NEW.IoTID
    ) AS col ON DUPLICATE KEY UPDATE value = value + col.value;

END
//
DELIMITER ;
