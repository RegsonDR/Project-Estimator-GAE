import re
import uuid
from urllib import urlopen
from datetime import datetime, timedelta

from flask import request, jsonify
from models import AccountDetails, TaskLog, UserProfile, UserSkill, TaskDetails, ProjectDetails, \
    WorkspaceDetails, SkillData
from routes.authenticated.utils import send_invitation_email, check_project_access


def return_json(data, message=None):
    response = {}
    if message:
        response['message'] = message
    response['data'] = data
    response['code'] = 200

    return jsonify(response)


def get_workspace(wk_id):
    return WorkspaceDetails.get_by_id(wk_id)


def get_all_workspace_projects(wks_key):
    return [dict(project.to_dict(), **dict(ProjectID=project.key.id(), Developers=project.get_developers())) for project
            in
            ProjectDetails.query(ProjectDetails.Wks == wks_key).fetch()]


def get_project(wks_key, project_id):
    project = ProjectDetails.get_by_id(project_id)
    if project:
        if project.Wks == wks_key:
            return project
        return {'code': 403, 'message': "Project (" + str(project_id) + ") not part of workspace. Forbidden access."}
    return {'code': 404, 'message': "Project not found: " + str(project_id)}


def get_account(ProfileID):
    return UserProfile.get_by_id(ProfileID)


def get_skills(wks_key):
    return [dict(skill.to_dict(), **dict(SkillID=skill.key.id(), usage=skill.usage())) for skill in
            SkillData.query(SkillData.Wks == wks_key).fetch()]


def get_user_skill(wks_key, account_key):
    return [dict(u_s.to_dict(), **dict(name=u_s.skill_name())) for u_s in
            UserSkill.query(UserSkill.Wks == wks_key, UserSkill.User == account_key).fetch()]


def get_user_projects(wks_key, ProfileID):
    data = get_account(ProfileID)
    return [dict(project.to_dict(), **dict(ProjectID=project.key.id())) for project in
            ProjectDetails.query(ProjectDetails.Wks == wks_key).fetch() if
            check_project_access(project, data.UserEmail, data.role)]


def validate_profile_update(wks_key, current_role, body):
    resp = {}
    if 'role' in body:
        role = body['role'].lower()
        valid_choices = ['admin', 'manager', 'developer']
        if validate_choices(role, valid_choices) == False:
            return {'code': 400, 'message': 'Invalid role provided. Must be one of ' + str(valid_choices)}
        if role == current_role:
            return {'code': 400, 'message': 'User already owns this role.'}
        if current_role == 'admin' and count_system_admins(wks_key) == 1:
            return {'code': 400, 'message': "Can not remove only admin in system."}
        current_role = role

    if 'disabled' in body:
        if current_role == 'admin' and count_system_admins(wks_key) == 1 and body['disabled'] == True:
            return {'code': 400, 'message': "Can not disable only admin in system."}

    return resp


def count_system_admins(wks_key):
    return UserProfile.query(UserProfile.Wks == wks_key, UserProfile.role == "admin").count()


def create_skill(wks_key, body):
    resp = {}
    check_duplicate = SkillData.query(SkillData.Wks == wks_key, SkillData.skill_name == body['skill_name']).get()
    if check_duplicate:
        return {'code': 400, 'message': "Skill already exists in this workspace: " + body['skill_name']}

    skill_data = SkillData(
        Wks=wks_key,
        skill_name=body['skill_name']
    ).put()
    resp['SkillID'] = skill_data.id()
    resp["infomation"] = "Skill created successfully."
    return resp


def get_users(wks_key):
    return [dict(user.to_dict(), **dict(ProfileID=user.key.id(), name=user.get_name(), AccountID=user.get_id())) for
            user in
            UserProfile.query(UserProfile.Wks == wks_key).fetch()]


def get_user(wks_key, ProfileID):
    user = UserProfile.get_by_id(ProfileID)
    if user:
        if user.Wks == wks_key:
            return user
        return {'code': 403, 'message': "User (" + str(ProfileID) + ") not part of workspace. Forbidden access."}
    return {'code': 404, 'message': "User not found: " + str(ProfileID)}


