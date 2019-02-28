from flask import Blueprint, session, flash, abort, redirect, url_for, render_template, request
from forms import NewOrganisation
from models import AccountDetails
from routes.authenticated.utils import create_org, get_user_data_by_email, get_user_data_by_id, check_access, \
    get_org_data_by_id, get_organizations
from functools import wraps
import gc
import time

authenticated = Blueprint('authenticated', __name__, template_folder='templates')


class LoggedUser:
    def __init__(self, user_key, org_key=None):
        self.org_key = org_key
        self.user_key = user_key

    def get_user_data(self):
        return get_user_data_by_id(self.user_key.id())

    def get_permitted_organizations(self):
        return get_organizations(self.user_key)

    def get_org_data(self):
        return get_org_data_by_id(self.org_key.id())


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
                org_key = None
                if kwargs and kwargs['org_id']:
                    org_key = get_org_data_by_id(kwargs['org_id']).key
                    permission = check_access(org_key, user_data.key)
                    # Check Permissions
                    if not permission and not roles and permission.role not in roles:
                        abort(403)

                kwargs['user'] = LoggedUser(user_data.key, org_key)
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

    permitted_organizations = kwargs['user'].get_permitted_organizations()
    return render_template('authenticated/html/my_workspaces_page.html',
                           form=new_org,
                           permitted_organizations=permitted_organizations,
                           page_title="Dashboard")


@authenticated.route('/Workspace/<int:org_id>', methods=['GET', 'POST'])
@login_required('super-admin')
def org_homepage(org_id, **kwargs):
    org_data = kwargs['user'].get_org_data()

    return render_template('authenticated/html/org_homepage.html',
                           page_title=org_data.org_name)


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
