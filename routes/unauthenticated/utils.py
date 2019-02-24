from werkzeug.security import generate_password_hash, check_password_hash
from models import OrganizationDetails, AccountDetails
from flask import flash, request, url_for, render_template
from google.appengine.api import mail
from app_statics import APP_NAME
import uuid


def register_org(org_name, org_phone, org_open, org_close, first_name, last_name, mobile_number, password, email):
    org_data = OrganizationDetails(
        org_name=org_name,
        org_phone=org_phone,
        org_open=org_open,
        org_close=org_close
    )
    user_data = AccountDetails(
        first_name=first_name,
        last_name=last_name,
        mobile_number=mobile_number.replace(' ', ''),
        password=generate_password_hash(password),
        email=email.lower(),
        role='super-admin',
        organization=org_data.put(),
        is_active=False,
        is_verified=False,
        verification_hash=uuid.uuid4().hex
    )
    user_data.put()
    flash('Account successfully created, please check email to verify.', 'success')
    return True


def send_verification_email(email):
    user = get_user_data(email)
    VERIFICATION_URL = (request.url_root + url_for('unauthenticated.verify_page').replace("/", "") + "?email=" + email +
                        "&code=" + user.verification_hash)
    mail.send_mail(
        sender="support@project-application-231720.appspotmail.com",
        to=email,
        subject=APP_NAME + "Verification code",
        body="",
        html=render_template('email/email_verification.html', EMAIL_HEADER="Thanks for signing up!",
                             VERIFICATION_URL=VERIFICATION_URL)
    )
    return True


def attempt_login(email, password):
    user = get_user_data(email)

    if user and check_password_hash(user.password, password):
        return True

    if user and not user.is_verified:
        flash('Please check your email to verify your account before use.', 'danger')
        return False

    flash('Email or Password incorrect, please try again.', 'danger')
    return False


def get_user_data(email):
    return AccountDetails.query(AccountDetails.email == email.lower()).get()
