from flask import Blueprint, render_template, url_for, request, redirect, flash
from routes.unauthenticated.forms import LoginForm, RegisterForm

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
        if login_user(submitted_email,submitted_passw):
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
        return 'killyosan'

    return render_template('html/register_page.html',
                           form=register_form,
                           page_title="Please Login")

def login_user(email,password):
    return True
