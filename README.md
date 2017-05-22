# cartTrackerAPI

A small project just testing out the [falcon web framework](https://github.com/falconry/falcon).

## installing

First create a new virtualenv:

`virtualenv trackerapp`

and install the requirements.txt:

`pip install -r requirements.txt`

Note that I'm using celery, so you'll have to connect to a rabbitmq server (or some other celery broker) and run a celery worker in order to test. By default it's set to connect to a local rabbitmq server, but you can change that in the trackerapp.py file by modifying the setting:

`CELERY_APP = Celery('trackerapp', broker='pyamqp://guest@localhost')`

Once you've set your broker, don't forget to start your celery worker! You should do this in the directory containing trackerapp.py.

`celery -A trackerapp worker --loglevel=info`

Now you should be able to run the app with gunicorn:

`gunicorn -b 127.0.0.1:8888 trackerapp:APP`

If this works then the falcon app should be running on your localhost. To see if it's working, try going to http://localhost:8888/api/v1/item in a browser and you should see a '405 GET not allowed' message from falcon. This means things are working as expected

## An Example Request

If you have [httpie](https://github.com/jakubroztocil/httpie) you can try:

`http localhost:8888/api/v1/item external_id='some_id'`

or else with curl:

`curl -H "Content-Type: application/json" -X POST -d '{"external_id":"some_id"}' localhost:8888/api/v1/item`

## Running The Tests

I like colorized output so I use [pyrg](https://pypi.python.org/pypi/pyrg). Of course you could just run them with whatever python interpreter you have as well. If you're in the root directory of the app, you can run...

Unit Tests:

`pyrg unittests.py`

Integration Tests:

`pyrg integrationtests.py`
