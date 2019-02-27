from flask import Blueprint, session, flash, abort, redirect, url_for, render_template, request
from forms import NewOrganisation
from utils import create_org
from routes.authenticated.utils import get_user_data_by_email
from functools import wraps
import gc

authenticated = Blueprint('authenticated', __name__, template_folder='templates')


# class LoggedUser:
#     def __init__(self, email, first_name, last_name,role, mobile_number, org_key):
#         self.email = email
#         self.first_name = first_name
#         self.last_name = last_name
#         self.last_name = last_name
#         self.role = role
#         self.mobile_number = mobile_number
#         # self.org_key = org_key
#         # org_data = self.get_from_db().get_org_data()
#         # self.org_name = org_data.org_name
#         # self.org_phone = org_data.org_phone
#
#     def get_full_name(self):
#         return self.first_name + ' ' + self.last_name
#
#     def get_from_db(self):
#         return get_user_data_by_email(self.email)
#
#
# # Permissions decorator, used and re-checked on every page load.
# def permitted_roles(roles):
#     def permission(f):
#         @wraps(f)
#         def view(*args, **kwargs):
#             if session.get('Logged_In', False):
#                 user_data = get_user_data_by_email(session.get('Email'))
#                 #
#                 # Check if account is active
#                 if not user_data.is_active:
#                     session.clear()
#                     gc.collect()
#                     flash('Your account is longer active.', 'danger')
#                     return redirect(url_for('unauthenticated.login_page'))
#                 #
#                 # Create Object
#                 kwargs['user'] = LoggedUser(
#                     user_data.email,
#                     user_data.first_name,
#                     user_data.last_name,
#                     user_data.role,
#                     user_data.mobile_number,
#                     user_data.organization
#                 )
#                 #
#                 # Check Role
#                 if user_data.role in roles:
#                     return f(*args, **kwargs)
#                 abort(403)
#             else:
#                 flash('Please login to access the requested page.','danger')
#                 abort(401)
#             return f(*args, **kwargs)
#
#         return view
#
#     return permission

@authenticated.route('/')
@authenticated.route('/Workspaces')
def my_workspaces_page():
    new_org = NewOrganisation()

    if request.method == 'POST':
        if new_org.validate_on_submit():
            org_id = create_org(new_org.org_name.data, new_org.org_phone.data)
            if org_id:
                return redirect(url_for('authenticated.org_homepage', org_id=org_id))
    return render_template('authenticated/html/my_workspaces_page.html',
                           form=new_org,
                           page_title="Dashboard")


@authenticated.route('/Workspace/<org_id>')
def org_homepage(org_id):
    return render_template('authenticated/html/Blank.html',
                           test=org_id,
                           page_title="Dashboard")


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
