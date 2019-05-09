from flask import Blueprint, jsonify, request
from models import *
from routes.api.utils import *
from functools import wraps

api = Blueprint('api', __name__, url_prefix='/api/')


class user_api_request:
    def __init__(self, workspace_data):
        self.workspace_data = workspace_data

    def get_workspace(self):
        return self.workspace_data

    def get_all_workspace_projects(self):
        return get_all_workspace_projects(self.workspace_data.key)


def auth_request():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not request.authorization or not request.authorization['username'] or not request.authorization['password']:
                return jsonify(
                    {"code": 400, "message": "Your username is your Workspace ID and your password is your api key."})
            wks_id = int(request.authorization['username'])
            api_key = request.authorization['password']
            workspace_data = get_workspace(wks_id)
            if not workspace_data or workspace_data.api_key != api_key:
                return jsonify({"code": 401, "message": "Invalid Credentials."})
            if not workspace_data.enable_api:
                return jsonify({"code": 401, "message": "API access disabled by your workspace administrator."})
            return func(user_api_request(workspace_data), *args, **kwargs)
        return wrapper
    return decorator


@api.route('/Workspace', methods=['GET', 'PUT'])
@auth_request()
def workspace(api_request, **kwargs):
    message = None
    workspace_data = api_request.get_workspace()
    if request.method == 'PUT':
        allowed_items = {'allow_dev_skills': bool, 'workspace_name': unicode, 'webhook_url': unicode,
                         'enable_webhook': bool}
        body = check_body(allowed_items)
        if 'code' in body:
            return jsonify(body)
        for item in body:
            if item == 'webhook_url':
                if valid_url(body[item]) != True:
                    return jsonify(valid_url(body[item]))
            new_value = body[item]
            setattr(workspace_data, item, new_value)
        workspace_data.put()

        message = {"information": str(body.keys()) + " updated."}

    response = workspace_data.to_dict()
    del response['api_key']
    del response['enable_api']

    return return_json(response, message)


@api.route('/Skills', methods=['GET', 'POST'])
@auth_request()
def skills(api_request, **kwargs):
    message = None
    if request.method == 'POST':
        allowed_items = {'skill_name': unicode}
        body = check_body(allowed_items)
        if 'code' in body:
            return jsonify(body)
        contains_all = mandatory(allowed_items, body)
        if contains_all != True:
            return jsonify(contains_all)
        create = create_skill(api_request.workspace_data.key, body)
        if 'code' in create:
            return jsonify(create)
        message = create

    response = get_skills(api_request.workspace_data.key)
    for item in response:
        del item['Wks']
    return return_json(response, message)


@api.route('/Users', methods=['GET', 'POST'])
@auth_request()
def users(api_request, **kwargs):
    message = None
    if request.method == 'POST':
        allowed_items = {'UserEmail': unicode, 'role': unicode}
        body = check_body(allowed_items)
        if 'code' in body:
            return jsonify(body)
        contains_all = mandatory(allowed_items, body)
        if contains_all != True:
            return jsonify(contains_all)
        create = invite_user(api_request.workspace_data, body)
        if 'code' in create:
            return jsonify(create)
        message = create

    response = get_users(api_request.workspace_data.key)
    for item in response:
        del item['Wks']
        del item["workspace_name"]

    return return_json(response, message)


@api.route('/Projects', methods=['GET', 'POST'])
@auth_request()
def projects(api_request, **kwargs):
    message = None
    if request.method == 'POST':
        allowed_items = {'project_deadline': unicode, 'project_description': unicode, 'project_manager': unicode,
                         'project_name': unicode, 'project_start': unicode}
        body = check_body(allowed_items)
        if 'code' in body:
            return jsonify(body)
        contains_all = mandatory(allowed_items, body)
        if contains_all != True:
            return jsonify(contains_all)
        create = create_project(api_request.workspace_data.key, body)
        if 'code' in create:
            return jsonify(create)
        message = create

    response = api_request.get_all_workspace_projects()
    for item in response:
        del item['Wks']

    return return_json(response, message)


