# Project Estimator
This is a project management tool I built for my final year project; the application allows managers to set up projects and tasks for developers to complete. Using machine learning, a time estimate for effort is produced for the completion of the project. In this initial version, linear regression is used as the model; however, other models can be experimented with and substituted. The application helps guide managers to choose developers most suited for specific tasks and gives graphs to help them manage the projects better. An API for the system has been produced for extendabilty. 

The application is written with Python using Flask on Google App Engine. 
An example of the site is deployed at https://project-application-231720.appspot.com/ (you can contact me for the login details).

## Set up
All the following auth tokens needs to be populated.

- main.py:12 Change SECRET_KEY to a random string of characters.
- app_settings.py:2    Google Recaptcha secret.
- ajax/utlis.py:61  Pusher app id
- ajax/utlis.py:62  Pusher app key
- ajax/utlis.py:63  Pusher app secret
- ajax/utlis.py:72  Pusher app id
- ajax/utlis.py:75  Pusher app key
- /routes/authenticated/templates/authenticated/html/project_chat.html:88   Pusher app key
- /routes/unauthenticated/templates/unauthenticated/html/register_page.html:28 Google Recaptcha sitekey.

Google App Engine SDK is required.

## Core Infrastructure
A user is required to create an account, which would need to be confirmed with email verification before the ability to access the application. The user is presented with a page displaying all of their connected workspaces; these are workspaces the user created or have been invited to join. From this page, the user can also create a new workspace. 
Creating a workspace gives the user the admin role for that workspace, other users can be invited in from the users' settings page where users can be managed. This page is only available to users with the admin roles. Admins have full visibility of the system, which means they can see all projects and tasks in the system without needing to be added the said resource. In order to use the system, skills must be set up for any user, and this allows that user to be added to a task. It is not possible to add a user to a task if they do not own the skills required for it. Admins can upload historical function points data, which will produce ML prediction on the duration of the projects; these predictions should only be used as a suggestion.  
Projects can be created from the workspace homepage. The homepage only shows projects which have been granted access to the user. Project Managers can see any of their projects or projects where they have been used as a developer in a task, and they will be able to see all tasks in that project. However, developers can only see projects and tasks which they have been added to.
After a project has been created and tasks have been assigned, the developers can log their time against each of the tasks, crossing the allocated time will highlight the task enabling the project managers to notice that there will be potential overrun.

## Development
### Frontend
Through the functionality of Flask and Jinja2, all templates were created primarily using DRY principle. Application context was used to pass information from the backend to the frontend, so pages are dynamic and based on the role of the user currently logged in, so they only access and view content permitted to them. HTML Templates can be found in the relevant /routes folder. For example, the homepage can be found in /routes\authenticated\templates\authenticated\html

All Templates are designed in the following structure:

<img src="https://image.prntscr.com/image/Q3pAY49BQe6cIY8ZsniBZw.png" width="30%"></img>

### Authorization and Error Handling
A Python decorator function was used to authorize all user requests, the decorator used checked the role of the currently logged in user against the required for the page. Usage of the python decorator this was useful as it allowed for page pre-processing. The function also checked and only loaded projects and tasks available to that user. So, if the user wasn’t permitted, they would be redirected straight to 403 or 404 pages, if they were permitted, their unique data was temporarily stored in a class object and past to the page function for usage. 

<img src="https://image.prntscr.com/image/MsUD5fGiRg6YoyOD8RWCGQ.png" width="50%"></img>

### Project Chat
The project chat was created with the usage of web sockets, which provide full-duplex communication with TCP connections. Web sockets were used because the project chat is a live chat and messages are pushed to the screen without the need to refresh the page. This functionality was achieved using Pusher API and AJAX. Each project has its own unique chatroom available to the admin, project manager and developer assigned. The messages are stored in base 64 in the datastore, to provide some privacy.  As the Pusher python library uses C extensions, the documentation following the Pusher REST API usage and authentication was followed

### Gantt Chart 
The project’s task data is retrieved from the datastore and put in a list of maps, which is passed as application context to the FullCalender Scheduler API in the frontend to render the chart. This was a powerful API as it provided a lot of customization options in order to produce a chart similar to a Gantt Chart. It is important to note that a premium license must be purchased in order to use FullCalender API in a production environment. 

### Skills Matrix
All the used skills and each of the user’s skill ratings in the workspace is obtained and stored as a list of maps. This is passed as an application context to the frontend, where it is looped through in order to produce the skill matrix. CSS was used in order to produce the grid.

### Task Level
Recursion is used to calculate a task’s sub level (task dependencies). The function loads the current task and calls itself to get the children task of the current task. This is done until all tasks have been looped through and sub levels have been generated. This functionally was used found via the API and the project page.

