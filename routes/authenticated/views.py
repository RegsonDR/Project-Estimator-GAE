from flask import Blueprint, session, flash, abort, redirect, url_for, render_template, request
from forms import NewOrganisation, NewProject
from models import AccountDetails
from app_statics import SIDEBAR
from routes.authenticated.utils import create_org, get_user_data_by_email, get_user_data_by_id, check_access, \
    get_org_data_by_id, get_organizations, create_project, get_projects
from functools import wraps
import gc
import time

authenticated = Blueprint('authenticated', __name__, template_folder='templates')


class LoggedUser:
    def __init__(self, user_data, org_data=None, access_data=None):
        self.user_data = user_data
        self.user_key = user_data.key

        if org_data:
            self.org_data = org_data
            self.org_key = org_data.key
        if access_data:
            self.access_data = access_data
            self.access_key = access_data.key

    def get_user_data(self):
        return self.user_data

    def get_org_data(self):
        return self.org_data

    def get_role(self):
        return self.access_data.role

    def get_permitted_organizations(self):
        return get_organizations(self.user_key)

    def get_projects(self, project_status):
        return get_projects(self.org_key, project_status)


# Permissions decorator, used and re-checked on every page load, first check login, account active, then org + role.
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
                org_data = None
                access_data = None
                if kwargs and kwargs['org_id']:
                    org_data = get_org_data_by_id(kwargs['org_id'])
                    access_data = check_access(org_data.key, user_data.key)
                    # Check Permissions
                    if not access_data and not roles and access_data.role not in roles:
                        abort(403)

                kwargs['user'] = LoggedUser(user_data, org_data, access_data)
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
    new_org = NewOrganisation()

    if request.method == 'POST':
        if new_org.validate_on_submit():
            org_id = create_org(new_org.org_name.data, new_org.org_phone.data, kwargs['user'].user_key)
            if org_id:
                time.sleep(1)
                return redirect(url_for('authenticated.org_homepage', org_id=org_id.key.id()))

    return render_template('authenticated/html/my_workspaces_page.html',
                           form=new_org,
                           user_data=kwargs['user'])


@authenticated.route('/Workspace/<int:org_id>/Projects', methods=['GET', 'POST'])
@login_required('super-admin')
def org_homepage(org_id, **kwargs):
    # # todo: create projects on front end
    # print kwargs['user'].get_projects()

    return render_template('authenticated/html/org_homepage.html',
                           user_data=kwargs['user'],
                           org_data=kwargs['user'].get_org_data(),
                           SIDEBAR=SIDEBAR)


@authenticated.route('/Workspace/<int:org_id>/NewProject', methods=['GET', 'POST'])
@login_required('super-admin')
def new_project_page(org_id, **kwargs):
    new_project = NewProject()

    if request.method == 'POST':
        if new_project.validate_on_submit():
            project_id = create_project(kwargs['user'].org_key,new_project.project_name.data,new_project.project_description.data)
            if project_id:
                return redirect(url_for('authenticated.org_homepage', org_id=org_id))

    return render_template('authenticated/html/new_project_page.html',
                           form=new_project,
                           user_data=kwargs['user'],
                           org_data=kwargs['user'].get_org_data(),
                           SIDEBAR=SIDEBAR)


@authenticated.route('/Workspace/<int:org_id>/Project/<int:project_id>', methods=['GET', 'POST'])
@login_required('super-admin')
# check permission
def view_project_page(org_id, project_id,**kwargs):
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