@api.route('/User/<int:ProfileID>', methods=['GET', 'PUT'])
@auth_request()
def user_profile(api_request, ProfileID, **kwargs):
    message = None
    user = get_user(api_request.workspace_data.key, ProfileID)
    if isinstance(user, dict):
        return jsonify(user)
    if request.method == 'PUT':
        allowed_items = {'disabled': bool, 'role': unicode}
        body = check_body(allowed_items)
        if 'code' in body:
            return jsonify(body)
        update = validate_profile_update(api_request.workspace_data.key, user.role, body)
        if 'code' in update:
            return jsonify(update)
        for item in body:
            new_value = body[item]
            setattr(user, item, new_value)
        user.put()
        message = {"information": str(body.keys()) + " updated."}

    response = user.to_dict()
    response['AccountID'] = user.get_id()
    del response['Wks']
    del response['workspace_name']
    account = get_account(ProfileID)
    if account.get_user_key() == False:
        return jsonify({'code': 400, 'message': 'User does not have an account.'})
    response['skills'] = get_user_skill(api_request.workspace_data.key, account.get_user_key())
    for item in response['skills']:
        del item['Wks']
        del item['User']
        item['SkillID'] = item['skill_id']
        del item['skill_id']

    response['projects'] = get_user_projects(api_request.workspace_data.key, ProfileID)
    for item in response['projects']:
        del item['Wks']

    return return_json(response, message)


@api.route('/User/<int:ProfileID>/Skill', methods=['POST'])
@auth_request()
def new_skill(api_request, ProfileID, **kwargs):
    response = {}
    message = None
    account = get_account(ProfileID)
    user = get_user(api_request.workspace_data.key, ProfileID)
    if isinstance(user, dict):
        return jsonify(user)

    if request.method == 'POST':
        allowed_items = {'SkillID': int, 'rating': int}
        body = check_body(allowed_items)
        if 'code' in body:
            return jsonify(body)
        contains_all = mandatory(allowed_items, body)
        if contains_all != True:
            return jsonify(contains_all)
        create = assign_skill(api_request.workspace_data.key, account, body)
        if 'code' in create:
            return jsonify(create)
        message = create
    return return_json(response, message)


@api.route('/User/<int:ProfileID>/Skill/<int:SkillID>', methods=['PUT', 'DELETE'])
@auth_request()
def user_skills(api_request, ProfileID, SkillID, **kwargs):
    response = {}
    message = None
    account = get_account(ProfileID)
    user = get_user(api_request.workspace_data.key, ProfileID)
    if isinstance(user, dict):
        return jsonify(user)

    if request.method == 'DELETE':
        delete = delete_skill(api_request.workspace_data.key, account, SkillID)
        if 'code' in delete:
            return jsonify(delete)
        message = delete

    if request.method == 'PUT':
        allowed_items = {'rating': int}
        body = check_body(allowed_items)
        if 'code' in body:
            return jsonify(body)
        contains_all = mandatory(allowed_items, body)
        if contains_all != True:
            return jsonify(contains_all)
        update = update_skill(api_request.workspace_data.key, account, body, SkillID)
        if 'code' in update:
            return jsonify(update)
        message = update

    return return_json(response, message)


@api.route('/Project/<int:ProjectID>', methods=['GET', 'PUT', 'DELETE'])
@auth_request()
def project(api_request, ProjectID, **kwargs):
    message = None
    project = get_project(api_request.workspace_data.key, ProjectID)
    if isinstance(project, dict):
        return jsonify(project)
    if request.method == 'PUT':
        allowed_items = {'project_deadline': unicode, 'project_description': unicode, 'project_manager': unicode,
                         'project_name': unicode, 'project_start': unicode, 'project_stage': unicode,
                         'project_status': unicode}
        body = check_body(allowed_items)
        if 'code' in body:
            return jsonify(body)
        update = update_project(allowed_items, project, body)
        if 'code' in update:
            return jsonify(update)
        message = update

    response = project.to_dict()
    response['Developers'] = project.get_developers()
    response['Prediction'] = project.predict(project.project_function_points)
    del response['Wks']
    response['Tasks'] = get_tasks(project.key)
    if request.method == 'DELETE':
        message = delete_project(project)
        response = {}

    return return_json(response, message)


