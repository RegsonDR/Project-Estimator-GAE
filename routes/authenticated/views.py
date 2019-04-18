# coding=utf-8
from flask import Blueprint, session, flash, abort, redirect, url_for, render_template, request, jsonify
from forms import *
from werkzeug.security import generate_password_hash
from routes.authenticated.utils import *
from models import AccountDetails
from app_statics import SIDEBAR
from functools import wraps
import time
import gc
import json

authenticated = Blueprint('authenticated', __name__, template_folder='templates')


class Vividict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()  # retain local pointer to value
        return value  # faster to return than dict lookup


class LoggedUser:
    def __init__(self, user_data, user_email, wks_data=None, projects_data=None, access_data=None):
        self.user_data = user_data
        self.user_key = user_data.key
        self.user_email = user_email

        if wks_data:
            self.wks_data = wks_data
            self.wks_key = wks_data.key
        if access_data:
            self.access_data = access_data
            self.access_key = access_data.key
        if projects_data:
            self.projects_data = projects_data

    def get_user_data(self):
        return self.user_data

    def get_wks_data(self):
        return self.wks_data

    def get_tasks_data_by_project_id(self, project_id):
        return project_id

    def get_role(self):
        return self.access_data.role

    def get_permitted_workspaces(self):
        return get_workspaces(self.user_email)

    def get_projects(self, project_status):
        return get_projects(self.wks_key, self.get_role(), self.user_email, project_status)

    def get_open_task_number(self, project_key):
        return get_open_task_number(project_key)

    def get_total_task_number(self, project_key):
        return get_total_task_number(project_key)

    def get_all_users(self):
        return get_all_users(self.wks_key)


