# Week 4 — Postgres and RDS

This week I created a Postgres database using Amazon RDS.  

Create an RDS database using CLI - This will be the production DB for the project. 
More information regarding RDS can be read here - [RDS](https://aws.amazon.com/rds/)

Enter in the GitPod session terminal

```sh
aws rds create-db-instance \
  --db-instance-identifier cruddur-db-instance \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version  14.6 \
  --master-username cruddurroot \
  --master-user-password Str0ngPassC0de \
  --allocated-storage 20 \
  --availability-zone us-east-1a \
  --backup-retention-period 0 \
  --port 5432 \
  --no-multi-az \
  --db-name cruddur \
  --storage-type gp2 \
  --publicly-accessible \
  --storage-encrypted \
  --enable-performance-insights \
  --performance-insights-retention-period 7 \
  --no-deletion-protection
```

![TableCreateCLI](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/DBCreateCLI.png)

Go to the AWS RDS console and verify DB has launched, wait for it to start up.

![RDSCREATED](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/RDSCreatedAWS.png)

During time in task where we dont need to leave the RDS instance running so stop it if needed:
Enter the DB instance menu.
Click on Actions
Stop Temporarily
Check the acknowledge DB instance will restart automatically after 7 days. 
Stop Temporarily

Go to the Gitpod environment and Docker compose up, ensure the PSQL DB is running using the Docker Tool

Enter the postgres terminal

enter the following:

```sh
psql -Upostgres --host localhost
```

enter the password: password

type ' \l ' to list current DBs

Type: 
```sql
create database cruddur;
```

The terminal will return 'CREATE DATABASE'
Check DB creation using \l command

![DBCreate](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/psqlCreatedlocal.png)

In the backend-flask folder create a new folder named 'db'
Within 'db' create a file named 'schema.sql'
Add the the following to 'schema.sql':

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

Run the schema.sql file from the backend-flask folder:
```sh
psql cruddur < db/schema.sql -h localhost -U postgres
```
The command will return 'CREATE EXTENSION' 

To avoid password inputs following every command, enter the user details in this format:
postgresql://[user[:password]@][netloc][:port][/dbname][?param1=value1&...]
Enter the following into the terminal:

```sh
psql postgresql://postgres:password@localhost:5432/cruddur
```

Exit the postgres terminal using \q.

Save the psql credentials in env variables to prevent re-entering details after every system reset.

```sh
export CONNECTION_URL="postgresql://postgres:password@localhost:5432/cruddur"
gp env CONNECTION_URL="postgresql://postgres:password@localhost:5432/cruddur"
```

enter env | grep to confirm variable is saved. 

To test try and connect to the DB server by entering in the terminal:

```sql
psql $CONNECTION_URL
```

If successful the terminal will return the psql version and a new user prompt 'cruddur=#' can be seen.

Before continuing create env variables for production password:

```sh
export PROD_CONNECTION_URL="postgresql://cruddurroot:Str0ngPassC0de@cruddur-db-instance.chna6c4lqqxk.us-east-1.rds.amazonaws.com:5432/cruddur"
gp env PROD_CONNECTION_URL="postgresql://cruddurroot:Str0ngPassC0de@cruddur-db-instance.chna6c4lqqxk.us-east-1.rds.amazonaws.com:5432/cruddur"
```

Now create a new folder within backend-flask titled 'bin'.
Add the files:
db-drop
db-create
db-schema-load

The files are going to be bash scripts with the following first line input :
```sh
#! /usr/bin/bash
```

After creating the file change permissions so that the file can be executed by entering :
```sh
chmod u+x [filepath]
```

To execute the file enter './[filepath]'

db-drop:

```sh
#! /usr/bin/bash

echo "db-drop"

NO_DB_CONNECTION_URL=$(sed 's/\/cruddur//g' <<<"$CONNECTION_URL")
psql $NO_DB_CONNECTION_URL -c "drop database cruddur;"
```

Execute the script in the terminal to test. It should return 'DROP DATABASE'

![Drop](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/db-drop.png)

Create db-create:

```sh
#! /usr/bin/bash

echo "db-create"
NO_DB_CONNECTION_URL=$(sed 's/\/cruddur//g' <<<"$CONNECTION_URL")
psql $NO_DB_CONNECTION_URL -c "create database cruddur;"
```
 
Execute the script in the terminal to test. It should return 'CREATE DATABASE'

![DBCreate](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/db-create.png)

Create db-schema-load
```sh
#! /usr/bin/bash

echo "db-schema-load"

schema_path="$(realpath .)/db/schema.sql"
echo $schema_path

if [ "$1" = "prod" ]; then
  echo "Running in production mode"
  URL=$PROD_CONNECTION_URL
else
  URL=$CONNECTION_URL
fi

psql $URL cruddur < $schema_path
```

Execute the file, it should return 'CREATE EXTENSION'

![SchemaLoad](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/db-schema-load.png)

If you wish to add colour to the script enter the following at the beginning of the script:
```sh
CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-schema-load"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"
```

Add to schema.sql, the complete script will look like:

```sql	
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
DROP TABLE IF EXISTS public.users;
DROP TABLE IF EXISTS public.activities;

CREATE TABLE public.users (
  uuid UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  display_name text,
  handle text,
  cognito_user_id text,
  created_at TIMESTAMP default current_timestamp NOT NULL
);

CREATE TABLE public.activities (
  uuid UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_uuid UUID,
  message text NOT NULL,
  replies_count integer DEFAULT 0,
  reposts_count integer DEFAULT 0,
  likes_count integer DEFAULT 0,
  reply_to_activity_uuid integer,
  expires_at TIMESTAMP,
  created_at TIMESTAMP default current_timestamp NOT NULL
);
```

Move on to schema configuration.
Enter the following in the terminal:

```sh
psql cruddur < db/schema.sql -h localhost -U postgres
```
The terminal will return 'CREATE EXTENSION'.

Create db-connect to connect to the db server:
```sh
#! /usr/bin/bash

echo db-connect

if [ "$1" = "prod" ]; then
  echo "Running in production mode"
  URL=$PROD_CONNECTION_URL
else
  URL=$CONNECTION_URL
fi

psql $URL
```

Change permissions and run the script. 

![Connect](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/db-connect.png)

Enter \dt to view newly created tables. 

![Tables](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/TableCreated.png)

Create bash script db-seed:
```sh
#! /usr/bin/bash

echo "db-seed"

seed_path="$(realpath .)/db/seed.sql"
echo $seed_path

if [ "$1" = "prod" ]; then
  echo "Running in production mode"
  URL=$PROD_CONNECTION_URL
else
  URL=$CONNECTION_URL
fi

psql $URL cruddur < $seed_path
```

Change permissions of bash script. 

Create seed.sql in db folder:

```sql
INSERT INTO public.users (display_name, handle, cognito_user_id)
VALUES
  ('Andrew Brown', 'andrewbrown' ,'MOCK'),
  ('Andrew Bayko', 'bayko' ,'MOCK');

INSERT INTO public.activities (user_uuid, message, expires_at)
VALUES
  (
    (SELECT uuid from public.users WHERE users.handle = 'andrewbrown' LIMIT 1),
    'This was imported as seed data!',
    current_timestamp + interval '10 day'
  )
```

Run db-seed to confirm it works. 
It will return INSERT 0 2 and INSERT 0 1

Check tables by entering cruddur tables and enter \dt when prompted
Enter \x on when in sql to expand view of tables if they seem to be incorrectly formatted. 

![Seed](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/db-seed.png)

Create db-sessions script in bin:
```sh
#! /usr/bin/bash

echo "db-sessions"

if [ "$1" = "prod" ]; then
  echo "Running in production mode"
  URL=$PROD_CONNECTION_URL
else
  URL=$CONNECTION_URL
fi

NO_DB_URL=$(sed 's/\/cruddur//g' <<<"$URL")
psql $NO_DB_URL -c "select pid as process_id, \
       usename as user,  \
       datname as db, \
       client_addr, \
       application_name as app,\
       state \
from pg_stat_activity;"
```

Make file executeable - chmod u+x

Make bash script db-setup:

```sh
#! /usr/bin/bash
-e # stop if it fails at any point

echo "db-setup"

bin_path="$(realpath .)/bin"

source "$bin_path/db-drop"
source "$bin_path/db-create"
source "$bin_path/db-schema-load"
source "$bin_path/db-seed"
```
Change permissions - chmod u+x

![Setup](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/db-setup.png)

### Download PSQL Drivers

In requirements.txt:
psycopg[binary]
psycopg[pool]

Enter in terminal: pip install -r requirements.txt

Add details to docker-compose.yml backend-flask environment with :
```yml
CONNECTION_URL: "postgresql://postgres:password@db:5432/cruddur"
```

Add to HomeActivities.py line 4:
```py
from lib.db import pool, query_wrap_object, query_wrap_array
```

From line 8 onwards, delete all code and enter in place:
```py
class HomeActivities:
  def run(cognito_user_id=None):
    #logger.info("HomeActivities")
    #with tracer.start_as_current_span("home-activites-mock-data"):
    #  span = trace.get_current_span()
    #  now = datetime.now(timezone.utc).astimezone()
    #  span.set_attribute("app.now", now.isoformat())

    sql = query_wrap_array("""
      SELECT
        activities.uuid,
        users.display_name,
        users.handle,
        activities.message,
        activities.replies_count,
        activities.reposts_count,
        activities.likes_count,
        activities.reply_to_activity_uuid,
        activities.expires_at,
        activities.created_at
      FROM public.activities
      LEFT JOIN public.users ON users.uuid = activities.user_uuid
      ORDER BY activities.created_at DESC
      """)
    print(sql)
    with pool.connection() as conn:
      with conn.cursor() as cur:
        cur.execute(sql)
        # this will return a tuple
        # the first field being the data
        json = cur.fetchone()
    return json[0]
    return results
```

Create a file - name it db.py:
```py
from psycopg_pool import ConnectionPool
import os

def query_wrap_object(template):
  sql = f"""
  (SELECT COALESCE(row_to_json(object_row),'{{}}'::json) FROM (
  {template}
  ) object_row);
  """
  return sql

def query_wrap_array(template):
  sql = f"""
  (SELECT COALESCE(array_to_json(array_agg(row_to_json(array_row))),'[]'::json) FROM (
  {template}
  ) array_row);
  """
  return sql

connection_url = os.getenv("CONNECTION_URL")
pool = ConnectionPool(connection_url)
```

Test by running db-seed and docker compose up. See the cruddur homepage for the following image. 

![CruddurSeed](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/PostToCruddur.png) 

Ensure PROD CONNECTION details are saved to be able to connect the RDS instance to the Gitpod environment

## Update security groups for RDS DB 

Add in user IP as source to the DB port 5432. 

Go to AWS Management console, go to RDS instance and view security groups. Edit inbound rules.
Create a rule that has Type = PostgreSQL and source = Anywhere 0.0.0.0/0. Give a description.

Use command to find GitPod user address - curl ifconfig.me in a Variable and export it:

```sh
export GITPOD_IP=$(curl ifconfig.me)
```

This will work until the Gitpod workspace is closed.

Create the script to update the SG rules. Make sure DBs are offline
Enter SG ID

```sh
export DB_SG_ID=""
gp env DB_SG_ID=""
```
Enter SG Rule ID

```sh
export DB_SG_RULE_ID=""
gp env DB_SG_RULE_ID=""
```

Enter this in to a new bash script to update the SG.
rds-update-sg-rule

```sh
#! /usr/bin/bash

aws ec2 modify-security-group-rules \
    --group-id $DB_SG_ID \
    --security-group-rules "SecurityGroupRuleId=$DB_SG_RULE_ID,SecurityGroupRule={IpProtocol=tcp,FromPort=5432,ToPort=5432,CidrIpv4=$GITPOD_IP/32}"
```

Change permissions.

Before running the script.
![Before](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/SGRULEBEFORE.png)

Run the code and re-enter the SG inbound rules page

![UpdateRule](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/rdsUpdateRule.png)

![RuleUpdated](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/SGUpdated.png)

To ensure that this can be done on start up enter into gitpod.yml and enter on line 17 under the postgre init section:
```yml
command: |
      export GITPOD_IP=$(curl ifconfig.me)
      source  "$THEIA_WORKSPACE_ROOT/backend-flask/bin/rds-update-sg-rule"
```
Start up a new environment when all changes have been saved. 

Enter the command to run db-connect with 'prod' after the command input:

```sh
./bin/db-connect prod
```

Update docker-compose.yml with the production db connection information, comment out the old variable:
```yml
CONNECTION_URL: "${PROD_CONNECTION_URL}"
#CONNECTION_URL: "postgresql://postgres:password@db:5432/cruddur"
```

enter the command for db-schema-load followed by 'prod' to enter a schema into the rds db, so that it can be accessed. 

Create a lambda function to create an auto update from Cognito to RDS.

Go to lambda console and create a new function
Author from scratch
Function name: cruddurpost-confirmation
runtime: python 3.8
Architecture: x86
Create a new role
Create

![Lambda](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/lambdaCreated.png)

Created a script for the lambda function [cruddur-post-confirmation.py](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/aws/lambdas/cruddur-post-confirmation.py)

Insert the script into the lambda function code source and deploy

Add env var:
CONNECTION_URL - save as the details saved in gitpod PROD_CONNECTION_URL

Go to layers in the function console then reference:
arn:aws:lambda:us-east-1:898466741470:layer:psycopg2-py38:2

Update lambda role to include the permissions for EC2 networking - create a policy containing:
"ec2:CreateNetworkInterface",
"ec2:DescribeNetworkInterfaces",                
"ec2:DeleteNetworkInterface",                
"ec2:AttachNetworkInterface"

Add VPC information in the VPC tab.
 
Go to cognito and find userpool properties
Add lambda trigger
sign up
post confirmation trigger
select the function

When configured, the creation of a new user will not produce errors in Cloudwatch logs.

![IAM](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/CreateAPolicy.png)

## Creating an activity
Create activities to input data onto cruddur home feed 

Edit db.py see link [db.py](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/backend-flask/lib/db.py)

Edit create_activity.py:
line 3:

```py
from lib.db import db
```

line 44:

```py
    else:
      expires_at = (now + ttl_offset)
      uuid = CreateActivity.create_activity(user_handle,message,expires_at)

      object_json = CreateActivity.query_object_activity(uuid)
      model['data'] = object_json
    return model

  def create_activity(handle, message, expires_at):
    sql = db.template('activities','create')
    uuid = db.query_commit(sql,{
      'handle': handle,
      'message': message,
      'expires_at': expires_at
    })
    return uuid
  def query_object_activity(uuid):
    sql = db.template('activities','object')
    return db.query_object_json(sql,{
      'uuid': uuid
    })
```

Create sql/activity folder under db folder:
Create file 'create.sql':

```sql
INSERT INTO public.activities (
  user_uuid,
  message,
  expires_at
)
VALUES (
  (SELECT uuid 
    FROM public.users 
    WHERE users.handle = %(handle)s
    LIMIT 1
  ),
  %(message)s,
  %(expires_at)s
) RETURNING uuid;
```

Create file 'object.sql':
```sql
SELECT
  activities.uuid,
  users.display_name,
  users.handle,
  activities.message,
  activities.created_at,
  activities.expires_at
FROM public.activities
INNER JOIN public.users ON users.uuid = activities.user_uuid 
WHERE 
  activities.uuid = %(uuid)s
```

Create file 'home.sql':
```sql
SELECT
  activities.uuid,
  users.display_name,
  users.handle,
  activities.message,
  activities.replies_count,
  activities.reposts_count,
  activities.likes_count,
  activities.reply_to_activity_uuid,
  activities.expires_at,
  activities.created_at
FROM public.activities
LEFT JOIN public.users ON users.uuid = activities.user_uuid
ORDER BY activities.created_at DESC
```

Edit home_activities.py:
```py
from datetime import datetime, timedelta, timezone
from opentelemetry import trace

from lib.db import db

#tracer = trace.get_tracer("home.activities")

class HomeActivities:
  def run(cognito_user_id=None):
    #logger.info("HomeActivities")
    #with tracer.start_as_current_span("home-activites-mock-data"):
    #  span = trace.get_current_span()
    #  now = datetime.now(timezone.utc).astimezone()
    #  span.set_attribute("app.now", now.isoformat())
    sql = db.template('activities','home')
    results = db.query_array_json(sql)
    return 
```

Test by running up the cruddur app and clciking the 'Crud' button on the main feed. the button will prompt for a message, write a short message and click crud just under the text box. An entry should form below if successful.

![Cruddur](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/CruddurCrud.png)
