from flask import Blueprint, jsonify
from routes.ajax.utils import *

ajax = Blueprint('ajax',__name__,url_prefix='/ajax',template_folder='templates')


@ajax.route('/ResetPassword', methods=['POST'])
def reset_password_email():
    email = request.form.get('reset_email')
    return jsonify({"Request":send_reset_email(email)})

@ajax.route('/Project/<int:project_id>/Chat', methods=['POST'])
def chat_message(project_id):
    # try:
        username = request.form.get('username')
        message = base64.b64encode(request.form.get('message').decode('utf-8'))
        message_time = datetime.now()
        print message_time
        email = request.form.get('email')
        role = request.form.get('role')
        log_message(project_id,username,message,message_time,email,role)
        push_message(project_id,username,message,message_time,email,role)
        return jsonify({'result': 'success'})
    # except:
    #     return jsonify({'Request': 'Failed'})

