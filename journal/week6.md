# Week 6 — Deploying Containers

This week I created ECS containers with Fargate. 
Fargate is an AWS native service that allows server less orchestration of containers hosted on AWS. 

I also used Route 53 as my DNS service to associate my domain name rpldev.co.uk with the app and created a secure link using Amazon Certificate Manager. This was all linked via an application load balancer and secured with security groups. 

Moved all bin files to root folder, change references in files to reflect new file locations. Ensure permissions of all files are executable so that they can be used during set up. [bin/](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/tree/main/bin)

Create new folders for backend and frontend and add files within to help automate commands such as to build and push containers to ECR/local. 

Create [erb](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/tree/main/erb) folder 
Create files for backend and frontend environments using ruby. 
Create files in backend and frontend to generate local environments named generate-env. 
Edit [Docker compose](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/docker-compose.yml) so that new environment cruddur-net can be launched, remove env variable list.   

Create a new file in bin/db/test
```py
#!/usr/bin/env python3

import psycopg
import os
import sys

connection_url = os.getenv("CONNECTION_URL")

conn = None
try:
  print('attempting connection')
  conn = psycopg.connect(connection_url)
  print("Connection successful!")
except psycopg.Error as e:
  print("Unable to connect to the database:", e)
finally:
  conn.close()
```

Review postgres in gitpod.yml for mistakes
line 19 'rds-' to /rds/update-sg-rule

Add to app.py above route to rollbar. Comment out roller
```py
@app.route('/api/health-check')
def health_check():
  return {'success': True}, 200
```
Execute test

Create new folder and file backend-flask/bin/health-check
```py
#!/usr/bin/env python3

import urllib.request

try:
  response = urllib.request.urlopen('http://localhost:4567/api/health-check')
  if response.getcode() == 200:
    print("[OK] Flask server is running")
    exit(0) # success
  else:
    print("[BAD] Flask server is not running")
    exit(1) # false
# This for some reason is not capturing the error....
#except ConnectionRefusedError as e:
# so we'll just catch on all even though this is a bad practice
except Exception as e:
  print(e)
  exit(1) # false
```

Execute health-check.

Create a CloudWatch Log Group (cruddur) via the CLI
Enter:
```sh
aws logs create-log-group --log-group-name "cruddur"

aws logs put-retention-policy --log-group-name "cruddur" --retention-in-days 1
```

Create ECS cluster with code:
```sh
aws ecs create-cluster --cluster-name cruddur --service-connect-defaults namespace=cruddur
```

See return results in terminal

Create ECR repo.
```sh
aws ecr create-repository \
  --repository-name cruddur-python \
  --image-tag-mutability MUTABLE
```

See return results

Log into ECR
```sh
aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com"
```

Set URL and test with echo command
```sh
export ECR_PYTHON_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/cruddur-python"
echo $ECR_PYTHON_URL
```

Pull the docker python image, Tag and push image to ECR. Enter the following commands separately
```sh
docker pull python:3.10-slim-buster
docker tag python:3.10-slim-buster $ECR_PYTHON_URL:3.10-slim-buster
docker push $ECR_PYTHON_URL:3.10-slim-buster
```

![PythonECR](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/Week6-7/ECR-Pull-Image-Console.png)

Go to ECR console to confirm upload. Copy endpoint address.
Go to Dockerfile and replace slim buster with ecr endpoint
Test with docker compose up in gitpod terminal
See current images stored in docker using command: docker images

Repeat for backend-flask and frontend-react-js containers, enter separately

```sh
#Backend

aws ecr create-repository \
  --repository-name backend-flask \
  --image-tag-mutability MUTABLE

#SET URL
export ECR_BACKEND_FLASK_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/backend-flask"
echo $ECR_BACKEND_FLASK_URL

#Build Image - Make sure directory is backend-flask
docker build -t backend-flask .

#Tag Image
docker tag backend-flask:latest $ECR_BACKEND_FLASK_URL:latest

#Push Image
docker push $ECR_BACKEND_FLASK_URL:latest
```
Check ECR to see if repo has been updated

Create a new folder/file aws/task-definitions/backend-flask.json

Create new policy for container role in aws/policies/service-execution-policy.json

Create service-execution-policy.json 

Create service-assume-role-execution-policy.json

```json
{
  "Version":"2012-10-17",
  "Statement":[{
      "Action":["sts:AssumeRole"],
      "Effect":"Allow",
      "Principal":{
        "Service":["ecs-tasks.amazonaws.com"]
    }}]
}
```

Make Cruddur execution role

