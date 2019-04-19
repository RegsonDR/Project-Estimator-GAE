from models import AccountDetails
from flask import request, url_for, render_template
from google.appengine.api import mail, urlfetch
from app_statics import APP_NAME
import uuid


def send_verification_email(user_id):
    user = get_user_data_by_id(user_id)
    VERIFICATION_URL = (request.url_root + url_for('unauthenticated.verify_page').replace("/", "") + "?email=" +
                        user.email + "&code=" + user.verification_code)
    mail.send_mail(
        sender="support@project-application-231720.appspotmail.com",
        to=user.email,
        subject=APP_NAME + " Verification Link",
        body="",
        html=render_template('unauthenticated/email/email_verification.html', EMAIL_HEADER="Thanks for signing up!",
                             VERIFICATION_URL=VERIFICATION_URL)
    )
    return True


def get_user_data_by_email(email):
    return AccountDetails.query(AccountDetails.email == email.lower()).get()


def send_reset_email(email):
    account = get_user_data_by_email(email)
    if account:
        reset_code = uuid.uuid4().hex
        if account.reset_code:
            reset_code = account.reset_code
        account.reset_code = reset_code
        account.put()
        RESET_URL = (
                request.url_root + url_for('unauthenticated.reset_password_page').replace("/", "") +
                "?email=" + email +
                "&code=" + reset_code
        )
        #
        mail.send_mail(
            sender="support@project-application-231720.appspotmail.com",
            to=email,
            subject=APP_NAME + " Password Reset Request",
            body="",
            html=render_template('ajax/email/reset_password.html', EMAIL_HEADER="Password Reset Request",
                                 RESET_URL=RESET_URL)
        )
        return True
    return False
