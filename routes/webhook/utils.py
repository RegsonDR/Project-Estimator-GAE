from routes.api.utils import *
from routes.api.views import user_api_request
from models import WorkspaceDetails
from google.appengine.api import urlfetch
import urllib


def call_webhook(wks_id, test):
    wks_data = WorkspaceDetails.get_by_id(wks_id)
    webhook_url = test
    if not test:
        if not wks_data.enable_webhook or wks_data.enable_webhook == False:
            return False
        if not wks_data.webhook_url or wks_data.webhook_url == "":
            return False
        webhook_url = wks_data.webhook_url

    webhook = user_api_request(wks_data)
    request_data = {}
    request_data['projects'] = webhook.get_all_workspace_projects()
    request_data['tasks'] = []
    request_data['logs'] = []
    for project in request_data['projects']:
        tasks = get_tasks(ProjectDetails.get_by_id(project['ProjectID']).key)
        del project['Wks']
        for task in tasks:
            logs = get_logs(task['TaskID'])
            request_data['logs'].append(logs)
        request_data['tasks'].append(tasks)

    try:
        resp = urlfetch.fetch(
            url=webhook_url,
            method="POST",
            payload=urllib.urlencode({"data": request_data}),
            deadline=100
        )
        return True
    except:
        return False