```sh
aws iam create-role \
    --role-name CruddurServiceExecutionRole \
    --assume-role-policy-document "{
  \"Version\":\"2012-10-17\",
  \"Statement\":[{
    \"Action\":[\"sts:AssumeRole\"],
    \"Effect\":\"Allow\",
    \"Principal\":{
      \"Service\":[\"ecs-tasks.amazonaws.com\"]
    }
  }]
}"
```

Create parameters
```sh
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/AWS_ACCESS_KEY_ID" --value $AWS_ACCESS_KEY_ID
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/AWS_SECRET_ACCESS_KEY" --value $AWS_SECRET_ACCESS_KEY
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/CONNECTION_URL" --value $PROD_CONNECTION_URL
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/ROLLBAR_ACCESS_TOKEN" --value $ROLLBAR_ACCESS_TOKEN
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/OTEL_EXPORTER_OTLP_HEADERS" --value "x-honeycomb-team=$HONEYCOMB_API_KEY"
```

Check in system manager > parameter store to see if parameters have been uploaded.

```sh
aws iam put-role-policy --policy-name CruddurServiceExecutionPolicy --role-name CruddurServiceExecutionRole --policy-document file://aws/policies/service-execution-policy.json
"
```

Attach policy to role:
```sh
aws iam attach-role-policy --policy-arn POLICY_ARN --role-name CruddurServiceExecutionRole
```
Create role in console if necessary

Create Task role
```sh
aws iam create-role \
    --role-name CruddurTaskRole \
    --assume-role-policy-document "{
  \"Version\":\"2012-10-17\",
  \"Statement\":[{
    \"Action\":[\"sts:AssumeRole\"],
    \"Effect\":\"Allow\",
    \"Principal\":{
      \"Service\":[\"ecs-tasks.amazonaws.com\"]
    }
  }]
}"

aws iam put-role-policy \
  --policy-name SSMAccessPolicy \
  --role-name CruddurTaskRole \
  --policy-document "{
  \"Version\":\"2012-10-17\",
  \"Statement\":[{
    \"Action\":[
      \"ssmmessages:CreateControlChannel\",
      \"ssmmessages:CreateDataChannel\",
      \"ssmmessages:OpenControlChannel\",
      \"ssmmessages:OpenDataChannel\"
    ],
    \"Effect\":\"Allow\",
    \"Resource\":\"*\"
  }]
}
"

aws iam attach-role-policy --policy-arn arn:aws:iam::aws:policy/CloudWatchFullAccess --role-name CruddurTaskRole
aws iam attach-role-policy --policy-arn arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess --role-name CruddurTaskRole
```

Create new folder aws/task-definitions/
Create files:
backend-flask.json
frontend-react.json


Upload task to ECR
```sh
aws ecs register-task-definition --cli-input-json file://aws/task-definitions/backend-flask.json
```


Find VPC details via CLI:
```sh
export DEFAULT_VPC_ID=$(aws ec2 describe-vpcs \
--filters "Name=isDefault, Values=true" \
--query "Vpcs[0].VpcId" \
--output text)
echo $DEFAULT_VPC_ID
```

Find Subnet details - Not necessary:
```sh
export DEFAULT_SUBNET_IDS=$(aws ec2 describe-subnets  \
 --filters Name=vpc-id,Values=$DEFAULT_VPC_ID \
 --query 'Subnets[*].SubnetId' \
 --output json | jq -r 'join(",")')
echo $DEFAULT_SUBNET_IDS
```

Create SG
```sh
export CRUD_SERVICE_SG=$(aws ec2 create-security-group \
  --group-name "crud-srv-sg" \
  --description "Security group for Cruddur services on ECS" \
  --vpc-id $DEFAULT_VPC_ID \
  --query "GroupId" --output text)
echo $CRUD_SERVICE_SG
```

Set inbound rules:

```sh
aws ec2 authorize-security-group-ingress \
  --group-id $CRUD_SERVICE_SG \
  --protocol tcp \
  --port 4567 \
  --cidr 0.0.0.0/0
```

To see SGID if needed:
```sh
export CRUD_SERVICE_SG=$(aws ec2 describe-security-groups \
  --filters Name=group-name,Values=crud-srv-sg \
  --query 'SecurityGroups[*].GroupId' \
  --output text)
```

Create a service in the cruddur cluster in the aws management console.

Edit cruddurexecutionpolicy
Create a policy for ecr,  need:
'ecr: get authorisation token' 
'batch get image'
'batch check layer availability'
'get download url for layer'
Cloudwatch logs:
'logs: create log stream'
'logs: put log events'
Put resource as *
Add cloudwatch full access user policy to role
Update role with updated policy.
Save.

Return to ECS and check see if service tasks are completing

