from flask import Blueprint, session, flash, abort, redirect, url_for, render_template, request
from forms import NewWorkspace, NewProject
from routes.authenticated.utils import *
from models import AccountDetails
from app_statics import SIDEBAR
from functools import wraps
import time
import gc

authenticated = Blueprint('authenticated', __name__, template_folder='templates')


class LoggedUser:
    def __init__(self, user_data, wks_data=None, access_data=None):
        self.user_data = user_data
        self.user_key = user_data.key

        if wks_data:
            self.wks_data = wks_data
            self.wks_key = wks_data.key
        if access_data:
            self.access_data = access_data
            self.access_key = access_data.key

    def get_user_data(self):
        return self.user_data

    def get_wks_data(self):
        return self.wks_data

    def get_role(self):
        return self.access_data.role

    def get_permitted_workspaces(self):
        return get_workspaces(self.user_key)

    def get_projects(self, project_status):
        return get_projects(self.wks_key, project_status)


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
                access_data = None
                if kwargs and kwargs['wks_id']:
                    wks_data = get_wks_data_by_id(kwargs['wks_id'])
                    if not wks_data:
                        abort(403)
                    access_data = check_access(wks_data.key, user_data.key)
                    # Check Permissions
                    if not access_data and not roles and access_data.role not in roles:
                        abort(403)

                kwargs['user'] = LoggedUser(user_data, wks_data, access_data)
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
            wks_id = create_wks(new_wks.workspace_name.data, kwargs['user'].user_key)
            if wks_id:
                time.sleep(1)
                return redirect(url_for('authenticated.workspace_homepage', wks_id=wks_id.key.id()))

    return render_template('authenticated/html/my_workspaces_page.html',
                           form=new_wks,
                           user_data=kwargs['user'])


@authenticated.route('/Workspace/<int:wks_id>/Projects', methods=['GET', 'POST'])
@login_required('super-admin')
def workspace_homepage(wks_id, **kwargs):
    # # todo: create projects on front end
    # print kwargs['user'].get_projects()

    return render_template('authenticated/html/workspace_homepage.html',
                           user_data=kwargs['user'],
                           wks_data=kwargs['user'].get_wks_data(),
                           SIDEBAR=SIDEBAR)


@authenticated.route('/Workspace/<int:wks_id>/NewProject', methods=['GET', 'POST'])
@login_required('super-admin')
def new_project_page(wks_id, **kwargs):
    new_project = NewProject()

    if request.method == 'POST' and new_project.validate_on_submit():
        project_id = create_project(kwargs['user'].wks_key,new_project.project_name.data,new_project.project_description.data)
        if project_id:
            return redirect(url_for('authenticated.workspace_homepage', wks_id=wks_id))

    return render_template('authenticated/html/new_project_page.html',
                           form=new_project,
                           user_data=kwargs['user'],
                           wks_data=kwargs['user'].get_wks_data(),
                           SIDEBAR=SIDEBAR)


@authenticated.route('/Workspace/<int:wks_id>/Project/<int:project_id>', methods=['GET', 'POST'])
@login_required('super-admin')
# check permission
def view_project_page(wks_id, project_id,**kwargs):
    return "sfdsfds"


@authenticated.route('/Logout')
def logout():
    session.clear()
    gc.collect()
    flash("Successfully Logged Out!", "success")
    return redirect(url_for('unauthenticated.login_page'))

# @authenticated.route('/debug')
# def debug():
#     flash('fsa fasdfasd fdsa fasdfas fdas  fasllo','danger')
#
#     return render_template('authenticated/html/Blank.html',
#                            page_title="Dashboard")
