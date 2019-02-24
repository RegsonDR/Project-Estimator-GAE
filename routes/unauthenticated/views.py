from flask import Blueprint, render_template, url_for, request, redirect
from routes.unauthenticated.forms import LoginForm, RegisterForm
from utils import register_org, attempt_login, send_verification_email

unauthenticated = Blueprint('unauthenticated', __name__, template_folder='templates')


@unauthenticated.route('/Login', methods=['GET', 'POST'])
def login_page():
    login_form = LoginForm()
    #
    # Check if login request is valid
    if request.method == 'POST' and login_form.validate_on_submit():
        submitted_email = request.form.get('email').lower()
        submitted_passw = request.form.get('password')
        #
        # Attempt to login
        if attempt_login(submitted_email, submitted_passw):
            return redirect(url_for('authenticated.homepage'))
    return render_template('html/login_page.html',
                           form=login_form,
                           page_title="Please Login")


@unauthenticated.route('/Register', methods=['GET', 'POST'])
def register_page():
    register_form = RegisterForm()
    #
    # Check if register request is valid
    if request.method == 'POST' and register_form.validate_on_submit():
        if register_org(
            register_form.org_name.data,
            register_form.org_phone.data,
            register_form.org_open.data,
            register_form.org_close.data,
            register_form.first_name.data,
            register_form.last_name.data,
            register_form.mobile_number.data,
            register_form.password.data,
            register_form.email.data
        ):
            send_verification_email(register_form.email.data)
        return redirect(url_for('unauthenticated.login_page'))

    return render_template('html/register_page.html',
                           form=register_form,
                           page_title="Please Login")


@unauthenticated.route('/Verify', methods=['GET', 'POST'])
def verify_page():
    return True
