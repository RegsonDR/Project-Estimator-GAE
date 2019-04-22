from models import AccountDetails, ProjectChat, TaskLog
from flask import request, url_for, render_template
from google.appengine.api import mail, urlfetch
from app_statics import APP_NAME
from datetime import datetime, timedelta
import uuid
import base64
import hmac
import hashlib
import json
import time

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

def log_message(project_id,username,message,message_time,email,role):
    data = ProjectChat(
        project_id=project_id,
        username=username,
        message=message,
        message_time=message_time,
        email=email,
        role=role
    )
    if data.put():
        return True
    return False

def create_pusher_auth_signature(timestamp, md5):
    app_id = "766185"
    key = "08d09cb027a29bc3cb55"
    secret = "25554a6393a0cbbb0814"
    string = "POST\n/apps/" + app_id + "/events\nauth_key=" + key + "&auth_timestamp=" + timestamp + "&auth_version=1.0&body_md5=" + md5
    return hmac.new(secret, string, hashlib.sha256).hexdigest()

def pusher_request(parameters):
    body_md5 = hashlib.md5(parameters).hexdigest()
    auth_timestamp = '%.0f' % time.time()
    auth_signature = create_pusher_auth_signature(auth_timestamp, body_md5)
    url_endpoint = ("https://api-eu.pusher.com/apps/766185/events?" +
                    "body_md5=" + body_md5 + "&" +
                    "auth_version=1.0&" +
                    "auth_key=08d09cb027a29bc3cb55&" +
                    "auth_timestamp=" + auth_timestamp + "&" +
                    "auth_signature=" + auth_signature)
    resp = urlfetch.fetch(
        url=url_endpoint,
        method="POST",
        payload=parameters,
        headers={"Content-Type": "application/json"}
    )
    return resp.content


def push_chat_message(project_id,username,message,message_time,email,role):
    parameters = json.dumps({
        "data":
            "{\"email\":\"" + email + "\","
            "\"message\":\"" + message + "\","
            "\"role\":\"" + role + "\","
            "\"username\":\"" + username + "\","
            "\"message_time\":\"" + (message_time).strftime('%H:%M | %d-%m-%Y') + "\"}",
        "name": "new-message",
        "channel": str(project_id) + "-channel"})
    return pusher_request(parameters)


def save_log(task_id,log_developer,log_minutes,log_comments):
    log_data = TaskLog(
        task_id=task_id,
        log_developer=get_user_data_by_email(log_developer).key.id(),
        log_minutes=log_minutes,
        log_comments=log_comments,
        log_time=datetime.now() + timedelta(hours=1)
    )
    log_data.update_total()
    if log_data.put():
        return True
    return False




