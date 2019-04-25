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

    def get_id(self):
        account_data = AccountDetails.query(AccountDetails.email == self.UserEmail).get()
        if account_data:
            return account_data.key.id()
        return False

    def get_user_key(self):
        account_data = AccountDetails.query(AccountDetails.email == self.UserEmail).get()
        if account_data:
            return account_data.key
        return False



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

    def delete(self):
        tasks = TaskDetails.query(TaskDetails.Project == self.key).fetch()
        for task in tasks:
            task.delete()
        self.key.delete()
        return True

class TaskDetails(ndb.Model):
    Project = ndb.KeyProperty(kind='ProjectDetails')
    task_name = ndb.StringProperty()
    task_description = ndb.StringProperty()
    task_aminutes = ndb.IntegerProperty()
    task_skills = ndb.IntegerProperty(repeated=True)
    task_developers = ndb.IntegerProperty(repeated=True)
    task_status = ndb.StringProperty(choices={'Open', 'Closed'})
    task_logged_minutes = ndb.IntegerProperty()

    def get_username(self, log_developer):
        account_data = AccountDetails.get_by_id(log_developer)
        return account_data.first_name + " " + account_data.last_name

    def get_logs(self):
        return TaskLog.query(TaskLog.task_id == self.key.id()).order(TaskLog.log_time).fetch()

    def delete(self):
        logs = TaskLog.query(TaskLog.task_id == self.key.id()).order(TaskLog.log_time).fetch(keys_only=True)
        ndb.delete_multi(logs)
        self.key.delete()
        return True

    def remove_minutes(self, minutes):
        self.task_logged_minutes = self.task_logged_minutes - minutes
        if self.put():
            return True
        return False


class TaskLog(ndb.Model):
    task_id = ndb.IntegerProperty()
    log_developer = ndb.IntegerProperty()
    log_minutes = ndb.IntegerProperty()
    log_comments = ndb.StringProperty()
    log_time = ndb.DateTimeProperty()

    def get_username(self):
        account_data = AccountDetails.get_by_id(self.log_developer)
        return account_data.first_name + " " + account_data.last_name

    def update_total(self):
        task_data = TaskDetails.get_by_id(self.task_id)
        logged_tasks = TaskLog.query(TaskLog.task_id == self.task_id)
        total_minutes = self.log_minutes
        for log in logged_tasks.fetch():
            total_minutes = total_minutes + log.log_minutes
        task_data.task_logged_minutes = total_minutes
        if task_data.put():
            return True
        return False

class ProjectChat(ndb.Model):
    project_id = ndb.IntegerProperty()
    username = ndb.StringProperty()
    message = ndb.StringProperty()
    message_time = ndb.DateTimeProperty()
    email = ndb.StringProperty()
    role = ndb.StringProperty()

class SkillData(ndb.Model):
    Wks = ndb.KeyProperty(kind='WorkspaceDetails')
    skill_name = ndb.StringProperty()

    def usage(self):
        return UserSkill.query(UserSkill.skill_id==self.key.id()).count()



class UserSkill(ndb.Model):
    Wks = ndb.KeyProperty(kind='WorkspaceDetails')
    User = ndb.KeyProperty(kind='AccountDetails')
    skill_id = ndb.IntegerProperty()
    skill_rating = ndb.IntegerProperty()

    def skill_name(self):
        return SkillData.get_by_id(self.skill_id).skill_name

    def user_name(self):
        data = AccountDetails.get_by_id(self.User.id())
        return data.first_name + " " + data.last_name