def get_task(wks_key, TaskID):
    task = TaskDetails.get_by_id(TaskID)
    if task:
        if task.get_wks() == wks_key:
            return task
        return {'code': 403, 'message': "Task (" + str(TaskID) + ") not part of workspace. Forbidden access."}
    return {'code': 404, 'message': "Task not found: " + str(TaskID)}


def get_tasks(project_key):
    return convert_tasks(TaskDetails.query(TaskDetails.Project == project_key).fetch())


def mandatory(allowed_items, body):
    for item in allowed_items:
        if item not in body or body[item] == "":
            return {'code': 400, 'message': 'Property missing or null provided: ' + item}
    return True


def parse_email(email):
    if re.match("[^@]+@[^@]+\.[^@]+", email):
        return True
    return False


def invite_user(wks, body):
    resp = {}
    key = wks.key
    name = wks.workspace_name
    UserEmail = body['UserEmail']
    role = body['role']

    if parse_email(UserEmail) == False:
        return {'code': 400, 'message': 'Invalid email format provided.'}

    valid_choices = ['admin', 'manager', 'developer']
    if validate_choices(role, valid_choices) == False:
        return {'code': 400, 'message': 'Invalid role provided. Must be one of ' + str(valid_choices)}

    if UserProfile.query(UserProfile.Wks == key, UserProfile.UserEmail == UserEmail).get():
        return {'code': 400, 'message': 'User: ' + UserEmail + ' already invited to this workspace!'}

    token = uuid.uuid4().hex
    user_data = UserProfile(
        Wks=key,
        workspace_name=name,
        UserEmail=UserEmail,
        role=role,
        invitation_token=token,
        invitation_accepted=False,
        disabled=False
    ).put()
    send_invitation_email(token, UserEmail)
    resp['ProfileID'] = user_data.id()
    resp["information"] = 'User: ' + UserEmail + ' invited!'
    return resp


def format_date(date):
    try:
        return datetime.strptime(str(date), '%d/%m/%Y').date()
    except:
        return False


def validate_choices(given, valid_choices):
    if given in valid_choices:
        return True
    return False


def validate_project(body):
    if is_manager(body['project_manager']) == False:
        return {'code': 400, 'message': body['project_manager'] + " is not an active admin or manager."}

    project_start = format_date(body['project_start'])
    project_deadline = format_date(body['project_deadline'])
    if project_start == False or project_deadline == False:
        return {'code': 400, 'message': "Dates must be in dd/mm/YYYY format."}
    if project_start > project_deadline:
        return {'code': 400, 'message': "project_start must be lower than project_deadline."}
    if datetime.today().date() > project_start:
        return {'code': 400, 'message': "project_start must be after or on the current date."}
    if datetime.today().date() > project_deadline:
        return {'code': 400, 'message': "project_deadline must be after or on the current date."}
    return True


def update_project(allowed_items, project, body):
    resp = {}
    old_body = body.copy()
    for item in allowed_items:
        if item not in body:
            body[item] = getattr(project, item)

    if validate_project(body) != True:
        return validate_project(body)

    valid_choices = ['Running', 'Closed', 'On Hold']
    if validate_choices(body['task_status'], valid_choices) == False:
        return {'code': 400, 'message': 'Invalid task_status provided. Must be one of ' + str(valid_choices)}

    for item in body:
        new_value = body[item]
        setattr(project, item, new_value)
    project.put()
    resp["information"] = str(old_body.keys()) + " updated."
    return resp


def create_project(wks_key, body):
    resp = {}
    if validate_project(body) != True:
        return validate_project(body)

    project_data = ProjectDetails(
        Wks=wks_key,
        project_manager=body['project_manager'],
        project_name=body['project_name'],
        project_description=body['project_description'],
        project_start=body['project_start'],
        project_deadline=body['project_deadline'],
        project_status="Running",
        project_stage="Planning"
    ).put()
    resp['ProjectID'] = project_data.id()
    resp["information"] = "Project created successfully."
    return resp


