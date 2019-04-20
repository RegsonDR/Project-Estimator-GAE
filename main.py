from flask import Flask, redirect, url_for
from routes.authenticated.views import authenticated
from routes.unauthenticated.views import unauthenticated
from routes.ajax.views import ajax
from routes.api.views import api
import base64


app = Flask(__name__)
app.config['SECRET_KEY'] = '586d4f92e93f985f6ceb58729938c52e'
app.register_blueprint(unauthenticated)
app.register_blueprint(authenticated)
app.register_blueprint(ajax)
app.register_blueprint(api)

# JINJA2 : Decodes base64
def decode_base64(string):
    if isinstance(string, str):
        string = string.decode('utf-8').strip()
    return base64.b64decode(string)

app.jinja_env.filters['decodeb64'] = decode_base64

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
