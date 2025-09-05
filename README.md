# lottary-system

## Endpoints
### /ping [GET]
Just a ping to check if the service is up

### /registrations [GET]
Returns a json list of registrations currently stored in the database.

### /register [POST]
Add a new entry to the lottery with a json object with a name and email address.
```json
{
    "name":"Your Name", 
    "email":"your.email@example.com"
}
```
Example:
```curl -X POST -H "Content-Type: application/json" -d '{"name":"Your Name", "email":"your.email@example.com"}' http://127.0.0.1:5000/register```

On first launch of the app, you need to setup the database with this to make sure persistance between runs.
This only needs to be done once per environment.
```
docker run --rm -v lottery-data:/app lottery-app python setup_db.py
```

## Build and Run

To build the app to a docker container.
```docker build -t lottery-app .```
This will setup the container and initilise the database tables using the start.sh script.

Then run the following to start the container. The specification of volume (here `lottery-data` as example) gives the ability to pick database on launch. if multiple decides to be used. for example, dev, test or prod databases.
```docker run -p 5000:8000 -v lottery-data:/app lottery-app```

After that, you can reach the app on `127.0.0.1:5000`. and for quick test you can call `http://127.0.0.1:5000/ping` in the browser.