### Predicted Time
After an admin uploads a CSV file, the CSV is processed and prepared by removing non-integer rows. The B0 and B1 are calculated for the linear regression and stored in the datastore, ready for further calculation when a prediction is required. If the prediction produced is less than 0 then more data is required, this is shown to the user.
- The file must be saved as an “CSV”.
- The file must have the headers “functional_points” and “actual_minutes” as the first row.
- The following rows must have integers as values for both columns, otherwise this row will be skipped.

<img src="https://image.prntscr.com/image/zdcBDW3MTyWjqsiCgFHzhg.png" width="20%"></img>

### API
An API key is generated for workspaces, with the ability to regenerate it for security purposes. Authorization required both the workspace id (as username) and API key (as password) to be passed through the basic authorization HTTP method. On each API request, these credentials are checked before processing the request with the usage of a Python Decorator function. Basic authorization was chosen because the implementation of OAuth would have proven to be time-consuming.
 
 ## Security Considerations
- Input Validation: Input fields had client-side and server-side validation which would then alert the user to make changes as required. Server-side sanitation was used when data was inserted into the datastore.  Additional CRSF tokens were utilized to prevent false input.
- Password Strength: Upon registration, the application displayed the strength of the password against common passwords, names and pattern which gave a rough indication if it should be altered or not.
- Password Reset Token: A randomly generated and unique token was generated when users wanted to change their passwords; this meant malicious users could not change accounts which were not theirs.  
- CAPTCHA: In order to prevent most fake traffic from creating fake accounts, Google’s CAPTCHA API generated text/numbers which humans can read.
- Email Verification: The email address used at sign up needed to be verified to prove that the email address is owned by the user who signed up with it. Additionally, the email had to be correct if the user wanted to reset their password in future as the generation token would be emailed to them privately.
- Hash and Salted Passwords: Passwords were hashed which made it impossible for humans to read and difficult to crack. It was also a method of prevention if an attacker managed to get information from the datastore, they would not be able to log into any accounts.
- Basic Header Authorization: API calls required workspace ID and API  key in order to execute any of the API commands. 

## ERD
<img src="https://image.prntscr.com/image/vOMKM2XaQyerayYRNppYmg.png" width="70%"></img>

## Use Case
<img src="https://image.prntscr.com/image/-ycHoEUrQiKRtguZ6vakog.png" width="70%"></img>

## APIs and libraries used

| Name  | Usage |
| ---- | ---- | 
|Pusher | Enabled easier use of web sockets and used in project chat.|
|Google Recaptcha | Used on register page to prevent spam and abuse.|
|DataTables | Made displaying entities more appealing, used in users list.|
|DatePicker | Provided a GUI of calendar dates for selection.|
|Chosen | Enabled multiselect drop downs.|
|Full Calender Scheduler | Created calendar which was used in timelines and Gantt chart.|
|Select2 | Enabled create your own option in drop downs.|
|zxcvbn | Checked password strength.|
|Werkzeug | Provided additional security when handling files and passwords.|
|Urlfetch | Produced HTTP requests, used for accessing APIs.|
|Numpy | Array computation library used in parsing the csv.|

# API Documentation
## Introduction
The API for this project allows any authenticated admin to perform admin operations which is available through the web application with the usage of REST http requests. It does not allow access to update a user’s personal information as this is up to the user. Each resource can be accessed and modified by an URL endpoint. This documentation will explain the methods, parameters and data types for each of the API requests.

## Getting Started
In order to use the API, the admin of the workspace must log into their account and enable API access in the workspace settings. This will allow REST communication to the application. This access can be revoked at any time. An API key is provided which will be used in authentication of the REST calls. This key can be regenerated at any time, which in doing will make the previous API keys obsolete.

## Authentication
The application uses basic authorization header, the username is the workspace ID, which can be found in the URL of the any workspace (“Workspace/<Workspace_ID>/”) and the password is the API key. These parameters need to be in base 64 as per the requirements of basic authorization method.

## HTTP Methods
- GET – Used to obtain data.
- POST – Used to create new entities or to perform actions. Parameters must be provided in the HTTP body.
- PUT – Used to update entities. Parameters must be provided in the HTTP body.
- DELETE – Used to delete entities. Entity ID must be provided in the endpoint.

## Response
All responses including errors will be in JSON format. Codes and data properties are returned at every API call. Errors will always be explained if there is a validation issue with the data provided.

## Codes
- 200 – Successful Request
- 400 – Bad request
- 401 – Authentication failure (check username and password). 
- 403 – Forbidden access (you don’t have access to this resource).
- 404 – Resource not found.
- 405 – HTTP Method is not permitted for the endpoint.

## Data Types
- Bool – Must be either True or False
- Unicode – Must a string of characters or numbers
- [List] – Only certain entries are accepted.
- Date – In the following format dd/mm/YYYY

