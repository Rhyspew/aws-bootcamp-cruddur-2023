# Week 1 — App Containerization


## Creating the App - Backend and Frontend Containers

As a pre-requisite to the task I had to download and install the docker extension to GitPod.
This can be done by searching for docker in the GitPod extension icon on the left and entering docker in the search bar on the new window. 


### Backend 

I created a [Dockerfile](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/backend-flask/Dockerfile) within the backend-flask folder. The file contains the code:

```dockerfile
FROM python:3.10-slim-buster

WORKDIR /backend-flask

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENV FLASK_ENV=development

EXPOSE ${PORT}
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=4567"]
```

The following code will build the container:

```sh
docker build -t  backend-flask ./backend-flask
```

The next line of code, will run the container:
```sh
docker run --rm -p 4567:4567 -it -e FRONTEND_URL='*' -e BACKEND_URL='*' backend-flask
```

The container will run. Switch to the ports tab and see port 4567, click on the lock to make the link public. Copy the link into a browser, add /api/activities/home to the link and a JSON script should be visible. Refresh the page a few times. Back in the GitPod terminal there should be a string of 404 codes appearing, one for every page refresh. 

The following code will run the container in the background. The container will be isolated if the front end is also run, meaning they will have no communication and the app will not function correctly. 

```sh
docker container run --rm -p 4567:4567 -d backend-flask
```


### Frontend

I created a new file called [Dockerfile](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/frontend-react-js/Dockerfile) in the frontend-react-js folder.

```dockerfile
FROM node:16.18

ENV PORT=3000

COPY . /frontend-react-js
WORKDIR /frontend-react-js
RUN npm install
EXPOSE ${PORT}
CMD ["npm", "start"]
```

Before this can be built NPM install must be carried out. Build requires a copy of the node modules downloaded in NPM install. 

```sh
cd frontend-react-js
npm i
```

After the NPM install completes, build the container using the following:

```
docker build -t frontend-react-js ./frontend-react-js
```

Run the container by entering the following:

```
docker run -p 3000:3000 -d frontend-react-js
```

The container will run up but isolated from the back end. Check the result by unlocking port 3000 under the ports tab, copy the link and follow in the browser. 


### Docker Compose
In the root directory aws-bootcamp-cruddur-2023 create a file called docker-compose.yml containing the following:
```yml
version: "3.8"
services:
  backend-flask:
    environment:
      FRONTEND_URL: "https://3000-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}"
      BACKEND_URL: "https://4567-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}"
    build: ./backend-flask
    ports:
      - "4567:4567"
    volumes:
      - ./backend-flask:/backend-flask
  frontend-react-js:
    environment:
      REACT_APP_BACKEND_URL: "https://4567-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}"
    build: ./frontend-react-js
    ports:
      - "3000:3000"
    volumes:
      - ./frontend-react-js:/frontend-react-js

# the name flag is a hack to change the default prepend folder
# name when outputting the image names
networks: 
  internal-network:
    driver: bridge
    name: cruddur
```

This will be used to "compose" the containers, which means it will build and run the referenced containers and apply all env data contianed. 
For this to run, NPM must be installed. 

When this is run both containers are linked which allow data to be transferred. Make sure both 3000 and 4567 ports have been made public by 'unlocking' them. 

I have amended some details in the home_activities file in the services directory so that alternative comments appear in the home page.

![HomePage](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/HomePage.png)

## OpenAI and Notification Page additions to Frontend and Backend

### Backend

