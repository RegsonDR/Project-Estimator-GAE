from werkzeug.security import generate_password_hash, check_password_hash
from models import OrganizationDetails, AccountDetails
from flask import flash, request, url_for, render_template
from google.appengine.api import mail, urlfetch
from app_statics import APP_NAME, RECAPTCHA_SECRET
import uuid
import urllib
import json


def register_org(org_name, org_phone, org_open, org_close, first_name, last_name, mobile_number, password, email):
    user = get_user_data_by_email(email)
    if user:
        flash('Email Address already in use!', 'danger')
        return False

    org_data = OrganizationDetails(
        org_name=org_name,
        org_phone=org_phone
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
    return user_data


def send_verification_email(user_id):
    user = get_user_data_by_id(user_id)
    VERIFICATION_URL = (request.url_root + url_for('unauthenticated.verify_page').replace("/", "") + "?email=" + user.email +
                        "&code=" + user.verification_hash)
    mail.send_mail(
        sender="support@project-application-231720.appspotmail.com",
        to=user.email,
        subject=APP_NAME + " Verification code",
        body="",
        html=render_template('email/email_verification.html', EMAIL_HEADER="Thanks for signing up!",
                             VERIFICATION_URL=VERIFICATION_URL)
    )
    return True


def attempt_login(email, password):
    user = get_user_data_by_email(email)

    if user and check_password_hash(user.password, password):
        return True

    if user and not user.is_verified:
        flash('Please check your email to verify your account before use.', 'danger')
        return False

    flash('Email or Password incorrect, please try again.', 'danger')
    return False


def get_user_data_by_email(email):
    return AccountDetails.query(AccountDetails.email == email.lower()).get()


def get_user_data_by_id(id):
    return AccountDetails.get_by_id(id)


def verify_account(email, code):
    user = get_user_data_by_email(email)
    if user and user.verification_hash == code:
        user.is_verified = True
        user.is_active = True
        user.put()
        flash('Email Verified! Please log in to access the site.', 'success')
        return True
    flash('Verification URL is invalid', 'danger')
    return False


def check_recaptcha():
    resp = api_launcher("POST",
                        "https://www.google.com/recaptcha/api/siteverify",
                        {"secret": RECAPTCHA_SECRET,
                         "response": request.form.get("g-recaptcha-response"),
                         "remoteip": request.remote_addr
                         }
                        )

    if not resp['success']:
        flash('Please tick the reCAPTCHA box.', 'warning')
        return False
    return True


def api_launcher(method, url_endpoint, params):
    if method == "GET":
        p = urllib.urlencode(params) if params else ""
        resp = urlfetch.fetch(
            url_endpoint + "?" + p
        )
    if method == "POST":
        resp = urlfetch.fetch(
            url=url_endpoint,
            method="POST",
            payload=urllib.urlencode(params)
        )
    if method == "oAuthv2":
        p = urllib.urlencode(params) if params else ""
        resp = urlfetch.fetch(
            url=url_endpoint,
            method="POST",
            payload=p,
        )

    return json.loads(resp.content)