## API Calls
### /api/Workspaces [GET] - Returns data about the workspace.
```json
{
    "code": 200,
    "data": {
        "allow_dev_skills": true,
        "enable_webhook": false,
        "webhook_url": "http://localhost:8080/webhook/Test",
        "workspace_name": "New TesS"
    }
}

```

### /api/Workspaces [PUT] - Updates the workspace data.
Parameters:
- 'allow_dev_skills': bool
- 'workspace_name': unicode
- 'webhook_url': unicode
- 'enable_webhook': bool

### /api/Skills [GET] - Returns a list of skills within the workspace. 
```json
{
    "code": 200,
    "data": [
        {
            "SkillID": 5337854074945536,
            "skill_name": "Java",
            "usage": 1
        },
        {
            "SkillID": 6463753981788160,
            "skill_name": "PHP",
            "usage": 1
        }
    ]
}
```
### /api/Skills [POST] - Creates a new skill.
Parameters:
- 'skill_name': unicode

### /api/Users [GET] - Returns a list of users in the system with details of their profiles. A false AccountID indicates the user has not create any accounts yet.
```json
{
    "code": 200,
    "data": [
        {
            "AccountID": false,
            "ProfileID": 5082767377301504,
            "UserEmail": "fdasfdas@buycow.org",
            "disabled": false,
            "invitation_accepted": false,
            "invitation_token": "7df6778910834792a117c82313333862",
            "name": false,
            "role": "manager"
        },
        {
            "AccountID": 5629499534213120,
            "ProfileID": 5900804028366848,
            "UserEmail": "regsondr@live.co.uk",
            "disabled": false,
            "invitation_accepted": true,
            "invitation_token": null,
            "name": "Regson Dr",
            "role": "admin"
        }
    ]
}
```

### /api/Users [POST] - Invites a new user into the system.
Parameters: 
- 'UserEmail': unicode
- 'role': [‘admin’,’manager’,’developer’]

### /api/Projects [GET] - Returns a list of projects in the system and the developers permitted to access them.
```json
{
    "code": 200,
    "data": [
        {
            "Developers": [
                5629499534213120
            ],
            "ProjectID": 4942029888946176,
            "project_deadline": "04/05/2019",
            "project_description": "Description",
            "project_manager": "regsondr@live.co.uk",
            "project_name": "Name",
            "project_stage": "Planning",
            "project_start": "29/04/2019",
            "project_status": "Running"
        }
    ]
```
### /api/Projects [POST] - Creates a new project.
Parameters:
- 'project_deadline': date,
- 'project_description': unicode,
- 'project_manager': unicode,
- 'project_name': unicode,
- 'project_start': date

### /api/User/:ProfileID: [GET] – Gets full details about the user including skills and projects.
``` json
{
    "code": 200,
    "data": {
        "AccountID": 5629499534213120,
        "UserEmail": "regsondr@live.co.uk",
        "disabled": false,
        "invitation_accepted": true,
        "invitation_token": null,
        "projects": [
            {
                "ProjectID": 4942029888946176,
                "project_deadline": "04/05/2019",
                "project_description": "Description",
                "project_manager": "regsondr@live.co.uk",
                "project_name": "Name",
                "project_stage": "Planning",
                "project_start": "29/04/2019",
                "project_status": "Running"
            }
        ],
        "role": "admin",
        "skills": [
            {
                "SkillID": 6463753981788160,
                "name": "PHP",
                "skill_rating": 4
            }
        ]
    }
}
```
### /api/User/:ProfileID: [PUT] – Updates the user’s access permissions to the workspace.
Parameters:
- 'disabled': bool
- 'role': [‘admin’,’manager’,’developer’]

### /api/User/:ProfileID:/Skill [POST] – Adds a new skill to a user.
Parameters:
- 'SkillID': SkillID
- 'rating': [1,2,3,4,5]

### /api/User/:ProfileID:/Skill/:SkillID: [PUT] – Updates a user’s skill rating.
Parameters:
- 'rating': [1,2,3,4,5]

