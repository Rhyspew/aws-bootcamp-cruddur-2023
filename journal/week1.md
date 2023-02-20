# Week 1 — App Containerization


## Creating the App - Backend and Frontend Containers

As a pre-requisite to the task I had to download and install the docker extension to GitPod.
This can be done by searching for docker in the GitPod extension icon on the left and entering docker in the search bar on the new window. 


### Backend 

I created a Dockerfile within the backend-flask folder. The file contains the code:

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

I created a new file called Dockerfile in the frontend-react-js folder.

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

I have amended some details in the home_activities file in the services directory so that some comments appear in the home page.