# Permissions decorator, used and re-checked on every page load, first check login, account active, then workspace + role.
def login_required(roles=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if session.get('Logged_In', False):
                user_data = get_user_data_by_email(session.get('Email'))
                #
                # Check if account is active
                if not user_data.is_active:
                    session.clear()
                    gc.collect()
                    flash('Your account is no longer active.', 'danger')
                    return redirect(url_for('unauthenticated.login_page'))
                #
                wks_data = None
                projects_data = None
                access_data = None
                if kwargs and kwargs['wks_id']:
                    wks_data = get_wks_data_by_id(kwargs['wks_id'])
                    if not wks_data:
                        abort(403)
                    access_data = check_access(wks_data.key, session.get('Email'))
                    # Check Permissions for workspace
                    if not access_data and not roles or access_data.role not in roles:
                        abort(403)
                    # Check Permission for page
                    # if kwargs['project_id']:

                kwargs['user'] = LoggedUser(user_data, session.get('Email'), wks_data, projects_data, access_data)
            else:
                flash('Please login to access the requested page.', 'danger')
                abort(401)
            return func(*args, **kwargs)

        return wrapper

    return decorator


@authenticated.route('/')
@authenticated.route('/Workspaces', methods=['GET', 'POST'])
@login_required()
def my_workspaces_page(**kwargs):
    new_wks = NewWorkspace()
    if request.method == 'POST':
        if new_wks.validate_on_submit():
            wks_id = create_wks(new_wks.workspace_name.data, kwargs['user'].user_email)
            if wks_id:
                time.sleep(1)
                return redirect(url_for('authenticated.workspace_homepage', wks_id=wks_id.key.id()))

    return render_template('authenticated/html/my_workspaces_page.html',
                           form=new_wks,
                           user_data=kwargs['user'])

@authenticated.route('/MyProfile', methods=['GET', 'POST'])
@login_required('admin')
def my_profile_page(**kwargs):
    user_profile = ProfileUser()

    user_data = kwargs['user'].get_user_data()
    if request.method == "POST" and user_profile.validate_on_submit():
        if user_profile.first_name.data and user_profile.first_name.data is not user_data.first_name:
            user_data.first_name = user_profile.first_name.data
        if user_profile.last_name.data and user_profile.last_name.data is not user_data.last_name:
            user_data.last_name = user_profile.last_name.data
        if user_profile.email.data and user_profile.email.data is not user_data.email:
            user_data.change_email(user_profile.email.data)
            session['Email'] = user_profile.email.data
        if user_profile.password.data and user_profile.password.data is not user_data.password:
            user_data.password = generate_password_hash(user_profile.password.data)
        if user_profile.mobile_number.data and user_profile.mobile_number.data is not user_data.mobile_number:
            user_data.mobile_number = user_profile.mobile_number.data
        if user_data.put():
            flash('Profile updated!','success')
            return redirect(url_for('authenticated.my_profile_page'))
        flash('Error occurred, please try again!', 'danger')

    user_profile.first_name.data = user_data.first_name
    user_profile.last_name.data = user_data.last_name
    user_profile.email.data = user_data.email
    user_profile.mobile_number.data = user_data.mobile_number


    return render_template('authenticated/html/my_profile_page.html',
                           form=user_profile,
                           user_data=kwargs['user'])


@authenticated.route('/Workspace/<int:wks_id>/Projects', methods=['GET', 'POST'])
@authenticated.route('/Workspace/<int:wks_id>', methods=['GET', 'POST'])
@login_required({'admin', 'manager'})
def workspace_homepage(wks_id, **kwargs):
    # # todo: create projects on front end
    # print kwargs['user'].get_projects()

    return render_template('authenticated/html/workspace_homepage.html',
                           user_data=kwargs['user'],
                           wks_data=kwargs['user'].get_wks_data(),
                           SIDEBAR=SIDEBAR)


@authenticated.route('/Workspace/<int:wks_id>/NewProject', methods=['GET', 'POST'])
@login_required('admin')
def new_project_page(wks_id, **kwargs):
    new_project = NewProject()

    if request.method == 'POST':
        if new_project.validate_on_submit():
            project_data = Vividict()
            taskid_list = []
            # Get all data
            for key in request.form.keys():
                # Extract ID
                component = [p[:-1] for p in key.split('[')][1:]
                if len(component) is 0:
                    project_data[key] = request.form[key]
                else:
                    task_id = component[0]
                    element = component[1]

                    if task_id not in taskid_list:
                        taskid_list.extend(task_id)
                    dic_position = taskid_list.index(task_id)

                    if element == "Skills" or element == "Developers":
                        project_data['Task'][dic_position][element] = request.form.getlist(
                            'Task[' + task_id + '][' + element + ']')
                    else:
                        project_data['Task'][dic_position][element] = request.form[
                            'Task[' + task_id + '][' + element + ']']
            project_id = create_project(kwargs['user'].wks_key, kwargs['user'].user_email, project_data)
            return redirect(url_for('authenticated.workspace_homepage', wks_id=wks_id))

    return render_template('authenticated/html/new_project_page.html',
                           form=new_project,
                           user_data=kwargs['user'],
                           wks_data=kwargs['user'].get_wks_data(),
                           SIDEBAR=SIDEBAR)


@authenticated.route('/Workspace/<int:wks_id>/Project/<int:project_id>', methods=['GET', 'POST'])
@login_required('admin')
def view_project_page(wks_id, project_id, **kwargs):
    return render_template('authenticated/html/view_project_page.html',
                           user_data=kwargs['user'],
                           wks_data=kwargs['user'].get_wks_data(),
                           project_data=get_project_data_by_id(project_id),
                           SIDEBAR=SIDEBAR)


@authenticated.route('/Workspace/<int:wks_id>/AddUsers', methods=['GET', 'POST'])
@login_required('admin')
def add_users_page(wks_id, **kwargs):
    new_user = NewUser()
    if request.method == "POST" and new_user.validate_on_submit():
        if add_user(kwargs['user'].wks_key, kwargs['user'].get_wks_data().workspace_name, new_user.user_email.data,
                    new_user.role.data):
            return redirect(url_for('authenticated.add_users_page', wks_id=wks_id))

    return render_template('authenticated/html/add_users_page.html',
                           form=new_user,
                           user_data=kwargs['user'],
                           wks_data=kwargs['user'].get_wks_data(),
                           SIDEBAR=SIDEBAR)


@authenticated.route('/Invitation', methods=['GET', 'POST'])
@login_required('admin')
def open_invitation(**kwargs):
    code = request.args.get('code')
    email = request.args.get('email')
    if not email or not code:
        return redirect(url_for('authenticated.my_workspaces_page'))

    if not verify_invite(code, email):
        return redirect(url_for('authenticated.my_workspaces_page'))

    if request.method == "POST":
        if request.form['accepted']:
            verify_invite(code, email).invitation_accepted = True
            verify_invite(code, email).put()
            flash('Invitation accepted! You can access your new workspace now!', 'success')
            return redirect(url_for('authenticated.my_workspaces_page'))

    return render_template('authenticated/html/open_invitation.html',
                           user_data=kwargs['user'],
                           wks_data=verify_invite(code, email)
                           )


@authenticated.route('/Logout')
def logout():
    session.clear()
    gc.collect()
    flash("Successfully Logged Out!", "success")
    return redirect(url_for('unauthenticated.login_page'))


@authenticated.route('/debug', methods=['GET', 'POST'])
def debug(**kwargs):
    return render_template('authenticated/html/Blank.html')
