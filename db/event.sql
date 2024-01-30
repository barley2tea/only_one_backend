SET GLOBAL event_scheduler = ON;

CREATE EVENT `cleaning_rollCall_delete` ON SCHEDULE EVERY 1 MONTH DO DELETE `cleaing` AS T1, `rollCall` AS T2, `IoT_Data` AS T3 FROM T1 INNER JOIN T2 ON T1.registeredTime = T2.registeredTime INNER JOIN T3 ON T1.registeredTime = T3.time WHERE (T1.registeredTime < DATE_SUB(CURDATE(), INTERVAL 6 MONTH));
