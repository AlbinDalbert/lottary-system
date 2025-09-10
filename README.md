# lottery-system

## Overview

A backend application for running a monthly lottary. It has been built using Flask and SQlite using Docker as a deployment environment. 

## Endpoints
### [GET] /ping 
Just a ping to check if the service is up.

### [GET] /registrations
Returns a json list of registrations currently stored in the database.

### [GET] /winners
Returns a list of the previous winners.

### [GET] /logs
Returns a json list of the logs ordered by time. This endpoint also supports pageination.
accept the query parameters `?page=<number>` and `?per_page=<number>` to control the output. Use `?per_page=0` to retrieve all records.

### [POST] /register
Add a new entry to the lottery with a json object with a name and email address.
```json
{
    "name":"Your Name", 
    "email":"your.email@example.com"
}
```
Example:
```
curl -X POST -H "Content-Type: application/json" -d '{"name":"Your Name", "email":"your.email@example.com"}' http://127.0.0.1:5000/register
```

## Build and Run
*(these instructions are aimed for an linux environment)*

**Prerequisite:** 
 - Python 3.12+
 - pip 
 - Docker

Clone the repository and enter the directory.
```
git clone https://github.com/AlbinDalbert/lottery-system.git
cd loggery-system
```

Create a virtual environment and intall the dependencies.
```
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

To build the app to a docker container.
```docker build -t lottery-app .```
This will setup the container and initilise the database tables using the start.sh script.

Then run the following to start the container. The specification of volume (here `lottery-data` as example) gives the ability to pick database on launch. if multiple decides to be used. for example, dev, test or prod databases.
```docker run -d -p 5000:8000 -v lottery-data:/data lottery-app```
The `-v`flag is used to specefy a persistent volume to make sure we don't loose data when the container stops.

After that, you can reach the app on `127.0.0.1:5000`. and for quick test you can call `http://127.0.0.1:5000/ping` in the browser.

The monthly winner selection would be executed by a scheduled job that is setup in the deployed environment (e.g. cron). And to select a winner it would run the following.
```
docker run --rm -v lottery-data:/data lottery-app python scheduler.py
```
Replace the container name and database mountpoint to the relevent names.

## CI/CD
The project uses GutHub Acrions workflow defined in `.github/workflows/` for continous integration and packaging. 

The pipeline is trigger on pushes to main and has three main jobs. 1. run tests, 2. build test, 3. package the application. All jobs require the previous job to have passed to even start.

### Tests 
It first runs the test specefied in `test_app.py` which focuses on getting a broad test scope that test the expected usages of the application with a focus on resulting behavious and error handling with malformated registrations.

### Docker Build
The second job tests the integration and dockerization, which builds the docker container and makes a request to all endpoints to catch intergration problems like database mount point problems and similar.

### Packaging
This last job packages the applicaiton to a .tar file that can be executed with docker in the given environment. This job could be adapted to the needs of the deployment envirnment, but as no such environment exist here, packaging a .tar is deamed sufficiant.

## Decisions
The main technological decision in this project was about data storage. And here it was decided that an SQLite database was the most fitting option as it provides the ergonomics of SQL and SQL tooling if expansions are being made in the future. 
The central role timestamps play in how the different data is accessed makes SQL fitting. 
Also, the data itself ha a very rigid framwork and is easy to fit in with tables and possible entries doesn't have any need for dynamic number of attributes/columns.

Email validation was added to make sure the email at least syntactical possible for an email, the DNS validation was removed to allow for testing entries (e.g. exampl.com would be an invalid email domain other wise).

An imporvment for the endpoints that can be emplemented is better handling of pageination and similar other filtering attributes to imporve the ergonomics, but it was out of the scope of this project to imporves these ergonomics of these endpoints. Though `/logs`felt necessery as it grows the fastest of them all.
