# Week 5 — DynamoDB and Serverless Caching

This week I created the DynamoDB for the app, with caching for the messaging service. 

Added boto3 to requirements.txt
Added pip install to gitpod.yml to install on start up
Rearranged bash scripts to be in separate folders and shorten names.
Correct updates in db-setup file - now setup in [db](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/tree/main/backend-flask/bin/db) folder.
Create [ddb](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/tree/main/backend-flask/bin/ddb) folder and add files. 
Change permissions and run schema-load

Create another file in ddb - list-tables
Run list tables
![List Tables](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/List-Tables-ddb.png)

Run ddb/drop

![Drop](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/ddbDrop.png)

Run seed. Make sure cruddur db is running first.

Create scan file in ddb. run to test - return seeded data

Created new folder called patterns
Make new files called list-conversations and get-conversation
Change permissions. Run get-conversations

![ListConversations](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/list-conversations-return.png)

![GetConversations](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/get-conversation-return.png)

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

create ddb.py in the [lib](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/tree/main/backend-flask/lib) backend folder

create [cognito](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/tree/main/backend-flask/bin/cognito) folder in bin - Create 

run code in terminal to find users in cognito user pool

```sh
aws cognito-idp list-users --user-pool-id=<UPID>
```
Set AWS_COGNITO_USER_POOL_ID variables. export and gp env

Create update_cognito_user_ids in bin/db folder

![UpdateCognito](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/PullUIDFromCognito.png)

Update db/setup to include new file. make sure to replace 'source' with python to run the script. 

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
If everything has worked and ddb/seed has been run then the conversation will be seen in messages when logged in. 

![Messages](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/MessageFeedFixed.png) 

Edited get_conversations to use correct year in message metadata. 

Edited seed line 233 to display seeded messages in base time -3 hours to allow my messages to be seen. 

Edit MessageGroupItem.js to include uuid. 

Edit messages.py

Edit create_message.py

Add in files user_short.py in backend services

Enter short.sql into db/sql/users

In backend - db/sql/users create a new file create_message_users.sql
In same folder create folder 
Add 'from services.users_short import *' to app.py to reference new document and add in route at bottom of code. 

Add new file to frontend src/components: MessageGroupNewItem.js

Edit MessageGroupFeed.js

![NewMessage](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/MessageList.png)

Added in new db user manually to test messages. 
Connect into DB. 
INSERT INTO public.users (display_name, email, handle, cognito_user_id)
VALUES
  ('Leonardo Turtle','tmnt@ninja.com' , 'leo' ,'MOCK');

Find user by entering messages endpoint followed by /new/leo.

![NewUser](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/NewUser.png)

Entered ./bin/ddb/schema-load prod into terminal. cruddur-messages was created in dynamoDB

## AWS Management Console
### Lambda and DynamoDB
Go to AWS console and enter the DynamoDB menu. Turn on streams with new image. 

Create a VPC Endpoint. Go to VPC menu, create endpoint, name it cruddur-ddb. Select DynamoDB as the service and select the defaults for the other options. Skip the policy creation and create. 

Created a lambda function for the message stream - create a new role and associate with the default vpc
Use the code from [cruddur-messaging-stream](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/aws/lambdas/cruddur-messaging-stream.py) 
Update the permissions to include AWSLambdaInvocation-DynamoDB and custom policy from [cruddur-message-stream-policy.json](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/aws/policies/cruddur-message-stream-policy.json)

Add the lambda function as a trigger to the dynamoDb table. 

Comment out the AWS ENDPOINT URL in docker compose

Play about with the cruddur app making sure to enter /new/<userhandle> after the message page url. 

After adding some of the items to the DDB table with new user group ids and messages, I deleted the entries and checked the app, all messages had been deleted. Checked CloudWatch logs to ensure entries had been recorded. 
![Logs](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/LogsLambdaTrigger.png)
  
  