Install 'session-manager-plugin' in terminal. 

Downloaded session-manager for unbuntu
```sh
curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_64bit/session-manager-plugin.deb" -o "session-manager-plugin.deb"

sudo dpkg -i session-manager-plugin.deb
```

Enter 'session-manager-plugin' to see if install was successful.

Add service-backend-flask.json to aws/json folder

Execute following command to create a new service in ECS cruddur cluster.
aws ecs create-service --cli-input-json file://aws/json/service-backend-flask.json

Execute command to connect to service:
aws ecs execute-command  \
--region $AWS_DEFAULT_REGION \
--cluster cruddur \
--task 4a16446f97e34d2e86d26ab4d351ee5d \
--container backend-flask \
--command "/bin/bash" \
--interactive

Add updates to gitpod.yml line 28
```yml
  - name: fargate
    before: |
      curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_64bit/session-manager-plugin.deb" -o "session-manager-plugin.deb"    
      sudo dpkg -i session-manager-plugin.deb
      cd backend-flask
```

Change security group rules to allow access, port 4567. 
Connect to ecs task via browser and public ip, find in task network bindings tab
change default SG to include ingress from new sg with postgre ports.
Enter the port number after a colon to connect :4567

Test health of task by using public ip, port number and url /api/health-check

Make sure RDS DB is running and enter ./bin/db/test in terminal to test connection. 

Run docker compose up and send table to rds prod DB to get app to respond


Create a new load Balancer
Choose ALB
Name cruddur-alb


Create new SG for alb 
Name cruddur-alb-sg
rules for ingress - http and https from IPv4 anywhere.
Subnets - 3 defaults

Edit crud-srv-sg:
ingress rule - Custom TCP 4567 from cruddur-alb

Create a target group
Name: cruddur-backend-flask-tg
http port 4567
Health check to /api/health-check
Healthy threshold - 3
Leave others in default 
Complete

Link to load balancer

Create a listener with the a new TG
Name: cruddur-frontend-react-js
Port 3000
complete

Link to Alb as listener and complete

Add load balancer to service-backend-flask.json in aws folder line 7.

```json
    "loadBalancers": [
      {
        "targetGroupArn": "arn:aws:elasticloadbalancing:us-east-1:926994502331:targetgroup/cruddur-backend-flask-tg/b9f87326a65d0f5c",
        "containerName": "backend-flask",
        "containerPort": "4567"
      }
    ],
```

Start a new service if one is not running already

Create s3 bucket to store alb access logs
Name: cruddur-alb-access-logs34
unblock public access. 
block access through ACLs
Acknowledge risk
complete

