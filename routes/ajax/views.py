from flask import Blueprint, jsonify, session
from routes.ajax.utils import *
from datetime import datetime, timedelta
from routes.authenticated.views import login_required
from routes.webhook.utils import call_webhook
import pytz

ajax = Blueprint('ajax', __name__, url_prefix='/ajax', template_folder='templates')


@ajax.route('/ResetPassword', methods=['POST'])
def reset_password_email():
    email = request.form.get('reset_email')
    return jsonify({"Request": send_reset_email(email)})


@ajax.route('/Project/<int:project_id>/Task/Delete', methods=['POST'])
@login_required({'admin', 'manager'})
def delete_projects(project_id, **kwargs):
    try:
        delete_project(project_id)
        return jsonify({'Request': True})
    except:
        return jsonify({'Request': False})


@ajax.route('/Project/<int:project_id>/Task/Create', methods=['POST'])
@login_required({'admin', 'manager'})
def new_tasks(project_id, **kwargs):
    try:
        Title = request.form.get('title')
        aMinutes = request.form.get('aMinutes')
        start = request.form.get('start')
        finish =  request.form.get('finish')
        Description = request.form.get('description')
        Skills = request.form.getlist('skills[]')
        Developers = request.form.getlist('developers[]')
        create_task(project_id, Title, aMinutes, start, finish, Description, Skills, Developers)
        return jsonify({'Request': True})
    except:
        return jsonify({'Request': False})

@ajax.route('/Task/<int:task_id>/Delete', methods=['POST'])
@login_required({'admin', 'manager'})
def delete_tasks(task_id, **kwargs):
    try:
        delete_task(int(task_id))
        return jsonify({'Request': True})
    except:
        return jsonify({'Request': False})

@ajax.route('/Task/<int:task_id>/Log/Save', methods=['POST'])
@login_required({'admin', 'manager', 'developer'})
def save_logs(task_id, **kwargs):
    try:
        log_developer = session.get("Email")
        log_minutes = int(request.form.get('minutes'))
        log_comments = request.form.get('comments')
        save_log(task_id, log_developer, log_minutes, log_comments)
        return jsonify({'Request': True})
    except:
        return jsonify({'Request': False})

@ajax.route('/Task/<int:task_id>/Log/Delete', methods=['POST'])
@login_required({'admin', 'manager'})
def delete_logs(task_id, **kwargs):
    try:
        log_id = request.form.get('log-id')
        delete_log(task_id,int(log_id))
        return jsonify({'Request': True})
    except:
        return jsonify({'Request': False})

@ajax.route('/Workspace/<int:wks_id>/User/Status/Update', methods=['POST'])
@login_required('admin')
def switch_account_status(wks_id, **kwargs):
    try:
        email = request.form.get('email')
        account_switch(kwargs['user'].wks_data.key, email)
        return jsonify({'Request': True})
    except:
        return jsonify({'Request': False})

@ajax.route('/Workspace/<int:wks_id>/User/Role/Update', methods=['POST'])
@login_required('admin')
def change_role(wks_id, **kwargs):
    try:
        email = request.form.get('email')
        new_role = request.form.get('role')
        change_user_role(kwargs['user'].wks_data.key, email, new_role)
        return jsonify({'Request': True})
    except:
        return jsonify({'Request': False})

@ajax.route('/Workspace/<int:wks_id>/Skill/Update', methods=['POST'])
@login_required({'admin', 'manager', 'developer'})
def alter_skill(wks_id, **kwargs):
    try:
        skill_id = int(request.form.get('skill_id'))
        rating = request.form.get('rating')
        update_user_skill(skill_id, rating)
        return jsonify({'Request': True})
    except:
        return jsonify({'Request': False})

@ajax.route('/Project/<int:project_id>/Chat', methods=['POST'])
@login_required({'admin', 'manager', 'developer'})
def chat_message(project_id, **kwargs):
    try:
        username = request.form.get('username')
        message = base64.b64encode(request.form.get('message').decode('utf-8'))
        message_time = datetime.now() + timedelta(hours=1)
        email = request.form.get('email')
        role = request.form.get('role')
        log_message(project_id, username, message, message_time, email, role)
        push_chat_message(project_id, username, message, message_time, email, role)
        return jsonify({'Request': True})
    except:
        return jsonify({'Request': False})

@ajax.route('/Workspace/<int:wks_id>/Regenerate', methods=['POST'])
@login_required({'admin'})
def regenerate_token(wks_id, **kwargs):
    try:
        currentAuth = request.form.get('currentAuth')
        regenerate(wks_id,currentAuth)
        return jsonify({'Request': True})
    except:
        return jsonify({'Request': False})

@ajax.route('/Workspace/<int:wks_id>/Trigger', methods=['POST'])
@login_required({'admin'})
def trigger_webhook(wks_id, **kwargs):
    try:
        call_webhook(wks_id, request.form.get('testURL'))
        return jsonify({'Request': True})
    except:
        return jsonify({'Request': False})


@ajax.route('/Workspace/<int:wks_id>/ML', methods=['POST'])
@login_required({'admin'})
def machine_learning(wks_id, **kwargs):
    try:
        trigger_ml(wks_id, request.form.get('action'))
        return jsonify({'Request': True})
    except:
        return jsonify({'Request': False})
