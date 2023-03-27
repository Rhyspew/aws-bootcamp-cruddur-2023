# Week 5 — DynamoDB and Serverless Caching

This week I created the DynamoDB for the app, with caching for the messaging service. 

dd boto3 to requirements.txt
Add pip install to gitpod.yml to install on start up
Rearranged bash scripts to be in separate folders and shorten names.
Correct updates in db-setup file - now setup in db folder.
Create ddb folder and add files. 
change permissions and run schema-load
Create another file in ddb - list-tables
run list tables. See pics
run ddb/drop see pics
run seed. Make sure cruddur db is running first. see pics
create scan file in ddb. run to test - return seeded data
Created new folder called patterns
Make new files called list-conversations and get-conversation
Change permissions. Run get-conversations

db.py updated line 85 - 91:

```py
  def query_value(self,sql,params={}):
    self.print_sql('value',sql,params)
    with self.pool.connection() as conn:
      with conn.cursor() as cur:
        cur.execute(sql,params)
        json = cur.fetchone()
        return json[0]
```

Run list-conversations (Error on terminal shown because of reverse code command. To be implemented later in the task)

Updated db/drop to only drop if table exists. 
```sh
psql $NO_DB_CONNECTION_URL -c "drop database IF EXISTS cruddur;"
```

create ddb.py in the lib backend folder

create cognito folder in bin - Create 

run code in terminal to find users in cognito user pool
```sh
aws cognito-idp list-users --user-pool-id=<UPID>
```
Set AWS_COGNITO_USER_POOL_ID variables. export and gp env

Create update_cognito_user_ids in bin/db folder

Update setup to include new file.

Update db to display handle and sub details in update cognito uId return message.

Updated app.py lines 121 - 138 to include cognito authentication

Update MessageGroups.py

Create new folder: sql/users
Create file uuid_from_cognito_user_id.sql

Update MessageGroupsPage.js
Update Message GroupPage.js
Update MessageForm.js

Create new folder called lib in frontend src.
Create a new file CheckAuth.js

Update HomeFeedPage.js

Add AWS_ENDPOINT_URL to docker compose file in backend environment - Run docker down then back up to continue

Update Apps.js with new handle for message group pages

Edited get_conversations to use correct year in message metadata. 

Edit MessageGroupItem.js to include uuid. 

Edit messages.py

Edit create_message.py

In backend - db/sql/users create a new file create_message_users.sql
In same folder create folder 
Add 'from services.users_short import *' to app.py to reference new document and add in route at bottom of code. 

Add new file to frontend src/components MessageGroupNewItem.js

Added in new db user manually to test messages. 
Connect into DB. 
INSERT INTO public.users (display_name, email, handle, cognito_user_id)
VALUES
('Noah AWS','noah@theboa.com' , 'noah' ,'MOCK')

Test in Cruddur app, could not get noah id to load so found that I could change the front end url to /messages/noah and insert a message from there. 

