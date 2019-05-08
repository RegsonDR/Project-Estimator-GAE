from models import AccountDetails, ProjectChat, TaskLog, UserProfile, UserSkill, TaskDetails, ProjectDetails,WorkspaceDetails, PredictionData
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
import csv
import io
import numpy as np

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


def log_message(project_id, username, message, message_time, email, role):
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


def push_chat_message(project_id, username, message, message_time, email, role):
    parameters = json.dumps({
        "data":
            "{\"email\":\"" + email + "\","
                                      "\"message\":\"" + message + "\","
                                                                   "\"role\":\"" + role + "\","
                                                                                          "\"username\":\"" + username + "\","
                                                                                                                         "\"message_time\":\"" + (
                message_time).strftime('%H:%M | %d-%m-%Y') + "\"}",
        "name": "new-message",
        "channel": str(project_id) + "-channel"})
    return pusher_request(parameters)


def save_log(task_id, log_developer, log_minutes, log_comments):
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


def account_switch(wks_key, email):
    profile = UserProfile.query(UserProfile.Wks == wks_key, UserProfile.UserEmail == email).get()
    profile.disabled = not profile.disabled
    if profile.put():
        return True
    return False


def change_user_role(wks_key, email, role):
    profile = UserProfile.query(UserProfile.Wks == wks_key, UserProfile.UserEmail == email).get()
    profile.role = role
    if profile.put():
        return True
    return False


def update_user_skill(user_skill_id, rating):
    data = UserSkill.get_by_id(user_skill_id)
    if rating:
        data.skill_rating = int(rating)
        if not data.put():
            return False
        return True
    if not rating:
        data.key.delete()
        return True
    return False


def delete_task(task_id):
    task = TaskDetails.get_by_id(task_id)
    if task.delete():
        return True
    return False


def delete_log(task_id, log_id):
    log = TaskLog.get_by_id(log_id)
    minutes = log.log_minutes
    log.key.delete()
    task = TaskDetails.get_by_id(task_id)
    if task.remove_minutes(minutes):
        return True
    return False


def create_task(project_id, Title, aMinutes, start, finish, Description, Skills, Developers):
    project = ProjectDetails.get_by_id(int(project_id))
    task_data = TaskDetails(
        Project=project.key,
        task_name=Title,
        task_description=Description,
        task_startdate=datetime.strptime(str(start), '%d/%m/%Y'),
        task_finishbydate=datetime.strptime(str(finish), '%d/%m/%Y'),
        task_skills=map(int, Skills),
        task_developers=map(int, Developers),
        task_aminutes=int(aMinutes),
        task_status="Open"
    )
    if task_data.put():
        return True
    return False


def delete_project(project_id):
    project = ProjectDetails.get_by_id(project_id)
    if project.delete():
        return True
    return False

def regenerate(wk_id,key):
    wk = WorkspaceDetails.get_by_id(wk_id)
    if wk.api_key == key:
        wk.api_key = uuid.uuid4().hex
        if wk.put():
            return True
    return False

def trigger_ml(wks_id, action):

    if action == "recalibrate":
        read_csv(wks_id)
        return True
    elif action == "delete":
        wks_key = WorkspaceDetails.get_by_id(wks_id).key
        data = PredictionData.query(PredictionData.Wks == wks_key).get()
        data.key.delete()
        return True
    return False



def read_csv(wks_id):
    wks_key = WorkspaceDetails.get_by_id(wks_id).key
    data = PredictionData.query(PredictionData.Wks == wks_key).get()
    stream = io.StringIO(data.csv.decode("UTF8"), newline=None)
    csv_input = csv.reader(stream)
    functional_points = []
    actual_minutes = []
    for row in csv_input:
        # Only add if is row contains integer, don't accept decimals or strings
        if is_number(row[0]) and is_number(row[1]):
            functional_points.append(int(row[0]))
            actual_minutes.append(int(row[1]))
    x = np.array(functional_points)
    y = np.array(actual_minutes)
    b = estimate_coef(x, y)
    data.b0 = b[0]
    data.b1 = b[1]
    data.valid_rows = len(functional_points)
    data.calibration_time = datetime.now() + timedelta(hours=1)
    if data.put():
        return True
    return False


def is_number(number):
    try:
        int(number)
        return True
    except ValueError:
        return False


def estimate_coef(x, y):
    # number of observations/points
    n = np.size(x)

    # mean of x and y vector
    m_x, m_y = np.mean(x), np.mean(y)

    # calculating cross-deviation and deviation about x
    SS_xy = np.sum(y * x) - n * m_y * m_x
    SS_xx = np.sum(x * x) - n * m_x * m_x

    # calculating regression coefficients
    b_1 = SS_xy / SS_xx
    b_0 = m_y - b_1 * m_x

    return (b_0, b_1)