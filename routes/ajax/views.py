from flask import Blueprint, jsonify
from routes.ajax.utils import *

ajax = Blueprint('ajax',__name__,url_prefix='/ajax',template_folder='templates')


@ajax.route('/ResetPassword', methods=['POST'])
def reset_password_email():
    email = request.form.get('reset_email')
    return jsonify({"Request":send_reset_email(email)})

