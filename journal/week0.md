# Week 0 — Billing and Architecture
## Beginning the Project

Prior to the course I had set up an AWS Account and followed all the pre-requisites. 
I watched the first live session, security and billing videos. 

## Required Homework

Some sensitive information has been altered to protect personal accounts (email addresses) 

### Building a Conceptual Diagram and Logical Architectural Diagram

Following the video instruction I was able to create a conceptual diagram of the cruddur app and understand the basic resource outlay needed to create such an application. [Conceptual Diagram](https://lucid.app/lucidchart/83ea1b85-4349-4dea-9431-a1259ca928e5/edit?viewport_loc=359%2C-100%2C1501%2C876%2C0_0&invitationId=inv_595f0343-0aa0-433e-92e5-1fc313fee478)
In addition to the conceptual diagram, I created a logical architectural diagram that used an outlay of resources and icons. 
[Logical Architectural Diagram](https://lucid.app/lucidchart/640f43ed-75de-4b0a-ad95-bf8f1d410979/edit?viewport_loc=-436%2C-77%2C3777%2C2204%2C0_0&invitationId=inv_1fea35f0-84f6-43d6-ac84-d647607478b9)

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

During the session I was able to create three scripts:
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
  2. Create a Budget Alarm linked to the SNS topic that will trigger when my budget has reached 80%.
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


### Review all the questions of each pillars in the Well Architected Tool 

### Create an architectural diagram (to the best of your ability) the CI/CD logical pipeline in Lucid Charts

### Research the technical and service limits of specific services and how they could impact the technical path for technical flexibility. 

### Open a support ticket and request a service limit
This task can be done in the Service Quotas Service.