@api.route('/Project/<int:ProjectID>/Task', methods=['POST'])
@auth_request()
def project_tasks(api_request, ProjectID, **kwargs):
    response = {}
    message = None
    project = get_project(api_request.workspace_data.key, ProjectID)
    if isinstance(project, dict):
        return jsonify(project)

    if request.method == 'POST':
        allowed_items = {'task_name': unicode, 'task_description': unicode, 'task_aminutes': int,
                         'task_skills': list, 'task_developers': list, 'task_startdate': unicode,
                         'task_finishbydate': unicode}
        body = check_body(allowed_items)
        if 'code' in body:
            return jsonify(body)
        contains_all = mandatory(allowed_items, body)
        if contains_all != True:
            return jsonify(contains_all)
        create = create_task(api_request.workspace_data.key, project, body)
        if 'code' in create:
            return jsonify(create)
        message = create

    return return_json(response, message)


@api.route('/Task/<int:TaskID>', methods=['GET', 'PUT', 'DELETE'])
@auth_request()
def task(api_request, TaskID, **kwargs):
    message = None
    task = get_task(api_request.workspace_data.key, TaskID)
    if isinstance(task, dict):
        return jsonify(task)

    if request.method == 'PUT':
        allowed_items = {'task_name': unicode, 'task_description': unicode, 'task_aminutes': int,
                         'task_skills': list, 'task_developers': list, 'task_startdate': unicode,
                         'task_finishbydate': unicode, 'parent_task': unicode, 'task_status': unicode}
        body = check_body(allowed_items)
        if 'code' in body:
            return jsonify(body)
        update = update_task(allowed_items, api_request.workspace_data.key, task, body)
        if 'code' in update:
            return jsonify(update)
        message = update

    response = task.to_dict()
    del response['Project']
    response['Logs'] = get_logs(task.key.id())
    if request.method == 'DELETE':
        message = delete_task(task)
        response = {}

    return return_json(response, message)


@api.route('/Task/<int:TaskID>/Log', methods=['POST'])
@auth_request()
def new_log(api_request, TaskID, **kwargs):
    response = {}
    message = None
    task = get_task(api_request.workspace_data.key, TaskID)
    if isinstance(task, dict):
        return jsonify(task)
    if request.method == 'POST':
        allowed_items = {'log_developer': int, 'log_minutes': int, 'log_comments': unicode}
        body = check_body(allowed_items)
        if 'code' in body:
            return jsonify(body)
        contains_all = mandatory(allowed_items, body)
        if contains_all != True:
            return jsonify(contains_all)
        create = create_log(task, body)
        if 'code' in create:
            return jsonify(create)
        message = create

    return return_json(response, message)


@api.route('/Log/<int:LogID>', methods=['PUT', 'DELETE'])
@auth_request()
def log(api_request, LogID, **kwargs):
    response = {}
    message = None
    log = get_log(api_request.workspace_data.key, LogID)
    if isinstance(log, dict):
        return jsonify(task)
    if request.method == 'DELETE':
        message = delete_log(log)

    if request.method == 'PUT':
        allowed_items = {'log_developer': int, 'log_minutes': int, 'log_comments': unicode}
        body = check_body(allowed_items)
        if 'code' in body:
            return jsonify(body)
        update = update_log(allowed_items, log, body)
        if 'code' in update:
            return jsonify(update)
        message = update
        response = log.to_dict()
        response['developer_name '] = log.get_username()

    return return_json(response, message)
