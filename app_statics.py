APP_NAME = "Project Estimator"
RECAPTCHA_SECRET = "6LeTmZMUAAAAAPsfXDZJWpxP2Q1A2e9XhOCA1zlf"
SIDEBAR = {
    'admin':[
        {
            "label":"Projects",
            "view": "authenticated.workspace_homepage",
            "icon": "tachometer-alt",
        },
        {
            "label": "New Project",
            "view": "authenticated.new_project_page",
            "icon": "folder-plus",
        },{
            "label": "Add Users",
            "view": "authenticated.add_users_page",
            "icon": "user-plus",
        }
    ],
    'manager': [
        {
            "label": "Projects",
            "view": "authenticated.workspace_homepage",
            "icon": "tachometer-alt",
        },
        {
            "label": "New Project",
            "view": "authenticated.new_project_page",
            "icon": "plus",
        }
    ],


}
