# only one backend
## Overviw
This is flask project.

## Set up
1. Install and setup python, pip and mysql in your pc.
2. Install the package written in the `requirements.txt`.
  - e.g. :`$ pip install -r requirements.txt`
3. Add database to mysql.
  - e.g. :`$ mysql -u <username> -p<password> -h <host> <databasename> < <product.sql>`
4. Create a `.env` file and set the following environment variables

| variable | explanation |
| --- | --- |
| DB\_CONFIG\_JSON | Path to a JSON file containing user information that references tables |
| DB\_IOT\_INSERTER | Path to a JSON file that contains user information to insert data into the IoTData table |
| FLASK\_CONFIGURATION | Configuration class name of flask. Choose from `application/config.py` |
| FRONTEND\_URL | URL of frontend |
| MODEL\_PATH | Path of YOLO's weight for image recognition |
| SAVE\_IMAGE | A True/False flag that determines whether to save the image with the image recognition data and the plotted results. Defaults to False. |
| APP\_LOG\_LEVEL | Log level of app\_logger. Defaults to info |
| WERKZEUG\_LOG\_LEVEL | Log level of werkzeug\_logger. Defaults to info |
| BOT\_LOG\_LEVEL | Log level of bot\_logger. Defaults to info |

## Getting Started
1. Start mysql server.
2. Run `python main.py` or use uwsgi

## Data analysis function.
  By actively starting the program, it is possible to analyze the data up to the previous day that exists in the IoTData table. Specifically, it calculates the average status for each IoTID over a 5-minute period.
You can start the program by following the steps below:
0. Start mysql server.
1. Install the package written in the `event_requirements.txt`.
2. Run `python event.py` to run the program.