I updated the [Open-api-3.0.yml](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/backend-flask/openapi-3.0.yml) file in the backend-flask folder to contain an endpoint for the notifications page. 
I used [Open-API Specification](https://swagger.io/specification/) to learn how to implement this feature. 

Added lines 151 - 165
```yml
 /api/activities/notifications:
    get:
      description: 'Return a feed of activity for all of those that I follow'
      tags:
        - activities
      parameters: []
      responses:
        '200':
          description: Returns an array of activities
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Activity'
``` 

In the [app.py]((https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/backend-flask/app.py) file, the following was added as a route to  notifications. 

Added in line 7

```py
from services.notifications_activities import *
```

Added in lines 69 - 72

```py
@app.route("/api/activities/notifications", methods=['GET'])
def data_notifications():
  data = NotificationsActivities.run()
  return data, 200
```

The file [notifications_activities.py](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/backend-flask/services/notifications_activities.py) was created as an endpoint for notfication information. 

```py
from datetime import datetime, timedelta, timezone
class NotificationsActivities:
  def run():
    now = datetime.now(timezone.utc).astimezone()
    results = [{
      'uuid': '68f126b0-1ceb-4a33-88be-d90fa7109eee',
      'handle':  'Bruce Wayne',
      'message': 'I am Batman',
      'created_at': (now - timedelta(days=2)).isoformat(),
      'expires_at': (now + timedelta(days=5)).isoformat(),
      'likes_count': 5,
      'replies_count': 1,
      'reposts_count': 0,
      'replies': [{
        'uuid': '26e12864-1c26-5c3a-9658-97a10f8fea67',
        'reply_to_activity_uuid': '68f126b0-1ceb-4a33-88be-d90fa7109eee',
        'handle':  'Barry Allen',
        'message': 'I am the fastest man alive',
        'likes_count': 0,
        'replies_count': 0,
        'reposts_count': 0,
        'created_at': (now - timedelta(days=2)).isoformat()
      }],
    }
    ]
    return results
```


### Frontend

The file [app.js](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/frontend-react-js/src/App.js) was updated to include a route to the notifications page. 

Added to line 4

```js
import NotificationsFeedPage from './pages/NotificationsFeedPage';
```
Added to lines 23 - 26

```js
 {
    path: "/notifications",
    element: <NotificationsFeedPage />
  },
  ```

[NotificationsFeedPage.js](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/frontend-react-js/src/pages/NotificationsFeedPage.js) and [NotificationsFeedPage.css](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/frontend-react-js/src/pages/NotificationsFeedPage.css) created to create a frontend page for notifications within the Cruddur app. I used the HomeFeedPage.js as a template for the notifcations feed page and changed line 1

```js
import './NotificationsFeedPage.css';
```
Notifications page of app shown below. 

![NotificationsPage](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/NotificationPage.png)

## Running and Testing DynamoDB and Postgres containers 

Update to .gitpod.yml to install postgres extension on GitPod startup. 

Lines 11 - 16

```yml
 - name: postgres
    init: |
      curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc|sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg
      echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" |sudo tee  /etc/apt/sources.list.d/pgdg.list
      sudo apt update
      sudo apt install -y postgresql-client-13 libpq-dev
```

Line 20

```yml
 - cweijan.vscode-postgresql-client2
```

Create .gitignore file

```sh
docker/**/*
```

Update to docker-compose.yml that includes build of DynamoDB and Postgre databases

Lines 39 - 71

```yml
dynamodb-local:
    # https://stackoverflow.com/questions/67533058/persist-local-dynamodb-data-in-volumes-lack-permission-unable-to-open-databa
    # We needed to add user:root to get this working.
    user: root
    command: "-jar DynamoDBLocal.jar -sharedDb -dbPath ./data"
    image: "amazon/dynamodb-local:latest"
    container_name: dynamodb-local
    ports:
      - "8000:8000"
    volumes:
      - "./docker/dynamodb:/home/dynamodblocal/data"
    working_dir: /home/dynamodblocal
  db:
    image: postgres:13-alpine
    restart: always
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - '5432:5432'
    volumes: 
      - db:/var/lib/postgresql/data

# the name flag is a hack to change the default prepend folder
# name when outputting the image names
networks: 
  internal-network:
    driver: bridge
    name: cruddur

volumes:
  db:
    driver: local
```    

Once update to docker-compose.yml was complete, I ran docker compose up. When build was complete I changed all ports to public. 


#### Testing DynamoDB local. 

Create a table. If successful a JSON script will be returned in the terminal with details of the DynamoDB table.

```sh
aws dynamodb create-table \
    --endpoint-url http://localhost:8000 \
    --table-name Music \
    --attribute-definitions \
        AttributeName=Artist,AttributeType=S \
        AttributeName=SongTitle,AttributeType=S \
    --key-schema AttributeName=Artist,KeyType=HASH AttributeName=SongTitle,KeyType=RANGE \
    --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1 \
    --table-class STANDARD
```

![DynamoDB](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/DynamoDBTableCreate.png)


Create an item in the table. A JSON will return on completion displaying item details.

```sh
aws dynamodb put-item \
    --endpoint-url http://localhost:8000 \
    --table-name Music \
    --item \
        '{"Artist": {"S": "No One You Know"}, "SongTitle": {"S": "Call Me Today"}, "AlbumTitle": {"S": "Somewhat Famous"}}' \
    --return-consumed-capacity TOTAL  
```  

![ItemInput](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/DynamoDBItemInput.png)


Check table by calling DynamoDB lists. 

```sh
aws dynamodb list-tables --endpoint-url http://localhost:8000
```

![ListTable](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/DynamoDBListTable.png)


#### Testing Postgres DB

In GitPod go to database menu, add a new DB connection. 

Enter details and password for postgres DB.

![Postgres setup](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/PostgresSetup.png)


Enter in terminal

```sh
psql -Upostgres --host localhost
```


Enter password used in connection setup.

enter \l to see Postgre DB list.

![postgresTest](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/PostgresTest.png)