### /api/User/:ProfileID:/Skill/:SkillID: [DELETE] – Deletes the skill for that user.
### /api/Project/:ProjectID: [GET] – Returns project date, developers, tasks and children tasks.
```json
{
    "code": 200,
    "data": {
        "Developers": [
            5629499534213120,
            6420323272491008
        ],
        "Tasks": [
            {
                "TaskID": 5092662981951488,
                "children": [],
                "level": 1,
                "task_aminutes": 30,
                "task_description": "ffds",
                "task_developers": [
                    5629499534213120
                ],
                "task_finishbydate": "Fri, 31 May 2019 00:00:00 GMT",
                "task_logged_minutes": null,
                "task_name": "one more task",
                "task_skills": [
                    6463753981788160
                ],
                "task_startdate": "Tue, 14 May 2019 00:00:00 GMT",
                "task_status": "Open"
            },
            {
                "TaskID": 6067929795788800,
                "children": [
                    {
                        "TaskID": 5655612935372800,
                        "children": [],
                        "level": "2.1",
                        "task_aminutes": 40,
                        "task_description": "Desc",
                        "task_developers": [
                            6420323272491008
                        ],
                        "task_finishbydate": "Tue, 21 May 2019 00:00:00 GMT",
                        "task_logged_minutes": null,
                        "task_name": "another task",
                        "task_skills": [
                            5337854074945536
                        ],
                        "task_startdate": "Fri, 17 May 2019 00:00:00 GMT",
                        "task_status": "Open"
                    }
                ],
                "level": 2,
                "task_aminutes": 1,
                "task_description": "fdas",
                "task_developers": [
                    5629499534213120
                ],
                "task_finishbydate": "Thu, 09 May 2019 00:00:00 GMT",
                "task_logged_minutes": 0,
                "task_name": "Title",
                "task_skills": [
                    5337854074945536,
                    6463753981788160
                ],
                "task_startdate": "Mon, 29 Apr 2019 00:00:00 GMT",
                "task_status": "Closed"
            }
        ],
        "project_deadline": "04/05/2019",
        "project_description": "Description",
        "project_manager": "regsondr@live.co.uk",
        "project_name": "Name",
        "Prediction": 78,
        "project_function_points": 60,
        "project_stage": "Planning",
        "project_start": "29/04/2019",
        "project_status": "Running"
    }
}
```
### /api/Project/:ProjectID: [PUT] – Updates project details.
Parameters:
- 'project_deadline': unicode
- 'project_description': unicode
- 'project_manager': email address of the project manager
- 'project_name': unicode,
- 'project_start': date,
- 'project_stage':unicode,
- 'project_status':[‘Running’,’Closed’,’On Hold’]

### /api/Project/:ProjectID: [DELETE] – Deletes the project and corresponding tasks, logs and chat messages.

### /api/Project/:ProjectID:/Task [POST] – Creates a new task in the project.
Paramaters:
- 'task_name': unicode
- 'task_description': unicode
- 'task_aminutes': int
- 'task_skills': [List of SkillIDs]
- 'task_developers': [List of AccountIDs]
- 'task_startdate':date
- 'task_finishbydate':date

### /api/Task/:TaskID: [GET] – Returns task details, including logs.
```json
{
    "code": 200,
    "data": {
        "Logs": [
            {
                "LogID": 6218562888794112,
                "developer_name": "Regson Dr",
                "log_comments": "did some work",
                "log_developer": 5629499534213120,
                "log_minutes": 20,
                "log_time": "Wed, 01 May 2019 16:30:00 GMT",
                "task_id": 6067929795788800
            }
        ],
        "parent_task": null,
        "task_aminutes": 1,
        "task_description": "fdas",
        "task_developers": [
            5629499534213120
        ],
        "task_finishbydate": "Thu, 09 May 2019 00:00:00 GMT",
        "task_logged_minutes": 20,
        "task_name": "Title",
        "task_skills": [
            5337854074945536,
            6463753981788160
        ],
        "task_startdate": "Mon, 29 Apr 2019 00:00:00 GMT",
        "task_status": "Closed"
    }
}
```
### /api/Task/:TaskID: [PUT] – Updates task data.
- 'task_name': unicode
- 'task_description': unicode
- 'task_aminutes': int
- 'task_skills': [List of SkillIDs]
- 'task_developers': [List of AccountIDs]
- 'task_startdate': date,
- 'task_finishbydate': date
- 'parent_task': TaskID (Cannot be itself)
- 'task_status':[‘Open’,’Closed’]

### /api/Task/:TaskID: [DELETE] – Deletes tasks and logs.
### /api/Task/:TaskID:/Log [POST] – Creates a new log for the task.
Parameters:
- 'log_developer': AccountID
- 'log_minutes': int
- 'log_comments':unicode

### /api/Log/:LogID: [PUT] – Creates a new log for the task.
Parameters:
- 'log_developer': AccountID
- 'log_minutes': int
- 'log_comments':unicode

### /api/Log/:LogID: [DELETE] – Deletes log.

## Webhook
It is also possible to set up a webhook which will allow of an external service to know of a change that has happened in the workspace. These events happen during, project, task, log creation, delete and updates. The webhook is not triggered by the API in order to prevent an infinite loop of payloads being send and APIs calls (changes) being made to the system. If the external services require additional data, then it should read the ID of the resource and make an API call to request it. The admin must enable this in the settings and provide a valid URL for the payload to be sent to.