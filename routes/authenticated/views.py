from flask import Blueprint

authenticated = Blueprint('authenticated',__name__,template_folder='templates')


@authenticated.route('/')
def homepage():
    return 'Logged'
