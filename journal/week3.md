# Week 3 — Decentralized Authentication

## Amazon Cognito

Cognito is Amazons native Authenication service. More details in this link. 

Open the AWS management console
Ensure region is correct
Search for Cognito in the service tool searchbar. Open Cognito.

Create a new user pool

Step 1 - Configure sign-in experience
Leave federated identity unchecked
For cognito user pool sign in options tick:
Email

Step 2 - Configure security requirements
Leave password settings on default
No MFA
Check Enable self-service account recovery

Step 3 - Configure sign-up experience
Leave default settings
Required Attributes - Select name, preferred_username

Step 4 - Configure Message Delivery 
Send email with cognito
Keep default from address

Step 5 - Integrate your app
User Pool Name
Leave the hosted UI box unticked
Leave it on Public Client
Give it an app client name
Don't generate a client secret

Step 6 - Review
Complete
Get User ID from user pool overview

See the newly created user group 
Go to App integration tab and scroll to bottom for client id 

## AWS Amplify

A hosting platform for applications

### Download the amplify SDK in gitpod

Go to front-end directory
Enter in terminal: npm i aws-amplify --save

Install Amplify

Add the following to docker-compose.yml frontend environment:
```yml
REACT_APP_AWS_PROJECT_REGION: "${AWS_DEFAULT_REGION}"
REACT_APP_AWS_COGNITO_REGION: "${AWS_DEFAULT_REGION}"
REACT_APP_AWS_USER_POOLS_ID: "us-east-1_Qb26BWfMo"
REACT_APP_CLIENT_ID: "1nmgqc8dpcq4lm5gm8o23mlgih"
```

Edit App.py:
import NotificationsFeedPage line 4 is deleted
Added line 13: 

import process from 'process';

line 19: 
```js
import { Amplify } from 'aws-amplify';

Amplify.configure({
  "AWS_PROJECT_REGION": process.env.REACT_APP_AWS_PROJECT_REGION,
  "aws_cognito_region": process.env.REACT_APP_AWS_COGNITO_REGION,
  "aws_user_pools_id": process.env.REACT_APP_AWS_USER_POOLS_ID,
  "aws_user_pools_web_client_id": process.env.REACT_APP_CLIENT_ID,
  "oauth": {},
  Auth: {
    // We are not using an Identity Pool
    // identityPoolId: process.env.REACT_APP_IDENTITY_POOL_ID, // REQUIRED - Amazon Cognito Identity Pool ID
    region: process.env.REACT_APP_AWS_PROJECT_REGION,           // REQUIRED - Amazon Cognito Region
    userPoolId: process.env.REACT_APP_AWS_USER_POOLS_ID,         // OPTIONAL - Amazon Cognito User Pool ID
    userPoolWebClientId: process.env.REACT_APP_CLIENT_ID,   // OPTIONAL - Amazon Cognito Web Client ID (26-char alphanumeric string)
  }
});
```

In HomeFeedPage.js - Enter code:

line 4:
import { Auth } from 'aws-amplify';

line 23: 
```js
  const loadData = async () => {
    try {
      const backend_url = `${process.env.REACT_APP_BACKEND_URL}/api/activities/home`
      const res = await fetch(backend_url, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`
        },
        method: "GET"
      });
      let resJson = await res.json();
      if (res.status === 200) {
        setActivities(resJson)
      } else {
        console.log(res)
      }
    } catch (err) {
      console.log(err);
    }
  };