Update bucket permissions to allow feed from ALB logs - use this [AWS Whitepaper](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/enable-access-logging.html#attach-bucket-policy)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::region-code:root"
      },
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::cruddur-alb-access-logs34/AWSLogs/accountID/*"
    }
  ]
}
```

Back in alb menu set monitoring on for access logs and set s3 uri to:
s3://cruddur-alb-access-logs

Next create scripts to run frontend containers
Create frontend-react-js.json

Create Dockerfile.prod in frontend folder
Create nginx.conf file in frontend
Update RecoverPage.js
Update ConfirmationPage.js

Enter 'npm run build' to test frontend build

Build should complete with warnings. 

Next create repo, ensure environment is logged into ecr
```sh
aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com"
```

Create frontend repo
```sh
aws ecr create-repository \
  --repository-name frontend-react-js \
  --image-tag-mutability MUTABLE
```

Set URL
```sh
export ECR_FRONTEND_REACT_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/frontend-react-js"
gp env ECR_FRONTEND_REACT_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/frontend-react-js"
echo $ECR_FRONTEND_REACT_URL
```

Create file in aws/json called service-frontend-react-js.json 

add load balancer info to service-frontend-react-js.json

```json
    "loadBalancers": [
      {
        "targetGroupArn": "arn:aws:elasticloadbalancing:us-east-1:926994502331:targetgroup/cruddur-frontend-react-js/5b3898c07562271a",
        "containerName": "frontend-react-js",
        "containerPort": "3000"
      }
    ],
```

Build Container - cd into frontend. 
```sh
docker build \
--build-arg REACT_APP_BACKEND_URL="http://cruddur-alb-312433817.us-east-1.elb.amazonaws.com" \
--build-arg REACT_APP_AWS_PROJECT_REGION="$AWS_DEFAULT_REGION" \
--build-arg REACT_APP_AWS_COGNITO_REGION="$AWS_DEFAULT_REGION" \
--build-arg REACT_APP_AWS_USER_POOLS_ID="us-east-1_sWiVpP341" \
--build-arg REACT_APP_CLIENT_ID="7q17rcrmc5qrq558n4ogm69hha" \
-t frontend-react-js \
-f Dockerfile.prod \
.
```

Push docker tags to repo
```sh
docker tag frontend-react-js:latest $ECR_FRONTEND_REACT_URL:latest
docker push $ECR_FRONTEND_REACT_URL:latest
```

Register task definition - cd into root
```sh
aws ecs register-task-definition --cli-input-json file://aws/task-definitions/frontend-react-js.json
```

Create a service for frontend
```sh
aws ecs create-service --cli-input-json file://aws/json/service-frontend-react-js.json
```

Adjust crud-src-sg rules to accept input from alb sg

Use the following command to connect to frontend and troubleshoot. Build container locally if troubleshooting proves difficult using aws containers. 
```sh
aws ecs execute-command  \
--region $AWS_DEFAULT_REGION \
--cluster cruddur \
--task <TaskID> \
--container frontend-react-js \
--command "/bin/sh" \
--interactive
```

If all is correct the frontend container should be healthy and connection is available from the alb dns name with port 3000 attached. 

![CrudHome](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/Week6-7/CruddurHomePage%20ViaALB%20.png)

The next step is to create a hosted zone - I used the name 'rpldev.co.uk' from ionos.
Copy the ns values from R53 into the name servers in Ionos and wait for them to upload.
Go to certificate manager and request a public certificate to the domain names:
rpldev.co.uk
*.rpldev.co.uk
Leave other settings as default and complete.
Enter the certificate page, go to the domain names and create a record for them both
Wait till the record has successfully been deployed.

Go to load balancer page. 
Add a new listener rule - Listen on port 80 and redirect to 443 HTTPS
Create another listener rule - listen on HTTPS 443 the forward to cruddur frontend target group - Add the certificate with correct domain name

Edit the listener rules for HTTPS:443 - Add an IF rule for the Host header to be value api.rpldev.co.uk. THEN rule forwards to backend. 
Remove the other listeners. 

Go back to R53 hosted zones and create a new record:
A record
Alias 
Application Load Balancer 
Select region
Select load balancer name
Simple routing

Repeat task with api as subdomain

When complete, if containers and rds is running, ping to https://api.rpldev.co.uk to confirm connectivity to app. Alternatively use curl command to https://api.rpldev.co.uk/api/health-check

Change values of frontend and backend in environment section of backend task definition to http://rpldev.co.uk and http://api.rpldev.co.uk respectively. 

Run new backend task definition to update with command;
aws ecs register-task-definition --cli-input-json file://aws/task-definitions/backend-flask.json

Build new app with updated url using build bash script in bin/frontend
Tag and push the image via bin/backend/push

For further testing limit the alb sg for access only to my ip in source box

Update backend Dockerfile
Update line:
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=4567", "--debug"]

Remove 
ENV FLASK_DEBUG=1

Make a new Dockerfile.prod With the following:
```sh
FROM 926994502331.dkr.ecr.us-east-1.amazonaws.com/cruddur-python:3.10-slim-buster

WORKDIR /backend-flask

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE ${PORT}

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=4567", "--no-debug","--no-debugger", "--no-reload"]
```

To build docker file: docker build -f Dockerfile.prod -t backend-flask.prod .

### Fix other problems. 
Populate RDS prod db with new users. Use ./bin/db/connect prod
Use INSERT command to insert new info into schema

If duplicate inserts have been made, delete using the following command:
DELETE FROM users where uuid = '<UUID>';

Update db/seed file. Run seed bash script (or setup)

Load ddb schema file if necessary to allow messaging.  

To get rid of a value return error go to backend-flask/lib/db.py
Change line 82 to:
return "{}"

Fix Cognito Auth Error
Update the auth descriptions to allow token refresh in app. 
Update the following as done in this [commit](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/commit/ba788230ea2aec7ce5305bb9f54113d688a6bf90)
  

### Testing

Log into ECR. 
Build backend and Frontend containers using bash scripts then run push scripts after builds are complete.  
Make sure RDS is running, connect to the table to confirm a schema and seed data are loaded. 
Make sure dynamodb has a table loaded.
Start the backend and frontend services.
Connect to the frontend by entering the saved domain name.
Play around with the app, enter activities or messages. Any returns following a post will confirm the backend is functioning. 
  

Finsihed app should look similar to the following images:
  
![Cruddur](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/Week6-7/Screenshot%202023-04-26%20at%2020.30.21.png)
  
![Messages](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/Week6-7/Screenshot%202023-04-26%20at%2020.30.45.png)
  
  
