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
    reset_code = ndb.StringProperty()

    def change_email(self, new_email):
        profiles = UserProfile.query(UserProfile.UserEmail == self.email)
        for account in profiles.fetch():
            account.UserEmail = new_email
        ndb.put_multi(profiles)
        self.email = new_email
        self.put()
        return True


class WorkspaceDetails(ndb.Model):
    workspace_name = ndb.StringProperty()


class UserProfile(ndb.Model):
    # User = ndb.KeyProperty(kind='AccountDetails')
    UserEmail = ndb.StringProperty()
    Wks = ndb.KeyProperty(kind='WorkspaceDetails')
    workspace_name = ndb.StringProperty()
    role = ndb.StringProperty(choices={'developer', 'manager', 'admin'})
    invitation_token = ndb.StringProperty()
    invitation_accepted = ndb.BooleanProperty()
    disabled = ndb.BooleanProperty()

    def get_name(self):
        account_data = AccountDetails.query(AccountDetails.email == self.UserEmail).get()
        if account_data:
            return account_data.first_name + " " + account_data.last_name
        return False

    # Super admin owns all
    # Super dev can log time anywhere
    # Deve can only log time


class TaskProfile(ndb.Model):
    email = ndb.StringProperty()
    Task = ndb.KeyProperty(kind='TaskDetails')


class ProjectDetails(ndb.Model):
    Wks = ndb.KeyProperty(kind='WorkspaceDetails')
    project_manager = ndb.StringProperty()
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

class ProjectChat(ndb.Model):
    project_id = ndb.IntegerProperty()
    username = ndb.StringProperty()
    message = ndb.StringProperty()
    message_time = ndb.DateTimeProperty()
    email = ndb.StringProperty()
    role = ndb.StringProperty()