```

insert line 43
```js
  const loadData = async () => {
    try {
      const backend_url = `${process.env.REACT_APP_BACKEND_URL}/api/activities/home`
      const res = await fetch(backend_url, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`
        },
        method: "GET"
      });
      let resJson = await res.json();
      if (res.status === 200) {
        setActivities(resJson)
      } else {
        console.log(res)
      }
    } catch (err) {
      console.log(err);
    }
  };
```

Profile info.js
Insert line 6: 

import { Auth } from 'aws-amplify';

line 15
```js
  const signOut = async () => {
    try {
        await Auth.signOut({ global: true });
        window.location.href = "/"
        localStorage.removeItem("access_token")
    } catch (error) {
        console.log('error signing out: ', error);
    }
  }
```

Signin.js
Insert
line 7: Over auth js cookie
import { Auth } from 'aws-amplify';

line 15:
```js
  const onsubmit = async (event) => {
    setErrors('')
    event.preventDefault();
    Auth.signIn(email, password)
    .then(user => {
      console.log('user',user)
      localStorage.setItem("access_token", user.signInUserSession.accessToken.jwtToken)
      window.location.href = "/"
    })
    .catch(error => { 
      if (error.code == 'UserNotConfirmedException') {
        window.location.href = "/confirm"
      }
      setErrors(error.message)
    });
    return false
  }
```

CORS needs to be updated in backend-flask app.py to:
```py
cors = CORS(
  app, 
  resources={r"/api/*": {"origins": origins}},
  headers=['Content-Type', 'Authorization'], 
  expose_headers='Authorization',
  methods="OPTIONS,GET,HEAD,POST"
)
```

Create a user in cognito user group:
Check email
Don't send an invitation
Enter a suitable username
enter email address, mark as verified
Request an email to be sent to your inbox
generate or create a temp password.

In terminal to change user password:

```sh
aws cognito-idp admin-set-user-password --username rpladmin1 --password Testing1234! --user-pool-id us-east-1_Qb26BWfMo --permanent
```

Refresh on cognito user group in console to check 'Force Password' has changed to confirmed. 

Click on new user then go to user attributes and edit. 

Enter values for name and add attributes to raise and enter the preferred username field. 

Test again on cruddur app, sign in using cognito user credentials. If signed in the following image will be seen. 

To create a user via the cruder app create edit the sign up page.
 
SignupPage.js

Add in line 7:
import { Auth } from 'aws-amplify';

Line 18:
```js
  const onsubmit = async (event) => {
    event.preventDefault();
    setErrors('')
    console.log('username',username)
    console.log('email',email)
    console.log('name',name)
    try {
      const { user } = await Auth.signUp({
        username: email,
        password: password,
        attributes: {
          name: name,
          email: email,
          preferred_username: username,
        },
        autoSignIn: { // optional - enables auto sign in after user is confirmed
          enabled: true,
        }
      });
      console.log(user);
      window.location.href = `/confirm?email=${email}`
    } catch (error) {
        console.log(error);
        setErrors(error.message)
    }
    return false
  }
```

Confirmation.js

line 7:
import { Auth } from 'aws-amplify';

line 24:
```js
  const resend_code = async (event) => {
    setCognitoErrors('')
    try {
      await Auth.resendSignUp(email);
      console.log('code resent successfully');
      setCodeSent(true)
    } catch (err) {
      // does not return a code
      // does cognito always return english
      // for this to be an okay match?
      console.log(err)
      if (err.message == 'Username cannot be empty'){
        setCognitoErrors("You need to provide an email in order to send Resend Activiation Code")   
      } else if (err.message == "Username/client id combination not found."){
        setCognitoErrors("Email is invalid or cannot be found.")   
      }
    }
  }
```

line 43:

```js
const onsubmit = async (event) => {
  event.preventDefault();
  setCognitoErrors('')
  try {
    await Auth.confirmSignUp(email, code);
    window.location.href = "/"
  } catch (error) {
    setCognitoErrors(error.message)
  }
  return false
}
```

Once the sign up and confirmation pages have been edited, delete the existing cognito user. 

Go through the app and sign up, complete the fields and use the confirmation code that will be available via email.

The newly created user will now be confirmed in cognito. Log back into app to confirm. 


To recover password if forgotten:
recoverPage.js

line 5
import { Auth } from 'aws-amplify';

line 16
```js
 const onsubmit_send_code = async (event) => {
    event.preventDefault();
    setErrors('')
    Auth.forgotPassword(username)
    .then((data) => setFormState('confirm_code') )
    .catch((err) => setErrors(err.message) );
    return false
  }
```

line 24
```js
 const onsubmit_confirm_code = async (event) => {
    event.preventDefault();
    setErrors('')
    if (password == passwordAgain){
      Auth.forgotPasswordSubmit(username, code, password)
      .then((data) => setFormState('success'))
      .catch((err) => setErrors(err.message) );
    } else {
      setCognitoErrors('Passwords do not match')
    }
    return false
  }
```
