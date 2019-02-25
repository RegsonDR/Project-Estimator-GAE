from flask import Blueprint, session, flash, abort, redirect, url_for
from routes.unauthenticated.utils import get_user_data_by_email
from functools import wraps
import gc

authenticated = Blueprint('authenticated', __name__, template_folder='templates')


class LoggedUser:
    def __init__(self, email, first_name, last_name,role, mobile_number, org_key):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.last_name = last_name
        self.role = role
        self.mobile_number = mobile_number
        self.org_key = org_key
        org_data = self.get_from_db().get_org_data()
        self.org_name = org_data.org_name
        self.org_phone = org_data.org_phone
        self.org_open = org_data.org_open
        self.org_close = org_data.org_close

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

    def get_from_db(self):
        return get_user_data_by_email(self.email)

# Permissions decorator, used and re-checked on every page load.
def permitted_roles(roles):
    def permission(f):
        @wraps(f)
        def view(*args, **kwargs):
            if session.get('Logged_In', False):
                user_data = get_user_data_by_email(session.get('Email'))
                #
                # Check if account is active
                if not user_data.is_active:
                    session.clear()
                    gc.collect()
                    flash('Your account is longer active.', 'danger')
                    return redirect(url_for('unauthenticated.login_page'))
                #
                # Create Object
                kwargs['user'] = LoggedUser(
                    user_data.email,
                    user_data.first_name,
                    user_data.last_name,
                    user_data.role,
                    user_data.mobile_number,
                    user_data.organization
                )
                #
                # Check Role
                if user_data.role in roles:
                    return f(*args, **kwargs)
                abort(403)
            else:
                flash('Please login to access the requested page.','danger')
                abort(401)
            return f(*args, **kwargs)

        return view

    return permission


@authenticated.route('/')
@permitted_roles({"super-admin"})
def homepage(**kwargs):
    return kwargs['user'].org_name


@authenticated.route('/')
def debug():
    return session

@authenticated.route('/Logout')
def logout(**kwargs):
    session.clear()
    gc.collect()
    flash("Successfully Logged Out!", "success")
    return redirect(url_for('login_page'))