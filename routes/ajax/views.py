from flask import Blueprint

ajax = Blueprint('ajax',__name__,url_prefix='/ajax')


@ajax.route('/5')
def hello_world():
    return 'Hello World!2'