def profile_from_account(wks_key, account_id):
    account = AccountDetails.get_by_id(account_id)
    if account:
        user = UserProfile.query(UserProfile.Wks == wks_key, UserProfile.UserEmail == account.email).get()
        if user:
            return user
        return {'code': 403, 'message': "User (" + str(ProfileID) + ") not part of workspace. Forbidden access."}
    return {'code': 404, 'message': "User not found: " + str(ProfileID)}


def validate_task(wks_key, body):
    skills = body['task_skills']
    for skill_id in skills:
        skill_check = check_skill_exists(wks_key, skill_id)
        if skill_check != True:
            return skill_check

    developers = body['task_developers']
    for account_id in developers:
        profile = profile_from_account(wks_key, account_id)
        if isinstance(profile, dict):
            return profile
        user_check = get_user(wks_key, profile.key.id())
        if isinstance(user_check, dict):
            return user_check
        if user_check.invitation_accepted == False:
            return {'code': 400, 'message': "User has not accepted invite: " + str(account_id)}
        if user_check.disabled == True:
            return {'code': 400, 'message': "User is disabled: " + str(account_id)}
        dev_check = developer_has_skill(wks_key, user_check, skills)
        if dev_check != True:
            return {'code': 400, 'message': "User does not have any of the required skills: " + str(account_id)}

    start = format_date(body['task_startdate'])
    deadline = format_date(body['task_finishbydate'])
    if start == False or deadline == False:
        print start
        print deadline
        return {'code': 400, 'message': "Dates must be in dd/mm/YYYY format."}
    if start > deadline:
        return {'code': 400, 'message': "task_startdate must be lower than task_finishbydate."}
    if datetime.today().date() > start:
        return {'code': 400, 'message': "task_startdate must be after or on the current date."}
    if datetime.today().date() > deadline:
        return {'code': 400, 'message': "task_finishbydate must be after or on the current date."}

    if body['task_aminutes'] <= 0:
        return {'code': 400, 'message': "task_aminutes must be greater than 0."}

    return True


def developer_has_skill(wks_key, user, skill_list):
    for skill in skill_list:
        user_skills = user_has_skill(wks_key, user.get_user_key(), skill)
        if user_skills != False:
            return True
    return False


def user_has_skill(wks_key, account_key, skill_id):
    user_skill = UserSkill.query(UserSkill.Wks == wks_key,
                                 UserSkill.User == account_key,
                                 UserSkill.skill_id == skill_id).get()
    if user_skill:
        return user_skill
    return False


def update_task(allowed_items, key, task, body):
    resp = {}
    old_body = body.copy()
    for item in allowed_items:
        if item not in body:
            if item == 'task_startdate' or item == 'task_finishbydate':
                body[item] = getattr(task, item).strftime('%d/%m/%Y')
            else:
                body[item] = getattr(task, item)

    if validate_task(key, body) != True:
        return validate_task(key, body)

    valid_choices = task.get_all_other_tasks()
    valid_choices.append("None")
    if validate_choices(body['parent_task'], valid_choices) == False:
        return {'code': 400, 'message': 'Invalid parent_task provided. Must be one of ' + str(valid_choices)}

    valid_choices = ['Open', 'Closed']
    if validate_choices(body['task_status'], valid_choices) == False:
        return {'code': 400, 'message': 'Invalid task_status provided. Must be one of ' + str(valid_choices)}

    for item in body:
        if item == 'task_startdate' or item == 'task_finishbydate':
            new_value = format_date(body[item])
        elif item == 'parent_task':
            if body[item] == 'None':
                new_value = None
            else:
                new_value = int(body[item])
        else:
            new_value = body[item]
        setattr(task, item, new_value)
    task.put()
    resp["information"] = str(old_body.keys()) + " updated."
    return resp


