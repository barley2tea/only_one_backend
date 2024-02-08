# only one backend
## Overviw
This is flask project.

## Set up
1. Install and setup python, pip and mysql in your pc.
2. Install the package written in the `requirements.txt`.
  - e.g. :`$ pip install -r requirements.txt`
3. Add database to mysql.
  - `test.sql` contains dummy data for testing
  - e.g. :`$ mysql -u <username> -p<password> -h <host> <databasename> < <product.sql or test.sql>`
4. Create a `.env` file and set the following environment variables

| variable | explanation |
| --- | --- |
| DB\_CONFIG\_JSON | Path of json file with `user`, `host`, `database` and `password` elements that connects to mysql by default |
| SWITCHBOT\_CONFIG\_JSON | Path of switchbot configuration json file |
| FLASK\_CONFIGURATION | Configuration class name of flask. Choose from `application/config.py` |
| FRONTEND\_URL | URL of frontend |
| MODEL\_PATH | Path of YOLO's weight for image recognition |
| APP\_LOG\_LEVEL | Log level of app\_logger |
| WERKZEUG\_LOG\_LEVEL | Log level of werkzeug\_logger |
| BOT\_LOG\_LEVEL | Log level of bot\_logger |

## Getting Started
Run `python main.py` or use uwsgi
