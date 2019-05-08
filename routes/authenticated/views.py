# coding=utf-8
import gc
import time
from functools import wraps
from app_statics import SIDEBAR
from flask import Blueprint, session, abort, redirect
from forms import *
from models import *
from routes.authenticated.utils import *
from routes.webhook.utils import call_webhook

authenticated = Blueprint('authenticated', __name__, template_folder='templates')


class DictMissKey(dict):
    # Create key if doesn't exist
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value


class LoggedUser:
    def __init__(self, user_data, user_email, wks_data=None, projects_data=None, task_data=None, access_data=None):
        self.user_data = user_data
        self.user_key = user_data.key
        self.user_email = user_email

        if wks_data:
            self.wks_data = wks_data
            self.wks_key = wks_data.key
        if access_data:
            self.access_data = access_data
            self.access_key = access_data.key
        if projects_data:
            self.projects_data = projects_data
            self.projects_key = projects_data.key
        if task_data:
            self.task_data = task_data
            self.task_key = task_data.key

    def get_user_data(self):
        return self.user_data

    def get_wks_data(self):
        return self.wks_data

    def get_file_meta(self):
        return get_file_meta(self.wks_data)

    def get_project_data(self):
        return self.projects_data

    def get_task_data(self):
        return self.task_data

    def get_role(self):
        return self.access_data.role

    def get_permitted_workspaces(self):
        return get_workspaces(self.user_email)

    def get_tasks(self):
        return get_tasks(self.projects_key, self.get_role(), self.user_data.key.id())

    def get_invites(self):
        return get_invites(self.user_email)

    def get_projects(self, project_status):
        return get_projects(self.wks_key, self.get_role(), self.user_email, project_status, self.user_key.id())

    def get_all_projects(self):
        return get_all_projects(self.wks_key, self.get_role(), self.user_email, self.user_key.id())

    # This is used to get number on any task, not the one the page is on.
    def get_open_task_number(self, project_key):
        return get_open_task_number(project_key)

    def get_total_task_number(self, project_key):
        return get_total_task_number(project_key)

    def get_invites_number(self):
        return get_invites_number(self.user_email)

    def get_all_users(self):
        return get_all_users(self.wks_key)

    def get_total_allocated_minutes(self):
        return get_total_allocated_minutes(self.projects_key)

    def get_total_logged_minutes(self):
        return get_total_logged_minutes(self.projects_key)

    def get_username(self, log_developer):
        account_data = AccountDetails.get_by_id(log_developer)
        return account_data.first_name + " " + account_data.last_name

    def call_webhook(self):
        call_webhook(self.wks_key.id(), False)

    def get_prediction(self, functional_points):
        return self.projects_data.predict(functional_points)
        # return get_prediction(self.wks_key, functional_points)