def create_task(wks_key, project, body):
    resp = {}
    validation = validate_task(wks_key, body)
    if validation != True:
        return validation

    task_data = TaskDetails(
        Project=project.key,
        task_name=body['task_name'],
        task_description=body['task_description'],
        task_aminutes=body['task_aminutes'],
        task_skills=body['task_skills'],
        task_developers=body['task_developers'],
        task_status="Open",
        task_startdate=format_date(body['task_startdate']),
        task_finishbydate=format_date(body['task_finishbydate'])
    ).put()
    resp['TaskID'] = task_data.id()
    resp["information"] = "Task created successfully."

    return resp


def is_manager(email):
    user = UserProfile.query(UserProfile.UserEmail == email).get()
    if not user:
        return False

    if user.invitation_accepted == True and user.disabled == False and (user.role == "manager" or user.role == "admin"):
        return True
    return False


def convert_string_to_bool(str):
    if str.lower() == "False".lower():
        item = False
    else:
        item = True
    return item


def is_number(number):
    try:
        float(number)
        return True
    except ValueError:
        return False


def is_number_list(number_list):
    try:
        map(int, number_list.split(','))
        return True
    except ValueError:
        return False


def check_body(accepted_items):
    body = request.form
    new_values = {}

    for item in body:
        value = request.form[item]
        if item not in accepted_items:
            return {'code': 400, 'message': 'Invalid key in body found: ' + item}
        # Check data type of accepted item
        elif not isinstance(value, accepted_items[item]):
            if accepted_items[item] == bool and (value.lower() == "false" or value.lower() == "true"):
                new_values[item] = convert_string_to_bool(value)
            elif accepted_items[item] == int and is_number(value):
                new_values[item] = int(value)
            elif accepted_items[item] == int and is_number(value):
                new_values[item] = int(value)
            elif accepted_items[item] == list and is_number_list(value):
                new_values[item] = map(int, value.split(','))
            elif value == "":
                return {'code': 400, 'message': 'Invalid property: ' + item + ', expected: ' + str(
                    accepted_items[item]) + ' found: Null.'}
            else:
                return {'code': 400, 'message': 'Invalid property: ' + item + ', expected: ' + str(
                    accepted_items[item]) + ' found: ' + str(type(value)) + '.'}
        else:
            new_values[item] = value
    return new_values


def check_skill_exists(wks_key, skill_id):
    skill = SkillData.get_by_id(skill_id)
    if skill:
        if skill.Wks == wks_key:
            return True
        return {'code': 403, 'message': "Skill (" + str(skill_id) + ") not part of this workspace. Forbidden access."}
    return {'code': 404, 'message': "Skill not found: " + str(skill_id)}


def assign_skill(wks_key, account, body):
    resp = {}
    rating = body['rating']
    skill_id = body['SkillID']

    skill_check = check_skill_exists(wks_key, skill_id)
    if skill_check != True:
        return skill_check

    if rating < 0 or 5 < rating:
        return {'code': 400, 'message': "Rating must be in range of 0 to 5."}

    if user_has_skill(wks_key, account.get_user_key(), skill_id):
        return {'code': 400, 'message': "User already has this skill."}

    UserSkill(
        Wks=wks_key,
        User=account.get_user_key(),
        skill_id=skill_id,
        skill_rating=rating
    ).put()

    resp["information"] = "Skill added successfully."
    return resp


def update_skill(wks_key, account, body, skill_id):
    resp = {}
    rating = body['rating']

    skill_check = check_skill_exists(wks_key, skill_id)
    if skill_check != True:
        return skill_check

    if rating < 0 or 5 < rating:
        return {'code': 400, 'message': "Rating must be in range of 0 to 5."}

    user_skill = user_has_skill(wks_key, account.get_user_key(), skill_id)
    if user_skill == False:
        return {'code': 400, 'message': "User does not own this skill."}

    user_skill.skill_rating = rating
    user_skill.put()

    resp['id'] = skill_id
    resp['information'] = "Skill updated."
    return resp


def delete_skill(wks_key, account, skill_id):
    resp = {}
    user_skill = user_has_skill(wks_key, account.get_user_key(), int(skill_id))
    if user_skill == False:
        return {'code': 404, 'message': "User does not own this skill."}
    user_skill.key.delete()
    resp['information'] = "Skill deleted."
    return resp


