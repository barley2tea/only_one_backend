
GRANT all ON [db_name].rollCall TO [user_name];
GRANT all ON [db_name].cleaning TO [user_name];
GRANT all ON [db_name].cleaningDuty TO [user_name];
GRANT all ON [db_name].cleaningDutyAgent TO [user_name];
GRANT all ON [db_name].studentReport TO [user_name];
GRANT all ON [db_name].teacherReport TO [user_name];
GRANT SELECT ON [db_name].* TO [user_name];
GRANT INSERT ON [db_name].IoT_Data TO [user_name];
GRANT UPDATE (pass, studentStatusID, wcma, mcma, scma) ON [db_name].student TO [user_name];
