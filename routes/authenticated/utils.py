from models import WorkspaceDetails, AccountDetails, UserProfile, ProjectDetails, TaskDetails, ProjectChat
from flask import flash, request, url_for, render_template
from google.appengine.api import mail
from app_statics import APP_NAME
import uuid


def create_wks(workspace_name, user_email):
    workspace_data = WorkspaceDetails(
        workspace_name=workspace_name
    )
    if not workspace_data.put():
        flash('Workspace not created.', 'danger')
        return False

    user_profile = UserProfile(
        UserEmail=user_email,
        workspace_name=workspace_name,
        Wks=workspace_data.key,
        role='admin',
        invitation_accepted=True,
        disabled=False
    )
    if not user_profile.put():
        flash('Workspace not created.', 'danger')
        return False

    flash('Workspace successfully created.', 'success')
    return workspace_data


def create_project(wks_key, user_email, form_data):
    project_data = ProjectDetails(
        Wks=wks_key,
        project_manager=user_email,
        project_name=form_data['project_name'],
        project_description=form_data['project_description'],
        project_deadline=form_data['project_deadline'],
        project_status="Running",
        project_stage="Planning"
    )
    if not project_data.put():
        flash('Project not created.', 'danger')
        return False

    for task in form_data['Task']:
        if form_data['Task'][task]['Developers']:
            print form_data['Task'][task]
            task_data = TaskDetails(
                Project=project_data.key,
                task_name=form_data['Task'][task]['Title'],
                task_description=form_data['Task'][task]['Description'],
                task_skills=map(int, form_data['Task'][task]['Skills']),
                task_developers=map(int, form_data['Task'][task]['Developers']),
                task_aminutes=int(form_data['Task'][task]['aMinutes']),
                task_status="Open"
            )

            task_data.put()

    flash('Project successfully created.', 'success')
    return project_data


def get_user_data_by_email(email):
    return AccountDetails.query(AccountDetails.email == email.lower()).get()


def get_user_data_by_id(datastore_id):
    return AccountDetails.get_by_id(datastore_id)


def get_wks_data_by_id(datastore_id):
    return WorkspaceDetails.get_by_id(datastore_id)

def get_project_data_by(datastore_id):
    return ProjectDetails.get_by_id(datastore_id)


def check_access(wks_key, user_email):
    return UserProfile.query(UserProfile.Wks == wks_key, UserProfile.invitation_accepted == True, UserProfile.disabled == False,
                             UserProfile.UserEmail == user_email).get()


def check_project_access(projects_data, user_email, role):
    if role == "admin":
        return True
    if role == "manager":
        if projects_data.project_manager == user_email:
            return True

    return False


def get_workspaces(user_email):
    wks_objects = UserProfile.query(UserProfile.UserEmail == user_email,  UserProfile.disabled == False,
                                    UserProfile.invitation_accepted == True).fetch()
    return wks_objects


def get_projects(wks_key, role, user_email, project_status):
    if role == "admin":
        project_objects = ProjectDetails.query(
            ProjectDetails.Wks == wks_key,
            ProjectDetails.project_status == project_status
        ).fetch()
    else:
        project_objects = ProjectDetails.query(
            ProjectDetails.Wks == wks_key,
            ProjectDetails.project_status == project_status,
            ProjectDetails.project_manager == user_email
        ).fetch()

    return project_objects


def get_open_task_number(project_key):
    return TaskDetails.query(TaskDetails.Project == project_key, TaskDetails.task_status == "Open").count()


def get_total_task_number(project_key):
    return TaskDetails.query(TaskDetails.Project == project_key).count()


def get_project_data_by_id(project_id):
    return ProjectDetails.get_by_id(project_id)


def get_all_users(wks_key):
    return UserProfile.query(UserProfile.Wks == wks_key).fetch()


def add_user(wks_key, workspace_name, UserEmail, role):
    if UserProfile.query(UserProfile.Wks == wks_key, UserProfile.UserEmail == UserEmail).get():
        flash('User: ' + UserEmail + ' already invited to this workspace!', 'danger')
        return False

    token = uuid.uuid4().hex
    user_data = UserProfile(
        Wks=wks_key,
        workspace_name=workspace_name,
        UserEmail=UserEmail,
        role=role,
        invitation_token=token,
        invitation_accepted=False,
        disabled=False
    )
    if not user_data.put():
        flash('Error occurred, User: ' + UserEmail + ' not created.', 'danger')
        return False

    send_invitation_email(token, UserEmail)
    flash('User: ' + UserEmail + ' invited!', 'success')
    return True


def send_invitation_email(verification_code, email):
    VERIFICATION_URL = (request.url_root + url_for('authenticated.open_invitation').replace("/", "") + "?email=" +
                        email + "&code=" + verification_code)
    mail.send_mail(
        sender="support@project-application-231720.appspotmail.com",
        to=email,
        subject=APP_NAME + " Invitation Link",
        body="",
        html=render_template('authenticated/email/Invitation.html', EMAIL_HEADER="You've been invited to a workspace!",
                             VERIFICATION_URL=VERIFICATION_URL)
    )

    return True


def verify_invite(code, email):
    user_profile = UserProfile.query(UserProfile.UserEmail == email, UserProfile.invitation_token == code).get()
    if user_profile:
        return user_profile
    flash('Invitation is invalid', 'danger')
    return False

def get_chat_messages(project_id):
    messages = ProjectChat.query(ProjectChat.project_id == project_id).order(ProjectChat.message_time).fetch(projection=[ProjectChat.username,
                                                                                         ProjectChat.message,ProjectChat.message_time,ProjectChat.email,ProjectChat.role])
    return messages


def get_tasks(project_key):
    return TaskDetails.query(TaskDetails.Project == project_key).fetch()