def delete_log(log):
    resp = {}
    log_id = log.key.id()
    task_id = log.task_id
    log = TaskLog.get_by_id(log_id)
    minutes = log.log_minutes
    log.key.delete()
    task = TaskDetails.get_by_id(task_id)
    task.remove_minutes(minutes)
    resp['information'] = "Log deleted."
    return resp

def delete_task(task):
    resp = {}
    task.delete()
    resp['information'] = "Task and logs deleted."
    return resp

def delete_project(project):
    resp = {}
    project.delete()
    resp['information'] = "Project, Task and logs deleted."
    return resp


def convert_tasks(tasks):
    tasks_list = []
    level = 1
    for task in tasks:
        if not task.parent_task:
            tasks_list.append({
                'level': level,
                'TaskID': task.key.id(),
                'task_name': task.task_name,
                'task_aminutes': task.task_aminutes,
                'task_description': task.task_description,
                'task_skills': task.task_skills,
                'task_developers': task.task_developers,
                'task_logged_minutes': task.task_logged_minutes,
                'task_startdate': task.task_startdate,
                'task_finishbydate': task.task_finishbydate,
                'task_status': task.task_status,
                'children': get_children(task.key.id(), tasks, level)
            })
            level = level + 1
    return tasks_list


def get_children(parent_id, tasks, level):
    data = []
    sublevel = 1
    for task in tasks:
        if task.parent_task == parent_id:
            data.append({
                'level': str(level) + "." + str(sublevel),
                'TaskID': task.key.id(),
                'task_name': task.task_name,
                'task_aminutes': task.task_aminutes,
                'task_description': task.task_description,
                'task_skills': task.task_skills,
                'task_developers': task.task_developers,
                'task_logged_minutes': task.task_logged_minutes,
                'task_startdate': task.task_startdate,
                'task_finishbydate': task.task_finishbydate,
                'task_status': task.task_status,
                'children': get_children(task.key.id(), tasks, str(level) + "." + str(sublevel))
            })
            sublevel = sublevel + 1
    return data


def validate_log(task, body):
    if validate_choices(body['log_developer'], task.task_developers) == False:
        return {'code': 400, 'message': 'Invalid developer provided. Must be one of ' + str(task.task_developers)}

    if body['log_minutes'] <= 0:
        return {'code': 400, 'message': "log_minutes must be greater than 0."}

    return True

def update_log(allowed_items,log,body):
    resp = {}
    old_body = body.copy()
    task = TaskDetails.get_by_id(log.task_id)
    for item in allowed_items:
        if item not in body:
            body[item] = getattr(log, item)

    validation = validate_log(task, body)
    if validation != True:
        return validation

    for item in body:
        new_value = body[item]
        setattr(log, item, new_value)
        task.put()
    resp["information"] = str(old_body.keys()) + " updated."

    return resp


def create_log(task, body):
    resp = {}
    validation = validate_log(task, body)
    if validation != True:
        return validation

    log_data = TaskLog(
        task_id=task.key.id(),
        log_developer=body['log_developer'],
        log_minutes=body['log_minutes'],
        log_comments=body['log_comments'],
        log_time=datetime.now() + timedelta(hours=1)
    )
    log_data.update_total()
    resp['LogID'] = log_data.put().id()
    resp["information"] = "Log created successfully."
    return resp

def get_logs(task_id):
    return [dict(log.to_dict(), **dict(LogID=log.key.id(), developer_name=log.get_username())) for log
            in TaskLog.query(TaskLog.task_id == task_id).order(TaskLog.log_time).fetch()]

def get_log(wks_key,logid):
    log = TaskLog.get_by_id(logid)
    if log:
        task = TaskDetails.get_by_id(log.task_id)
        if task.get_wks() == wks_key:
            return log
        return {'code': 403, 'message': "Log (" + str(logid) + ") not part of workspace. Forbidden access."}
    return {'code': 404, 'message': "Log not found: " + str(logid)}


def valid_url(url):
    try:
        urlopen(url)
        return True
    except:
        return {'code': 400, 'message': "Webhook URL invalid"}