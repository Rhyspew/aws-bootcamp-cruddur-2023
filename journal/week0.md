# Week 0 — Billing and Architecture
## Beginning the Project

Prior to the course I had set up an AWS Account and followed all the pre-requisites. 
I watched the first live session, security and billing videos. 

## Required Homework

Some sensitive information has been altered to protect personal accounts (email addresses) 

### Building a Conceptual Diagram and Logical Architectural Diagram

My [Conceptual Diagram](https://lucid.app/lucidchart/83ea1b85-4349-4dea-9431-a1259ca928e5/edit?viewport_loc=359%2C-100%2C1501%2C876%2C0_0&invitationId=inv_595f0343-0aa0-433e-92e5-1fc313fee478). This diagram is a basic layout of a messaging application that uses front end and back end servers to store and publish messages.


![Conceptual Diagram](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/Course%20Conceptual%20Diagram.png)


In addition to the conceptual diagram, I created a logical architectural diagram that used an outlay of AWS icons representing AWS services. 
[Logical Architectural Diagram](https://lucid.app/lucidchart/640f43ed-75de-4b0a-ad95-bf8f1d410979/edit?viewport_loc=-436%2C-77%2C3777%2C2204%2C0_0&invitationId=inv_1fea35f0-84f6-43d6-ac84-d647607478b9)
This architecture uses a variety of services to make the aim of the conceptual diagram possible. 
It uses Route 53 for DNS
Cognito for User Authentication
EC2 containers and an Application Load Balancer. 
RDS and DynamoDB as the database services. 
AppSync combines data from DynamoDb and RDS for queries. 
External service Memento for caching
There is also a serverless solution for processing avatar images using Lambda and an S3 bucket. 


![Architecture](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/LogicalArchitectureDiagram.png)


### Account Setup and Billing Alarms 
The first task was to create a GitPod button on the repo landing page. This was done by downloading and installing the Chrome GitPod extension. 
When GitHub is opened the button will automatically appear. 
In GitHub click the GitPod button and continue to the new environment. 
Using the code found in the student help repository I was able to create a script that would install the AWS CLI on start.
I also installed the AWS CLI manually so I could use the cli during the current session. This was done using the following commands in the gitpod.yml file. 
```sh
cd /workspace
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```
I saved my AWS access keys to the environmental data which allow access to my AWS account. 

I went into the management console as the rootuser to enable billing. 
I did this by searching for Billing in the service menu, selecting billing preferences and checking 'Receive Billing Alerts'. 

During the GitPod session I was able to create three scripts:
  1. Create a budget with notifications via SNS. 
  ```json
  [
  {
      "Notification": {
          "ComparisonOperator": "GREATER_THAN",
          "NotificationType": "ACTUAL",
          "Threshold": 80,
          "ThresholdType": "PERCENTAGE"
      },
      "Subscribers": [
          {
              "Address": "rhy8904@discord.discord",
              "SubscriptionType": "EMAIL"
          }
      ]
  }
]
  ```
  2. Create a Budget Alarm.
  
  ![Budget](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/Rhys%20Budget%20Proof.png)
  ```json
  {
  "BudgetLimit": {
      "Amount": "1",
      "Unit": "USD"
  },
  "BudgetName": "Rhys-Zero-Spend-Budget",
  "BudgetType": "COST",
  "CostFilters": {
      "TagKeyValue": [
          "user:Key$value1",
          "user:Key$value2"
      ]
  },
  "CostTypes": {
      "IncludeCredit": true,
      "IncludeDiscount": true,
      "IncludeOtherSubscription": true,
      "IncludeRecurring": true,
      "IncludeRefund": true,
      "IncludeSubscription": true,
      "IncludeSupport": true,
      "IncludeTax": true,
      "IncludeUpfront": true,
      "UseBlended": false
  },
  "TimePeriod": {
      "Start": 1477958399,
      "End": 3706473600
  },
  "TimeUnit": "MONTHLY"
  ```
  3. Create a CloudWatch Alarm that will trigger when a spending threshold has been met.
  
  ![CWAlarm](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/CWAlarm-Active.png)
  ```json
  {
  "AlarmName": "DailyEstimatedCharges",
  "AlarmDescription": "This alarm is triggered if the daily estimated charges exceeds 1$",
  "ActionsEnabled": true,
  "AlarmActions": [
      "arn:aws:sns:arn:aws:sns:us-east-1:92699402331:billing-alarm"
  ],
  "EvaluationPeriods": 1,
  "DatapointsToAlarm": 1,
  "Threshold": 1,
  "ComparisonOperator": "GreaterThanOrEqualToThreshold",
  "TreatMissingData": "breaching",
  "Metrics": [{
      "Id": "m1",
      "MetricStat": {
          "Metric": {
              "Namespace": "AWS/Billing",
              "MetricName": "EstimatedCharges",
              "Dimensions": [{
                  "Name": "Currency",
                  "Value": "USD"
              }]
          },
          "Period": 86400,
          "Stat": "Maximum"
      },
      "ReturnData": false
  },
  {
      "Id": "e1",
      "Expression": "IF(RATE(m1)>0,RATE(m1)*86400,0)",
      "Label": "DailyEstimatedCharges",
      "ReturnData": true
  }]
}
  ```  


### Launching AWS CloudShell
Cloudshell is a cloud based means of entering the CLI to programmatically configure AWS resources. 
I was able find cloudshell via the management console, open it then log in and display my AWS credentials. Using the code:
``` sh
aws sts get-caller-identity
```
Following the command entry the CLI returned the following with my account details and User ID complete:
```json
{
    "UserId": "",
    "Account": "",
    "Arn": ""
}
```

## Homework Challenges

### Root Account Shutdown
Once billing alarms and budgets had been configured I locked down my root account. 
I did this by enabling MFA on the root account. Ensuring the password is strong (includes a mix of upper case and lower case letters, numbers and symbols). All service related actions are now to be carried out by an admin user that I created using IAM users and groups. Access keys were created using my admin IAM user.  

### Use EventBridge to Hookup Health Dashboard to SNS and Send a Notification When There is a Service Health Issue
I used an AWS whitepaper document to find the instructions to complete this task. 
Using the white paper for [Monitoring AWS Health](https://docs.aws.amazon.com/health/latest/ug/cloudwatch-events-health.html) I was able to follow and create a working alarm that will trigger an SNS message via email whenever an AWS service is down. 


![EventBridge](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/EventBridge-AWSHealth.png)


### Review all the questions of each pillars in the Well Architected Tool 
This is within the Well Architected tool service. 
Created a workload. Proceded to review questions.

Each question helps paint a picture of the goals, needs, risks, compliance requirements, potential tradeoffs and benefits a business would be considering when moving to the cloud. All factors are affected when one pillar of the well architected framework is considered over the other, a balance has to be met that satisfies the business needs while managing risk and potential issues. The six pillars are displayed below with the number of questions required to answer in the well architected tool. 


![Questions](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/Well%20Architected%20Tool.png)


### Create an architectural diagram (to the best of your ability) the CI/CD logical pipeline in Lucid Charts
My [CICD Logical Architecure Diagram](https://lucid.app/lucidchart/967e7dad-53de-45c6-bccb-dc203e7ff0a2/edit?viewport_loc=-291%2C-430%2C2363%2C1180%2C0_0&invitationId=inv_92950db0-57c7-47c0-ab49-689aa87e3baf). This diagram shows a CICD Pipeline using Code Pipeline. 
The user will commit code to a repository such as GitHub or CodeCommit. The commit must contain a file named buildspec.yaml to carry out a build.  

Next the build stage. CodeBuild will pull the code from the CodeCommit repo and build the code in an isolated environment. If at any stage the build fails the user will be notified of the error in the code, reducing the time taken to fix bugs and typos. 

After successful builds, CodeBuild will generate a CloudFormation Template file into Amazon S3. 

The deploy stage will deploy the cloudformation template, either to development and test, or to production environments.


![CICD Diagram](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/CICD.png)


### Open a support ticket and request a service limit
This task can be done in the Service Quotas Service. 
I used the whitepaper [Requesting a Quota Increase](https://docs.aws.amazon.com/servicequotas/latest/userguide/request-quota-increase.html) to find out how to complete this task. I completed the task using the Management Console. 


![Service Quota options](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/Service%20Quota%20Menu.png)


![Service Quota pending](https://github.com/Rhyspew/aws-bootcamp-cruddur-2023/blob/main/_docs/assets/Service%20Quota%20Change%20Pending.png)


