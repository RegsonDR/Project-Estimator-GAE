from models import WorkspaceDetails, AccountDetails, UserProfile, ProjectDetails, TaskDetails
from flask import flash


def create_wks(workspace_name, user_key):
    workspace_data = WorkspaceDetails(
        workspace_name=workspace_name
    )
    if not workspace_data.put():
        flash('Organization not created.', 'danger')
        return False

    user_profile = UserProfile(
        User=user_key,
        workspace_name=workspace_name,
        Wks=workspace_data.key,
        role='super-admin'
    )
    if not user_profile.put():
        flash('Organization not created.', 'danger')
        return False

    flash('Organization successfully created.', 'success')
    return workspace_data


def create_project(wks_key, form_data):
    project_data = ProjectDetails(
        Wks=wks_key,
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
                task_skills= map(int, form_data['Task'][task]['Skills']),
                task_developers= map(int, form_data['Task'][task]['Developers']),
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


def check_access(wks_key, user_key):
    return UserProfile.query(UserProfile.Wks == wks_key, UserProfile.User == user_key).get()


def get_workspaces(user_key):
    wks_objects = UserProfile.query(UserProfile.User == user_key).fetch()
    return wks_objects


def get_projects(wks_key, project_status):
    project_objects = ProjectDetails.query(ProjectDetails.Wks == wks_key,
                                           ProjectDetails.project_status == project_status).fetch()
    return project_objects


def get_open_task_number(project_key):
    return TaskDetails.query(TaskDetails.Project == project_key, TaskDetails.task_status == "Open").count()

def get_total_task_number(project_key):
    return TaskDetails.query(TaskDetails.Project == project_key).count()