# Permissions decorator, used and re-checked on every page load, first check login, account active, then workspace + role.
def login_required(roles=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if session.get('Logged_In', False):
                user_data = get_user_data_by_email(session.get('Email'))
                #
                # Check if account is active
                if not user_data.is_active:
                    session.clear()
                    gc.collect()
                    flash('Your account is no longer active.', 'danger')
                    return redirect(url_for('unauthenticated.login_page'))
                #
                wks_data = None
                projects_data = None
                task_data = None
                access_data = None
                if 'wks_id' in kwargs.keys():
                    if kwargs['wks_id'] == 0:
                        return redirect(url_for('authenticated.my_workspaces_page'))
                    wks_data = get_wks_data_by_id(kwargs['wks_id'])
                    if not wks_data:
                        abort(403)
                    access_data = check_access(wks_data.key, session.get('Email'))
                    # Check Permissions for workspace
                    if not access_data or access_data.role not in roles:
                        abort(403)
                    # Check Permission for project
                    if 'project_id' in kwargs.keys():
                        projects_data = get_project_data_by_id(kwargs['project_id'])
                        if not projects_data:
                            abort(403)
                        if not check_project_access(projects_data, session.get('Email'), access_data.role):
                            abort(403)
                    if 'task_id' in kwargs.keys():
                        task_data = get_task_data_by_id(kwargs['task_id'])
                        if not task_data:
                            abort(403)

                kwargs['user'] = LoggedUser(user_data, session.get('Email'), wks_data, projects_data, task_data,
                                            access_data)

            elif request.args.get("email") is not None:
                flash('Please login or sign up to access the requested page.', 'danger')
                return redirect(url_for('unauthenticated.register_page', email=request.args.get("email")))
            else:
                flash('Please login to access the requested page.', 'danger')
                abort(401)
            return func(*args, **kwargs)

        return wrapper

    return decorator


# Only Admin:

@authenticated.route('/Workspace/<int:wks_id>/Users', methods=['GET', 'POST'])
@login_required('admin')
def users_page(wks_id, **kwargs):
    new_user = NewUser()
    if request.method == "POST" and new_user.validate_on_submit():
        if add_user(kwargs['user'].wks_key, kwargs['user'].get_wks_data().workspace_name, new_user.user_email.data,
                    new_user.role.data):
            return redirect(url_for('authenticated.users_page', wks_id=wks_id))

    return render_template('authenticated/html/users_page.html',
                           form=new_user,
                           user_data=kwargs['user'],
                           wks_data=kwargs['user'].get_wks_data(),
                           SIDEBAR=SIDEBAR)


@authenticated.route('/Workspace/<int:wks_id>/Settings', methods=['GET', 'POST'])
@login_required('admin')
def wk_settings(wks_id, **kwargs):
    form = WKSettings()
    file_form = UploadHistorical()

    wk_data = kwargs['user'].get_wks_data()

    if request.method == "POST":
        if 'save' in request.form and file_form.validate_on_submit():
            if save_file(wk_data.key,file_form.file):
                flash('File Upload, recalibrate algorithm to use new data!', 'success')
                return redirect(url_for('authenticated.wk_settings', wks_id=wks_id))
            flash('Error occurred, please try again!', 'danger')
        if 'submit' in request.form and form.validate_on_submit():
            wk_data.workspace_name = form.workspace_name.data
            if form.enable_api.data == "False":
                wk_data.enable_api = False
            else:
                wk_data.enable_api = True

            if form.allow_dev_skills.data == "False":
                wk_data.allow_dev_skills = False
            else:
                wk_data.allow_dev_skills = True

            if form.enable_webhook.data == "False":
                wk_data.enable_webhook = False
            else:
                wk_data.enable_webhook = True

            wk_data.webhook_url = form.webhook_url.data

            if wk_data.put():
                flash('Details updated!', 'success')
                return redirect(url_for('authenticated.wk_settings', wks_id=wks_id))
            flash('Error occurred, please try again!', 'danger')

    form.workspace_name.data = wk_data.workspace_name
    form.allow_dev_skills.data = str(wk_data.allow_dev_skills)
    form.api_key.data = wk_data.api_key
    form.enable_api.data = str(wk_data.enable_api)
    form.webhook_url.data = wk_data.webhook_url
    form.enable_webhook.data = str(wk_data.enable_webhook)

    return render_template('authenticated/html/wk_settings.html',
                           form=form,
                           file_form=file_form,
                           user_data=kwargs['user'],
                           wks_data=kwargs['user'].get_wks_data(),
                           SIDEBAR=SIDEBAR)


# Manager or higher:
@authenticated.route('/Workspace/<int:wks_id>/Skills/<int:user_id>', methods=['GET', 'POST'])
@authenticated.route('/Workspace/<int:wks_id>/MySkills', methods=['GET', 'POST'])
@login_required({'admin', 'manager', 'developer'})
def my_skills_page(wks_id, user_id=None, **kwargs):
    if not kwargs['user'].get_wks_data().allow_dev_skills and kwargs['user'].get_role() == "developer":
        flash('Your Manager handles your skills, contact them to update!', 'warning')
        return redirect(url_for('authenticated.workspace_homepage', wks_id=wks_id))

    if user_id and (kwargs['user'].get_role() == "admin" or kwargs['user'].get_role() == "manager"):
        account_data = AccountDetails.get_by_id(user_id)
        look_up_key = account_data.key
        name = account_data.first_name
    else:
        look_up_key = kwargs['user'].user_key
        name = kwargs['user'].user_data.first_name

    new_skill = AddSkill()
    new_skill.skill_name.choices = [(skill.key.id(), skill.skill_name) for skill in
                                    SkillData.query(SkillData.Wks == kwargs['user'].wks_key
                                                    ).fetch()]

    if request.method == "POST":
        create_skill(new_skill.skill_name.data, kwargs['user'].wks_key, look_up_key)
        time.sleep(1)
        return redirect(url_for('authenticated.my_skills_page', wks_id=wks_id, user_id=user_id))

    current_skills = UserSkill.query(UserSkill.Wks == kwargs['user'].wks_key, UserSkill.User == look_up_key).fetch()

    return render_template('authenticated/html/my_skills_page.html',
                           name=name,
                           user_data=kwargs['user'],
                           wks_data=kwargs['user'].get_wks_data(),
                           current_skills=current_skills,
                           form=new_skill,
                           SIDEBAR=SIDEBAR)


@authenticated.route('/Workspace/<int:wks_id>/SkillsMatrix', methods=['GET', 'POST'])
@login_required({'admin', 'manager'})
def skills_matrix_page(wks_id, **kwargs):
    skill_data = [(skill.skill_name, skill.key.id()) for skill in
                  SkillData.query(SkillData.Wks == kwargs['user'].wks_key).fetch(
                      projection=[SkillData.skill_name]) if skill.usage() > 0]

    users_data = [(user.get_name(), user.get_user_key(), user.get_id()) for user in
                  UserProfile.query(
                      UserProfile.Wks == kwargs['user'].wks_key,
                      UserProfile.invitation_accepted == True,
                      UserProfile.disabled == False).fetch()
                  ]

    user_skill = DictMissKey()
    for user in users_data:
        user_skill[user[0]]['id'] = user[2]
        for skill in skill_data:
            test = UserSkill.query(UserSkill.Wks == kwargs['user'].wks_key,
                                   UserSkill.User == user[1],
                                   UserSkill.skill_id == skill[1]
                                   ).get()
            if test:
                user_skill[user[0]][skill[0]] = test.skill_rating
            else:
                user_skill[user[0]][skill[0]] = 0

    return render_template('authenticated/html/skills_matrix_page.html',
                           skill_data=skill_data,
                           user_skill=user_skill,
                           user_data=kwargs['user'],
                           wks_data=kwargs['user'].get_wks_data(),
                           SIDEBAR=SIDEBAR)


# Developer or higher (basically must be a user of the workspace):
@authenticated.route('/Workspace/<int:wks_id>/Timeline', methods=['GET', 'POST'])
@login_required({'admin', 'manager', 'developer'})
def timelines(wks_id, **kwargs):
    resources = []
    events = []

    for project in kwargs['user'].get_all_projects():
        data = filter(lambda pm: pm['id'] == project.project_manager, resources)
        if data:
            data[0]['children'].append({'id': str(project.key.id()), 'title': project.project_name})
        else:
            resources.append({
                'id': project.project_manager,
                'title': project.get_pm_data(),
                'children': [{'id': str(project.key.id()), 'title': project.project_name}]
            })

        project_start = datetime.strptime(project.project_start, '%d/%m/%Y').strftime('%Y-%m-%d')
        project_deadline = datetime.strptime(project.project_deadline, '%d/%m/%Y').strftime('%Y-%m-%d')
        if project.project_status == "Running":
            color = "green"
        elif project.project_status == "Closed":
            color = "yellow"
        else:
            color = "red"
        events.append({
            'resourceId': str(project.key.id()),
            'title': project.project_name,
            'color': color,
            'start': project_start,
            'end': project_deadline,
            'url': url_for('authenticated.view_project_page', wks_id=wks_id, project_id=project.key.id())
        })

    return render_template('authenticated/html/timelines.html',
                           user_data=kwargs['user'],
                           resources=resources,
                           events=events,
                           wks_data=kwargs['user'].get_wks_data(),
                           SIDEBAR=SIDEBAR)


@authenticated.route('/Workspace/<int:wks_id>/Project/<int:project_id>/GanttChart', methods=['GET', 'POST'])
@login_required({'admin', 'manager'})
def ganttchart(wks_id, project_id, **kwargs):
    # only show if manager of project
    tasks = kwargs['user'].get_tasks()
    project_data = kwargs['user'].get_project_data()
    resources = [{
        'id': str(project_data.key.id()),
        'title': project_data.project_name,
        'children': []}]
    events = []
    for task in tasks:
        resources[0]['children'].append({
            'id': str(task.key.id()),
            'title': task.task_name,
        })
        task_start = datetime.strftime(task.task_startdate, '%Y-%m-%d')
        task_deadline = datetime.strftime(task.task_finishbydate, '%Y-%m-%d')

        color = "red"
        if task.task_status == "Open":
            color = "green"

        events.append({
            'resourceId': str(task.key.id()),
            'title': task.task_name,
            'color': color,
            'start': task_start,
            'end': task_deadline,
            'url': url_for('authenticated.view_task_page', wks_id=wks_id, project_id=project_id, task_id=task.key.id())
        })

        project_start = datetime.strptime(project_data.project_start, '%d/%m/%Y').strftime('%Y-%m-%d')
        project_deadline = datetime.strptime(project_data.project_deadline, '%d/%m/%Y').strftime('%Y-%m-%d')
    events.append({
        'resourceId': str(project_data.key.id()),
        'title': project_data.project_name,
        'start': project_start,
        'end': project_deadline,
    })

    return render_template('authenticated/html/ganttchart.html',
                           user_data=kwargs['user'],
                           project_data=project_data,
                           resources=resources,
                           events=events,
                           project_id=project_id,
                           wks_data=kwargs['user'].get_wks_data(),
                           SIDEBAR=SIDEBAR)


@authenticated.route('/Workspace/<int:wks_id>/Projects', methods=['GET', 'POST'])
@login_required({'admin', 'manager', 'developer'})
def workspace_homepage(wks_id, **kwargs):
    new_project = NewProject()

    total = 0
    for skill in SkillData.query(SkillData.Wks == kwargs['user'].wks_key):
        total = total + skill.usage()

    if total == 0:
        flash("To begin, please let up skills for at least one user!", "info")

    if request.method == 'POST':
        if new_project.validate_on_submit() and kwargs['user'].get_role() != "developer":
            project_id = create_project(kwargs['user'].wks_key, kwargs['user'].user_email,
                                        new_project.project_description.data, new_project.project_start.data,
                                        new_project.project_deadline.data,
                                        new_project.project_name.data)

            time.sleep(1)
            kwargs['user'].call_webhook()
            return redirect(url_for('authenticated.view_project_page', wks_id=wks_id, project_id=project_id))

    return render_template('authenticated/html/workspace_homepage.html',
                           form=new_project,
                           user_data=kwargs['user'],
                           wks_data=kwargs['user'].get_wks_data(),
                           SIDEBAR=SIDEBAR)


@authenticated.route('/Workspace/<int:wks_id>/Project/<int:project_id>', methods=['GET', 'POST'])
@login_required({'admin', 'manager', 'developer'})
def view_project_page(wks_id, project_id, **kwargs):
    project_form = Project()
    project_form.project_manager.choices = [(user.UserEmail, user.get_name()) for user in
                                            UserProfile.query(UserProfile.role != "developer",
                                                              UserProfile.Wks == kwargs['user'].wks_key,
                                                              UserProfile.invitation_accepted == True).fetch(
                                                projection=[UserProfile.UserEmail])]

    manager_data = [(user.UserEmail, user.get_name(), user.disabled) for user in
                    UserProfile.query(UserProfile.role != "developer", UserProfile.Wks == kwargs['user'].wks_key,
                                      UserProfile.invitation_accepted == True).fetch(
                        projection=[UserProfile.UserEmail, UserProfile.disabled])]

    project_data = kwargs['user'].get_project_data()
    if request.method == "POST" and project_form.validate_on_submit() and kwargs['user'].get_role() != "developer":
        project_data.project_name = project_form.project_name.data
        project_data.project_start = project_form.project_start.data
        project_data.project_deadline = project_form.project_deadline.data
        project_data.project_function_points = project_form.project_function_points.data
        project_data.project_description = project_form.project_description.data
        project_data.project_manager = project_form.project_manager.data
        project_data.project_stage = project_form.project_stage.data
        project_data.project_status = project_form.project_status.data
        if project_data.put():
            kwargs['user'].call_webhook()
            flash('Project details updated!', 'success')
            return redirect(url_for('authenticated.view_project_page', wks_id=wks_id, project_id=project_id))
        flash('Error occurred, please try again!', 'danger')

    project_form.project_name.data = project_data.project_name
    project_form.project_start.data = project_data.project_start
    project_form.project_deadline.data = project_data.project_deadline
    project_form.project_description.data = project_data.project_description
    project_form.project_manager.data = project_data.project_manager
    project_form.project_stage.data = project_data.project_stage
    project_form.project_status.data = project_data.project_status
    project_form.project_function_points.data = project_data.project_function_points

    if kwargs['user'].get_role() == "developer":
        project_form.project_name.render_kw = {"disabled": True}
        project_form.project_start.render_kw = {"disabled": True}
        project_form.project_deadline.render_kw = {"disabled": True}
        project_form.project_description.render_kw = {"disabled": True}
        project_form.project_stage.render_kw = {"disabled": True}
        project_form.project_status.render_kw = {"disabled": True}
        project_form.project_function_points.render_kw = {"disabled": True}

    skill_choices = [(skill.key.id(), skill.skill_name) for skill in
                     SkillData.query(SkillData.Wks == kwargs['user'].wks_key
                                     ).fetch(projection=[SkillData.skill_name]) if skill.usage() > 0]

    users_choices = [(u_s.User.id(), u_s.user_name(), u_s.skill_name(), u_s.disabled_check()) for u_s in
                     UserSkill.query().fetch()]

    dev_options = DictMissKey()
    for choice in users_choices:
        dev_options[choice[0]]['name'] = choice[1]
        dev_options[choice[0]]['disabled'] = choice[3]

        if dev_options[choice[0]]['skills']:
            dev_options[choice[0]]['skills'] = dev_options[choice[0]]['skills'] + ";" + choice[2]
        else:
            dev_options[choice[0]]['skills'] = choice[2]

    tasks = convert_tasks(kwargs['user'].get_tasks())

    return render_template('authenticated/html/view_project_page.html',
                           # tasks=kwargs['user'].get_tasks(),
                           tasks=tasks,
                           dev_options=dev_options,
                           skill_choices=skill_choices,
                           user_data=kwargs['user'],
                           wks_data=kwargs['user'].get_wks_data(),
                           form=project_form,
                           project_data=project_data,
                           manager_data=manager_data,
                           SIDEBAR=SIDEBAR)


@authenticated.route('/Workspace/<int:wks_id>/Project/<int:project_id>/Task/<int:task_id>', methods=['GET', 'POST'])
@login_required({'admin', 'manager', 'developer'})
def view_task_page(wks_id, project_id, task_id, **kwargs):
    task_form = Task()
    log_form = LogTask()
    task_form.parent_task.choices = [(str(task.key.id()), task.task_name) for task in
                                     TaskDetails.query(TaskDetails.Project == kwargs['user'].projects_key, ).fetch(
                                         projection=TaskDetails.task_name) if task.key.id() != task_id]
    task_form.parent_task.choices.append(['None', 'None'])

    task_form.task_skills.choices = [(str(skill.key.id()), skill.skill_name) for skill in
                                     SkillData.query(SkillData.Wks == kwargs['user'].wks_key
                                                     ).fetch(projection=[SkillData.skill_name]) if skill.usage() > 0]

    task_form.task_developers.choices = [(str(user.get_id()), user.get_name()) for user in
                                         UserProfile.query(UserProfile.Wks == kwargs['user'].wks_key,
                                                           UserProfile.invitation_accepted == True).fetch(
                                             projection=[UserProfile.UserEmail])]

    users_choices = [(str(u_s.User.id()), u_s.user_name(), u_s.skill_name(), u_s.disabled_check()) for u_s in
                     UserSkill.query().fetch()]

    dev_options = DictMissKey()
    for choice in users_choices:
        dev_options[choice[0]]['name'] = choice[1]
        dev_options[choice[0]]['disabled'] = choice[3]

        if dev_options[choice[0]]['skills']:
            dev_options[choice[0]]['skills'] = dev_options[choice[0]]['skills'] + ";" + choice[2]
        else:
            dev_options[choice[0]]['skills'] = choice[2]

    task_data = kwargs['user'].get_task_data()

    if request.method == "POST" and task_form.validate_on_submit():
        if kwargs['user'].get_role() != "developer":
            task_data.task_name = task_form.task_name.data
            task_data.task_aminutes = task_form.task_aminutes.data
            task_data.task_startdate = datetime.strptime(str(task_form.task_startdate.data), '%d/%m/%Y')
            task_data.task_finishbydate = datetime.strptime(str(task_form.task_finishbydate.data), '%d/%m/%Y')
            task_data.task_description = task_form.task_description.data
            task_data.task_skills = map(int, task_form.task_skills.data)
            task_data.task_developers = map(int, task_form.task_developers.data)
            if task_form.parent_task.data == "None":
                task_data.parent_task = None
            else:
                task_data.parent_task = int(task_form.parent_task.data)
        task_data.task_status = task_form.task_status.data
        if task_data.put():
            kwargs['user'].call_webhook()
            flash('Task details updated!', 'success')
            return redirect(
                url_for('authenticated.view_task_page', wks_id=wks_id, project_id=project_id, task_id=task_id))
        flash('Error occurred, please try again!', 'danger')

    task_form.task_name.data = task_data.task_name
    task_form.task_aminutes.data = task_data.task_aminutes
    task_form.task_startdate.data = datetime.strftime(task_data.task_startdate, '%d/%m/%Y')
    task_form.task_finishbydate.data = datetime.strftime(task_data.task_finishbydate, '%d/%m/%Y')
    task_form.task_status.data = task_data.task_status
    task_form.task_description.data = task_data.task_description
    task_form.task_skills.data = map(str, task_data.task_skills)
    task_form.task_developers.data = map(str, task_data.task_developers)
    task_form.parent_task.data = str(task_data.parent_task)

    if kwargs['user'].get_role() == "developer":
        task_form.task_name.render_kw = {'readonly': True}
        task_form.task_aminutes.render_kw = {'readonly': True}
        task_form.task_startdate.render_kw = {'readonly': True}
        task_form.task_finishbydate.render_kw = {'readonly': True}
        task_form.task_description.render_kw = {'readonly': True}
        task_form.task_skills.render_kw = {'disabled': True}
        task_form.task_developers.render_kw = {'readonly': True}
        task_form.parent_task.render_kw = {'readonly': True}

    return render_template('authenticated/html/view_task_page.html',
                           user_data=kwargs['user'],
                           form=task_form,
                           task_data=task_data,
                           dev_options=dev_options,
                           log_form=log_form,
                           project_id=project_id,
                           wks_data=kwargs['user'].get_wks_data(),
                           SIDEBAR=SIDEBAR)


@authenticated.route('/Workspace/<int:wks_id>/Project/<int:project_id>/Chat/', methods=['GET', 'POST'])
@login_required({'admin', 'manager', 'developer'})
def project_chat(wks_id, project_id, **kwargs):
    return render_template('authenticated/html/project_chat.html',
                           user_data=kwargs['user'],
                           wks_data=kwargs['user'].get_wks_data(),
                           old_messages=get_chat_messages(project_id),
                           project_data=kwargs['user'].get_project_data(),
                           SIDEBAR=SIDEBAR)


# Not in a particular workspace:

@authenticated.route('/')
@authenticated.route('/Workspaces', methods=['GET', 'POST'])
@login_required()
def my_workspaces_page(**kwargs):
    new_wks = NewWorkspace()
    if request.method == 'POST':
        if new_wks.validate_on_submit():
            wks_id = create_wks(new_wks.workspace_name.data, kwargs['user'].user_email)
            if wks_id:
                time.sleep(1)
                return redirect(url_for('authenticated.workspace_homepage', wks_id=wks_id.key.id()))

    return render_template('authenticated/html/my_workspaces_page.html',
                           form=new_wks,
                           user_data=kwargs['user'])


@authenticated.route('/MyProfile', methods=['GET', 'POST'])
@login_required()
def my_profile_page(**kwargs):
    user_profile = ProfileUser()

    user_data = kwargs['user'].get_user_data()
    if request.method == "POST" and user_profile.validate_on_submit():
        if user_profile.first_name.data is not user_data.first_name:
            user_data.first_name = user_profile.first_name.data
        if user_profile.last_name.data is not user_data.last_name:
            user_data.last_name = user_profile.last_name.data
        if user_profile.email.data is not user_data.email:
            user_data.change_email(user_profile.email.data)
            session['Email'] = user_profile.email.data
        if user_profile.mobile_number.data is not user_data.mobile_number:
            user_data.mobile_number = user_profile.mobile_number.data
        if user_data.put():
            flash('Profile updated!', 'success')
            return redirect(url_for('authenticated.my_profile_page'))
        flash('Error occurred, please try again!', 'danger')

    user_profile.first_name.data = user_data.first_name
    user_profile.last_name.data = user_data.last_name
    user_profile.email.data = user_data.email
    user_profile.mobile_number.data = user_data.mobile_number

    return render_template('authenticated/html/my_profile_page.html',
                           form=user_profile,
                           user_data=kwargs['user'])


@authenticated.route('/MyInvites', methods=['GET', 'POST'])
@login_required()
def my_invites(**kwargs):
    if not kwargs['user'].get_invites_number():
        flash("You have no pending invites!", "danger")
        return redirect(url_for('authenticated.my_workspaces_page'))
    return render_template('authenticated/html/my_invites.html',
                           user_data=kwargs['user'])


@authenticated.route('/Invitation', methods=['GET', 'POST'])
@login_required()
def open_invitation(**kwargs):
    code = request.args.get('code')
    email = request.args.get('email')
    if not email or not code:
        return redirect(url_for('authenticated.my_workspaces_page'))

    if not verify_invite(code, email):
        return redirect(url_for('authenticated.my_workspaces_page'))

    if request.method == "POST":
        if request.form['accepted']:
            verify_invite(code, email).invitation_accepted = True
            verify_invite(code, email).put()
            time.sleep(1)
            flash('Invitation accepted! You can access your new workspace now!', 'success')
            return redirect(url_for('authenticated.my_workspaces_page'))

    return render_template('authenticated/html/open_invitation.html',
                           user_data=kwargs['user'],
                           wks_data=verify_invite(code, email)
                           )


@authenticated.route('/Logout')
@login_required()
def logout(**kwargs):
    session.clear()
    gc.collect()
    flash("Successfully Logged Out!", "success")
    return redirect(url_for('unauthenticated.login_page'))
