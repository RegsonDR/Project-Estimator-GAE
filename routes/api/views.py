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

    def get_all_projects(self):
        return get_all_projects(self.workspace_data.key)


def auth_request():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not request.authorization or not request.authorization['username'] or not request.authorization[
                'password']:
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
    if request.method == 'PUT' and request.form:
        allowed_items = {'allow_dev_skills': bool, 'workspace_name': unicode}
        body = check_body(allowed_items)
        if 'code' in body:
            return jsonify(body)
        workspace_data = api_request.get_workspace()
        for item in body:
            new_value = body[item]
            setattr(workspace_data, item, new_value)
        workspace_data.put()
        response = workspace_data.to_dict()
        message = "Workspace updated."

    # This is get
    else:
        response = api_request.get_workspace().to_dict()

    del response['api_key']
    del response['enable_api']

    return return_json(response, message)


@api.route('/Projects', methods=['GET', 'POST'])
@auth_request()
def projects(api_request, **kwargs):
    message = None
    if request.method == 'POST' and request.form:
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
        message = ["Project created", create]

    response = api_request.get_all_projects()
    for item in response:
        del item['Wks']

    return return_json(response, message)

@api.route('/Project/<int:project_id>', methods=['GET', 'PUT', 'DELETE'])
@auth_request()
def project(api_request, project_id, **kwargs):
    message = None
    response = {}

    response = get_project(api_request.workspace_data.key,project_id)


    return return_json(response, message)
