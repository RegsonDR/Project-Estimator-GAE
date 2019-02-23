from flask import Flask, redirect, url_for
from routes.authenticated.views import authenticated
from routes.unauthenticated.views import unauthenticated
from routes.ajax.views import ajax


app = Flask(__name__)
app.config['SECRET_KEY'] = '586d4f92e93f985f6ceb58729938c52e'

app.register_blueprint(unauthenticated)
app.register_blueprint(authenticated)
app.register_blueprint(ajax)


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
    return redirect(url_for('login_page'))
