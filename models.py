from google.appengine.ext import ndb


# Account Data
class AccountDetails(ndb.Model):
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    mobile_number = ndb.StringProperty()
    password = ndb.StringProperty()
    email = ndb.StringProperty()
    is_active = ndb.BooleanProperty()
    is_verified = ndb.BooleanProperty()
    verification_code = ndb.StringProperty()


class WorkspaceDetails(ndb.Model):
    workspace_name = ndb.StringProperty()

class UserProfile(ndb.Model):
    User = ndb.KeyProperty(kind='AccountDetails')
    Wks = ndb.KeyProperty(kind='WorkspaceDetails')
    workspace_name = ndb.StringProperty()
    role = ndb.StringProperty(choices={'dev', 'manager', 'super-dev', 'super-admin'})


class ProjectDetails(ndb.Model):
    Wks = ndb.KeyProperty(kind='WorkspaceDetails')
    project_name = ndb.StringProperty()
    project_description = ndb.StringProperty()
    project_deadline = ndb.StringProperty()
    project_status = ndb.StringProperty(choices={'Running', 'Closed', 'On Hold'})
    project_stage = ndb.StringProperty()


class TaskDetails(ndb.Model):
    Project = ndb.KeyProperty(kind='ProjectDetails')
    task_name = ndb.StringProperty()
    task_description = ndb.StringProperty()
    task_aminutes = ndb.IntegerProperty()
    task_skills = ndb.IntegerProperty(repeated=True)
    task_developers = ndb.IntegerProperty(repeated=True)
    task_status = ndb.StringProperty()
