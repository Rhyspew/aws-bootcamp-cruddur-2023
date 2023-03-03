# Week 2 — Distributed Tracing

### Update Gitpod Installations
This week I updated .gitpod.yml to include the npm install required to run the front end docker build. 

Add the following to the task section:
```yml
 - name: react-js
    command: |
      cd frontend-react-js
      npm i
```

In addition, create a step at the end of the file to make frontend and backend servers public automatically:
```yml
ports:
  - name: frontend
    port: 3000
    onOpen: open-browser
    visibility: public
  - name: backend
    port: 4567
    visibility: public
  - name: xray-daemon
    port: 2000
    visibility: public
```

Notice the inclusion of a port for xray which will be used later in this weeks tasks. 


## Honeycomb
Honeycomb allows users to monitor activity within an application to help the user monitor performance and pinpoint problems that arise. 
See [Honeycomb](https://www.honeycomb.io/) for more details. 

### Integrate Honeycomb into the app
Create a Honeycomb account. In the account create a new environment then take note of the api key. 

In the terminal export and save details of the api key to environment variables and repeat with and aws service name.  

```sh
export HONEYCOMB_API_KEY="APIKEY"
export HONEYCOMB_SERVICE_NAME="Cruddur"

gp env HONEYCOMB_API_KEY="APIKey"
gp env HONEYCOMB_SERVICE_NAME="Cruddur"
```
Check the variables have saved by entering the command: env | grep HONEY
The command should return the saved variables. 

In the backend-flask folder edit the requirements.txt folder. 
Add the following underneath the last entry;

```
opentelemetry-api
opentelemetry-sdk
opentelemetry-exporter-otlp-proto-http
opentelemetry-instrumentation-flask
opentelemetry-instrumentation-requests
```

Run the file to install tools: pip install -r requirements.txt

Update the docker-compose.yml file, add into the backend-flask environment variables pasge:

```yml
OTEL_SERVICE_NAME: 'backend-flask'
OTEL_EXPORTER_OTLP_ENDPOINT: "https://api.honeycomb.io"
OTEL_EXPORTER_OTLP_HEADERS: "x-honeycomb-team=${HONEYCOMB_API_KEY}"
``` 

In the app.py folder ensure the following code is entered, it will allow tracing for the honeycomb console:

```py
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
```

Then add in another block:
```py
provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter())
provider.add_span_processor(processor)

simple_processor = SimpleSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(simple_processor)

trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)
```

Then enter under 'app = Flask(_name_)'
```py
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()
```

Enter 'docker compose up' in console and start the containers. 
Copy the backend server link and follow in a new window or tab, add /api/activities/home to the end of it and enter in browser. Refresh a few times. 
Go to the honeycomb console and check the home page to confirm if data has been traced, a 404 code and a few 200 codes should have been saved if successful so far.

Update the backend file home_activities.js, entries to the beginning and end of the code. 
Enter after the first entry then incorporate the rest into the function, make sure the code is indented correctly. 

```py
from opentelemetry import trace

tracer = trace.get_tracer("home.activities")

class HomeActivities:
  def run():
    with tracer.start_as_current_span("home-activites-mock-data"):
      span = trace.get_current_span()
```

Add to the end of the code just before 'return results'

```py
span.set_attribute("app.result_length", len(results))
```
Repeat refresh of backend link with api/activities/home url. Check honeycomb for results. 

## X-Ray

In requirements.txt enter the following 'aws-xray-sdk' in the next line of the file. This will download the plugin for the Xray SDK. 

Install by entering ' pip install -r requirements.txt'

Create a json file in aws/json for the xray sampling rule. 

In backend-flask, edit the app.py file. 
Add in the following after the first block of honeycomb code

```py
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
```

Add in after the second block of honeycomb code:

```py
xray_url = os.getenv("AWS_XRAY_URL")
xray_recorder.configure(service='backend-flask', dynamic_naming=xray_url)
```

Add in after 'app = Flask(_name_)'
```py
XRayMiddleware(app, xray_recorder)
```

Entered the following command into the terminal and saw the json script returned. The returned json confirmed the group was created. 

```sh
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (Week2) $ aws xray create-group \
> --group-name "Cruddur" \
> --filter-expression "service(\"backend-flask\")"
{
    "Group": {
        "GroupName": "Cruddur",
        "GroupARN": "arn:aws:xray:us-east-1:926994502331:group/Cruddur/QYUAU6FLGUHYWGFEK2WYBZQ3ENJDWUUXRITGQSC6USUMMM2C7PMQ",
        "FilterExpression": "service(\"backend-flask\")",
        "InsightsConfiguration": {
            "InsightsEnabled": false,
            "NotificationsEnabled": false
        }
    }
}
```

Go to aws management console, find the cruddur group in cloudwatch>settings>traces>groups

Enter the following code to insert parameters using json file in aws>json 

```sh
gitpod /workspace/aws-bootcamp-cruddur-2023 (Week2) $ aws xray create-sampling-rule --cli-input-json file://aws/json/xray.json
{
    "SamplingRuleRecord": {
        "SamplingRule": {
            "RuleName": "Cruddur",
            "RuleARN": "arn:aws:xray:us-east-1:926994502331:sampling-rule/Cruddur",
            "ResourceARN": "*",
            "Priority": 9000,
            "FixedRate": 0.1,
            "ReservoirSize": 5,
            "ServiceName": "backend-flask",
            "ServiceType": "*",
            "Host": "*",
            "HTTPMethod": "*",
            "URLPath": "*",
            "Version": 1,
            "Attributes": {}
        },
        "CreatedAt": "2023-02-27T01:09:59+00:00",
        "ModifiedAt": "2023-02-27T01:09:59+00:00"
    }
}
```

Add xray daemon to dockercompose
Under backend-flask environment details enter:

```yml
AWS_XRAY_URL: "*4567-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}*"
AWS_XRAY_DAEMON_ADDRESS: "xray-daemon:2000"
```
Under services enter the following, ensure indentation is correct:

```yml
xray-daemon:
    image: "amazon/aws-xray-daemon"
    environment:
      AWS_ACCESS_KEY_ID: "${AWS_ACCESS_KEY_ID}"
      AWS_SECRET_ACCESS_KEY: "${AWS_SECRET_ACCESS_KEY}"
      AWS_REGION: "ca-central-1"
    command:
      - "xray -o -b xray-daemon:2000"
    ports:
      - 2000:2000/udp
```

In the terminal enter: docker compose up

Open the link to the backend server and  view logs on trace in xray console

Update user_activity.py file to test more logs, changed to script below:

```py
  def run(user_handle):
    # xray
    segment = xray_recorder.begin_segment('user_activities')

    model = {
      'errors': None,
      'data': None
    }

    now = datetime.now(timezone.utc).astimezone()
    
    if user_handle == None or len(user_handle) < 1:
      model['errors'] = ['blank_user_handle']
    else:
      now = datetime.now()
      results = [{
        'uuid': '248959df-3079-4947-b847-9e0892d1bab4',
        'handle':  'Bruce Banner',
        'message': 'Hulk Smash!!!',
        'created_at': (now - timedelta(days=1)).isoformat(),
        'expires_at': (now + timedelta(days=31)).isoformat()
      }]
      model['data'] = results

    # Xray
    subsegment = xray_recorder.begin_subsegment('mock-data')
    
    dict = {
      "now": now.isoformat(),
      "results-size": len(model['data'])
    }
    subsegment.put_metadata('key', dict, 'namespace')

    return model
```

Repeat steps to create logs via backend-flask url.

### Update to Xray tracing

Later in the week I followed the information on how to provide more data for xray tracing. 

In app.py the following lines were added to allow capture of specific logs. 

```py
@app.route("/api/activities/home", methods=['GET'])
@xray_recorder.capture('activities_home')
def data_home():
  data = HomeActivities.run()
  return data, 200

@app.route("/api/activities/notifications", methods=['GET'])
@xray_recorder.capture('activities_users')
def data_notifications():
  data = NotificationsActivities.run()
  return data, 200
  
@app.route("/api/activities/<string:activity_uuid>", methods=['GET'])
@xray_recorder.capture('activities_show')
def data_show_activity(activity_uuid):
  data = ShowActivity.run(activity_uuid=activity_uuid)
  return data, 200
```

Update user_activities.py to the following:

```py
from datetime import datetime, timedelta, timezone
from aws_xray_sdk.core import xray_recorder
class UserActivities:
  def run(user_handle):
    try:
      model = {
        'errors': None,
        'data': None
      }

      now = datetime.now(timezone.utc).astimezone()
        
      if user_handle == None or len(user_handle) < 1:
          model['errors'] = ['blank_user_handle']
      else:
        now = datetime.now()
        results = [{
          'uuid': '248959df-3079-4947-b847-9e0892d1bab4',
          'handle':  'Bruce Banner',
          'message': 'Hulk Smash!!!',
          'created_at': (now - timedelta(days=1)).isoformat(),
          'expires_at': (now + timedelta(days=31)).isoformat()
        }]
        model['data'] = results

      subsegment = xray_recorder.begin_subsegment('mock-data')
      # xray
      dict = {
        "now": now.isoformat(),
        "results-size": len(model['data'])
      }
      subsegment.put_metadata('key', dict, 'namespace')
      xray_recorder.end_subsegment()
    finally:
      # Close Segment   
      xray_recorder.end_subsegment()  
    return model
```

Log into frontend url and switch between a user page and the home page to see log traces on AWS Xray

## Cloudwatch

Add watchtower to requirements.txt

enter command in terminal: ping install -r requirements.txt

In app.py enter the following code after the entry for xray to import tools needed for logging with CloudWatch:

```py
import watchtower
import logging
from time import strftime

# Configuring Logger to Use CloudWatch
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()# cw_handler = watchtower.CloudWatchLogHandler(log_group='cruddur')
LOGGER.addHandler(console_handler)
LOGGER.addHandler(cw_handler)
LOGGER.info("test log")
```
Add the following after frontend, backend and origins env get requests:

```py
@app.after_request
def after_request(response):
    timestamp = strftime('[%Y-%b-%d %H:%M]')
    LOGGER.error('%s %s %s %s %s %s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, response.status)
    return response
```

Find the following endpoint description and update with (logger=LOGGER)

```py
@app.route("/api/activities/home", methods=['GET'])
def data_home():
  data = HomeActivities.run(logger=LOGGER)
  return data, 200
```


Update home_activities.py after function 'run()' :

```py
logger.info("HomeActivities")
```
Add 'logger' between parenthesis of run() function.

Complete by editing docker-comose.yml, add the followin env variables to the backend-flask environment list:

```yml
      AWS_DEFAULT_REGION: "${AWS_DEFAULT_REGION}"
      AWS_ACCESS_KEY_ID: "${AWS_ACCESS_KEY_ID}"
      AWS_SECRET_ACCESS_KEY: "${AWS_SECRET_ACCESS_KEY}"
```

Change all AWS service lines of code to inline comments using the '#' at the start of each line of code so that they arent run and wont incurr costs. 

## Rollbar

Use the [Rollbar](https://rollbar.com/) service for this task. Create an account and continue. 

From the Rollbar setup page copy the access key. 

In requirements.txt add in 'blinker' and 'rollbar' on seperate lines.

In the terminal change directory to backend-flask and run command 'pip install -r requirements.txt'

Enter the following commands into the terminal, input the access key between the quotation marks:

```sh
export ROLLBAR_ACCESS_TOKEN=""
gp env ROLLBAR_ACCESS_TOKEN=""
```

Confirm env var has saved by entering: env | grep ROLL

Enter 'ROLLBAR_ACCESS_TOKEN: "${ROLLBAR_ACCESS_TOKEN}" ' into the environment section. 

Go to app.py and input:

```py
import rollbar
import rollbar.contrib.flask
from flask import got_request_exception
```

Then input:

```py
rollbar_access_token = os.getenv('ROLLBAR_ACCESS_TOKEN')
@app.before_first_request
def init_rollbar():
    """init rollbar module"""
    rollbar.init(
        # access token
        rollbar_access_token,
        # environment name
        'production',
        # server root directory, makes tracebacks prettier
        root=os.path.dirname(os.path.realpath(__file__)),
        # flask already sets up logging
        allow_logging_basic_config=False)

    # send exceptions from `app` to rollbar, using flask's signal system.
    got_request_exception.connect(rollbar.contrib.flask.report_exception, app)
```

and the input for a test endpoint:
```py
@app.route('/rollbar/test')
def rollbar_test():
    rollbar.report_message('Hello World!', 'warning')
    return "Hello World!"
```
Next enter 'docker compose up' in the terminal and open a link from the backend server. Follow the link and enter /rollbar/test at the end of the url. 
Ensure the text 'Hello World' is seen in the browser window. 

Go to Rollbar. After a minute or so, the menu should update and the new logs will be displayed. If the Cruddur app is working correctly, code 200 will be logged. To display a fault code I deleted two letters from 'return' at the bottom of the user_activities.py file. This caused an error which was picked up in Rollbar. 


