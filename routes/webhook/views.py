# Internal Testing Webhook
from flask import Blueprint, request
from routes.authenticated.views import login_required

webhook = Blueprint('webhook', __name__, url_prefix='/webhook/')


@webhook.route('/Test', methods=['POST'])
def test(**kwargs):
    print request.form['data']

    return "Pass"
