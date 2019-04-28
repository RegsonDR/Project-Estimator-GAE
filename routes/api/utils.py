from models import AccountDetails, ProjectChat, TaskLog, UserProfile, UserSkill, TaskDetails, ProjectDetails, \
    WorkspaceDetails
from flask import request, jsonify
from google.appengine.api import mail, urlfetch
from app_statics import APP_NAME
from datetime import datetime, timedelta
import uuid
import base64
import hmac
import hashlib
import json
import time


def return_json(data, message=None):
    response = {}
    if message:
        response['message'] = message
    response['data'] = data
    response['code'] = 200

    return jsonify(response)
def get_workspace(wk_id):
    return WorkspaceDetails.get_by_id(wk_id)
def get_all_projects(wks_key):
    return [dict(project.to_dict(), **dict(id=project.key.id())) for project in
            ProjectDetails.query(ProjectDetails.Wks == wks_key).fetch()]
def get_project(wks_key, project_id):
    project = ProjectDetails.get_by_id(project_id)
    if project:
        if project.Wks == wks_key:
            return wk.to_dict()
        return {'code': 403, 'message': "You don't have access to this project. Forbidden access."}
    return {'code': 404, 'message': "Project not found."}


def get_tasks(wks_key, project_key):
    return [dict(task.to_dict(), **dict(id=task.key.id())) for task in
            TaskDetails.query(TaskDetails.Project == project_key).fetch()]

def mandatory(allowed_items, body):
    for item in allowed_items:
        if item not in body or body[item] == "":
            return {'code': 400, 'message': 'Property missing or null provided: ' + item}
    return True
def format_data(date):
    try:
        return datetime.strptime(str(date), '%d/%m/%Y').date()
    except:
        return False
def validate_choices(given, valid_choices):
    if given in valid_choices:
        return True
    return False


def create_project(wks_key, body):
    resp = {}
    if is_manager(body['project_manager']) == False:
        return {'code': 400, 'message': body['project_manager'] + " is not an active admin or manager."}

    project_start = format_data(body['project_start'])
    project_deadline = format_data(body['project_deadline'])
    if project_start == False or project_deadline == False:
        return {'code': 400, 'message': "Dates must be in dd/mm/YYYY format."}

    if project_start > project_deadline:
        return {'code': 400, 'message': "project_start must be lower than project_deadline."}

    if datetime.today().date() > project_start:
        return {'code': 400, 'message': "project_start must be after or on the current date."}

    if datetime.today().date() > project_deadline:
        return {'code': 400, 'message': "project_deadline must be after or on the current date."}

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
    resp['id'] = project_data.id()
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
def check_body(accepted_items):
    body = request.form
    new_values = {}

    for item in body:
        value = request.form[item]
        if item not in accepted_items:
            return {'code': 400, 'message': 'Invalid key in body found: ' + item}
        # Check data type of accepted item
        elif not isinstance(value, accepted_items[item]):
            print value
            if accepted_items[item] == bool and type(value) == unicode and (
                    value.lower() == "false" or value.lower() == "true"):
                new_values[item] = convert_string_to_bool(request.form[item])
            elif value == "":
                return {'code': 400, 'message': 'Invalid property: ' + item + ', expected: ' + str(
                    accepted_items[item]) + ' found: Null.'}
            else:
                return {'code': 400, 'message': 'Invalid property: ' + item + ', expected: ' + str(
                    accepted_items[item]) + ' found: ' + str(type(value)) + '.'}
        else:
            new_values[item] = value
    return new_values
