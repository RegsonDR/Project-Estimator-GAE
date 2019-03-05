from flask import Blueprint, render_template, url_for, request, redirect, session
from routes.unauthenticated.forms import LoginForm, RegisterForm
from utils import register_user, attempt_login, send_verification_email, check_recaptcha, verify_account

unauthenticated = Blueprint('unauthenticated', __name__, template_folder='templates')


@unauthenticated.route('/Login', methods=['GET', 'POST'])
def login_page():
    login_form = LoginForm()
    #
    # Check if login request is valid
    if request.method == 'POST':
        if login_form.validate_on_submit():
            submitted_email = request.form.get('email').lower()
            submitted_passw = request.form.get('password')
            if attempt_login(submitted_email, submitted_passw):
                session['Logged_In'] = True
                session['Email'] = submitted_email
                return redirect(url_for('authenticated.my_workspaces_page'))
    return render_template('unauthenticated/html/login_page.html',
                           form=login_form,
                           page_title="Please Login")


@unauthenticated.route('/Register', methods=['GET', 'POST'])
def register_page():
    register_form = RegisterForm()
    #
    # Check if register request is valid
    if request.method == 'POST':
        if check_recaptcha():
            if register_form.validate_on_submit():
                user_id = register_user(
                    register_form.first_name.data,
                    register_form.last_name.data,
                    register_form.mobile_number.data,
                    register_form.password.data,
                    register_form.email.data
                )
                if user_id:
                    send_verification_email(user_id.key.id())
                    return redirect(url_for('unauthenticated.login_page'))

    return render_template('unauthenticated/html/register_page.html',
                           form=register_form,
                           page_title="Please Sign Up")


@unauthenticated.route('/Verify', methods=['GET', 'POST'])
def verify_page():
    email = request.args.get('email')
    code = request.args.get('code')
    if email and code:
        verify_account(email, code)
    return redirect(url_for("unauthenticated.login_page"))


# TODO: Password Reset Route
@unauthenticated.route('/Reset', methods=['GET', 'POST'])
def reset_password_page():
    return True


