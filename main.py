from flask import Flask, redirect, url_for
from routes.authenticated.views import authenticated
from routes.unauthenticated.views import unauthenticated
from routes.webhook.views import webhook
from routes.ajax.views import ajax
from routes.api.views import api
import base64
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = '586d4f92e93f985f6ceb58729938c52e'
app.register_blueprint(unauthenticated)
app.register_blueprint(authenticated)
app.register_blueprint(webhook)
app.register_blueprint(ajax)
app.register_blueprint(api)

# JINJA2 : Decodes base64
def decode_base64(string):
    if isinstance(string, str):
        string = string.decode('utf-8').strip()
    return base64.b64decode(string)

def int_to_minhour(minutes):
    if isinstance(minutes, int):
        return '{:02d}:{:02d}'.format(*divmod(minutes, 60))
    else:
        return '00:00'


def create_initials(full_name):
    if isinstance(full_name, str):
        print full_name
    names = full_name.split(" ")
    return names[0][0].upper()+names[1][0].upper()


def check_late(date):
    today = datetime.today().date()
    check = datetime.strptime(date, '%d/%m/%Y').date()
    return check < today

def format_date(date):
    return datetime.strftime(date, '%H:%M %d/%m/%Y')

app.jinja_env.filters['decodeb64'] = decode_base64
app.jinja_env.filters['int_to_minhour'] = int_to_minhour
app.jinja_env.filters['create_initials'] = create_initials
app.jinja_env.filters['check_late'] = check_late
app.jinja_env.filters['format_date'] = format_date

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True


if __name__ == '__main__':
    app.run()


@app.errorhandler(404)
def page_not_found(e):
    return e


@app.errorhandler(403)
def forbidden(e):
    return e


@app.errorhandler(401)
def unauthorised(e):
    return redirect(url_for('unauthenticated.login_page'))
