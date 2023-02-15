# Week 0 — Billing and Architecture
## Beginning the Project


Prior to the course I had set up an AWS Account and followed all the pre-requisites. 
I watched the first live session and the security and billing videos. 


### Building a Conceptual and Logical Architectural Diagram


#### Using Lucid Charts to create diagrams
Following the video instruction I was able to create a conceptual diagram of the cruddur app and understand the basic resource outlay needed to create such an application. [Conceptual Diagram](https://lucid.app/lucidchart/83ea1b85-4349-4dea-9431-a1259ca928e5/edit?viewport_loc=359%2C-100%2C1501%2C876%2C0_0&invitationId=inv_595f0343-0aa0-433e-92e5-1fc313fee478)
In addition to the conceptual diagram, I created a logical architectural diagram that used an outlay of resources and icons. 
[Logical Architectural Diagram](https://lucid.app/lucidchart/640f43ed-75de-4b0a-ad95-bf8f1d410979/edit?viewport_loc=-436%2C-77%2C3777%2C2204%2C0_0&invitationId=inv_1fea35f0-84f6-43d6-ac84-d647607478b9)

#### Account Setup and Billing Alarms 
The first task was to create a GitPod button on the repo landing page. This was done by downloading and installing the Chrome GitPod extension. 
When GitHub is opened the button will automatically appear. 
In GitHub click the GitPod button and continue to the interface. The browser will take you to a new window, using the code found in the student help repository, to add to the start up, the code will create more magic 

Launching AWS CloudShell and looking at AWS CLI
Generating AWS credentials

## Homework Challenges


Shut down my root account by creating a strong passwor, 2FA and creating an IAM admin user in which the majority of my work will be carried out on. This ensures that if my IAM user account is compromised they do not have the permissions to change any of the billing settings, preventing them from stealing money or charging my account what I can not afford. 

Use EventBridge to hookup Health Dashboard to SNS and send notification when there is a service health issue.
Review all the questions of each pillars in the Well Architected Tool (No specialized lens)

Create an architectural diagram (to the best of your ability) the CI/CD logical pipeline in Lucid Charts

Research the technical and service limits of specific services and how they could impact the technical path for technical flexibility. 

Open a support ticket and request a service limit
