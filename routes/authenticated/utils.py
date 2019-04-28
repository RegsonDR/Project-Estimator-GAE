from models import WorkspaceDetails, AccountDetails, UserProfile, ProjectDetails, TaskDetails, ProjectChat, SkillData, \
    UserSkill
from flask import flash, request, url_for, render_template
from google.appengine.api import mail
from app_statics import APP_NAME
import uuid


def create_wks(workspace_name, user_email):
    workspace_data = WorkspaceDetails(
        workspace_name=workspace_name,
        allow_dev_skills=True,
        api_key = uuid.uuid4().hex,
        enable_api=False
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


def create_project(wks_key, user_email, description,start, deadline, name):
    project_data = ProjectDetails(
        Wks=wks_key,
        project_manager=user_email,
        project_name=name,
        project_description=description,
        project_start = start,
        project_deadline=deadline,
        project_status="Running",
        project_stage="Planning"
    )
    if not project_data.put():
        flash('Project not created.', 'danger')
        return False

    flash('Project successfully created.', 'success')
    return project_data.key.id()


def get_user_data_by_email(email):
    return AccountDetails.query(AccountDetails.email == email.lower()).get()


def get_user_data_by_id(datastore_id):
    return AccountDetails.get_by_id(datastore_id)


def get_wks_data_by_id(datastore_id):
    return WorkspaceDetails.get_by_id(datastore_id)


def get_project_data_by_id(project_id):
    return ProjectDetails.get_by_id(project_id)


def get_task_data_by_id(task_id):
    return TaskDetails.get_by_id(task_id)


def check_access(wks_key, user_email):
    return UserProfile.query(UserProfile.Wks == wks_key, UserProfile.invitation_accepted == True,
                             UserProfile.disabled == False,
                             UserProfile.UserEmail == user_email).get()


def check_project_access(projects_data, user_email, role):
    if role == "admin":
        return True
    if role == "manager":
        project = ProjectDetails.get_by_id(projects_data.key.id())
        user_id = AccountDetails.query(AccountDetails.email == user_email).get().key.id()
        if user_id in project.get_developers():
            return True
        if projects_data.project_manager == user_email:
            return True
    if role == "developer":
        project = ProjectDetails.get_by_id(projects_data.key.id())
        user_id = AccountDetails.query(AccountDetails.email == user_email).get().key.id()
        if user_id in project.get_developers():
            return True
    return False


def get_workspaces(user_email):
    wks_objects = UserProfile.query(UserProfile.UserEmail == user_email, UserProfile.disabled == False,
                                    UserProfile.invitation_accepted == True).fetch()
    return wks_objects


def get_all_projects(wks_key, role, user_email, user_id):
    if role == "admin":
        project_objects = ProjectDetails.query(
            ProjectDetails.Wks == wks_key
        ).fetch()
    elif role == "manager":
        project_objects = []
        projects = ProjectDetails.query(ProjectDetails.Wks == wks_key).fetch()
        for project in projects:
            if user_id in project.get_developers() or project.project_manager == user_email:
                project_objects.append(project)
    elif role == "developer":
        projects = ProjectDetails.query(ProjectDetails.Wks == wks_key
                                        ).fetch()
        project_objects = []
        for project in projects:
            if user_id in project.get_developers():
                project_objects.append(project)
    return project_objects


def get_projects(wks_key, role, user_email, project_status, user_id):
    if role == "admin":
        project_objects = ProjectDetails.query(
            ProjectDetails.Wks == wks_key,
            ProjectDetails.project_status == project_status
        ).fetch()
    elif role == "manager":
        project_objects = []
        projects = ProjectDetails.query(ProjectDetails.Wks == wks_key,
                                        ProjectDetails.project_status == project_status).fetch()
        for project in projects:
            if user_id in project.get_developers() or project.project_manager == user_email:
                project_objects.append(project)

    elif role == "developer":
        projects = ProjectDetails.query(ProjectDetails.Wks == wks_key,
                                        ProjectDetails.project_status == project_status).fetch()
        project_objects = []
        for project in projects:
            if user_id in project.get_developers():
                project_objects.append(project)
    return project_objects


def get_open_task_number(project_key):
    return TaskDetails.query(TaskDetails.Project == project_key, TaskDetails.task_status == "Open").count()


def get_total_task_number(project_key):
    return TaskDetails.query(TaskDetails.Project == project_key).count()


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
    messages = ProjectChat.query(ProjectChat.project_id == project_id).order(ProjectChat.message_time).fetch(
        projection=[ProjectChat.username,
                    ProjectChat.message, ProjectChat.message_time, ProjectChat.email, ProjectChat.role])
    return messages


def get_tasks(project_key, role, user_id):
    if role == "developer":
        return TaskDetails.query(TaskDetails.Project == project_key, TaskDetails.task_developers == user_id).order(TaskDetails.task_startdate).fetch()
    return TaskDetails.query(TaskDetails.Project == project_key).order(TaskDetails.task_startdate).fetch()


def get_invites_number(email):
    return UserProfile.query(UserProfile.UserEmail == email, UserProfile.invitation_accepted == False,
                             UserProfile.disabled == False).count()


def get_invites(email):
    return UserProfile.query(UserProfile.UserEmail == email, UserProfile.invitation_accepted == False,
                             UserProfile.disabled == False).fetch()


def create_skill(skill_id, wk_key, user_key):
    try:
        int(skill_id)
    except ValueError:
        # it's not an id, it's a name.
        skill_data = SkillData(
            Wks=wk_key,
            skill_name=skill_id
        ).put()
        skill_id = skill_data.id()

    UserSkill(
        Wks=wk_key,
        User=user_key,
        skill_id=int(skill_id),
        skill_rating=1
    ).put()
    return True


def get_total_allocated_minutes(project_key):
    task_data = TaskDetails.query(TaskDetails.Project == project_key).fetch(projection=TaskDetails.task_aminutes)
    total_allocated = 0
    for task in task_data:
        total_allocated += task.task_aminutes
    return total_allocated


def get_total_logged_minutes(project_key):
    task_data = TaskDetails.query(TaskDetails.Project == project_key, TaskDetails.task_logged_minutes != None).fetch(
        projection=TaskDetails.task_logged_minutes)
    total = 0
    for task in task_data:
        total += task.task_logged_minutes
    return total




def convert_tasks(tasks):
    tasks_list = []
    level = 1
    for task in tasks:
        if not task.parent_task:
            tasks_list.append({
                'level':level,
                'id': task.key.id(),
                'key': task.key,
                'Project': task.Project,
                'task_name': task.task_name,
                'task_aminutes': task.task_aminutes,
                'task_description': task.task_description,
                'task_skills': task.task_skills,
                'task_developers': task.task_developers,
                'task_logged_minutes': task.task_logged_minutes,
                'task_startdate': task.task_startdate,
                'task_finishbydate': task.task_finishbydate,
                'task_status': task.task_status,
                'children': get_children(task.key.id(), tasks,level)
            })
            level=level+1
    return tasks_list


def get_children(parent_id,tasks,level):
    data = []
    sublevel = 1
    for task in tasks:
        if task.parent_task == parent_id:
            data.append({
                'level':str(level)+"."+str(sublevel),
                'id': task.key.id(),
                'key': task.key,
                'Project': task.Project,
                'task_name': task.task_name,
                'task_aminutes': task.task_aminutes,
                'task_description': task.task_description,
                'task_skills': task.task_skills,
                'task_developers': task.task_developers,
                'task_logged_minutes': task.task_logged_minutes,
                'task_startdate': task.task_startdate,
                'task_finishbydate': task.task_finishbydate,
                'task_status': task.task_status,
                'children': get_children(task.key.id(),tasks,str(level)+"."+str(sublevel))
            })
            sublevel = sublevel +1
    return data
