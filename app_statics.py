APP_NAME = "Project Estimator"
RECAPTCHA_SECRET = "6LeTmZMUAAAAAPsfXDZJWpxP2Q1A2e9XhOCA1zlf"
SIDEBAR = {
    'super-admin':[
        {
            "label":"Projects",
            "view": "authenticated.org_homepage",
            "icon": "tachometer-alt",
        },
        {
            "label": "New Project",
            "view": "authenticated.new_project_page",
            "icon": "plus",
        },
    ]
}
