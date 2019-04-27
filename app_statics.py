APP_NAME = "Project Estimator"
RECAPTCHA_SECRET = "6LeTmZMUAAAAAPsfXDZJWpxP2Q1A2e9XhOCA1zlf"
SIDEBAR = {
    'admin':[
        {
            "label":"Projects",
            "view": "authenticated.workspace_homepage",
            "icon": "tachometer-alt",
        },{
            "label": "Timelines",
            "view": "authenticated.timelines",
            "icon": "calendar-week",
        },{
            "label": "My Skills",
            "view": "authenticated.my_skills_page",
            "icon": "sliders-h",
        },
        {
            "label": "Skills Matrix",
            "view": "authenticated.skills_matrix_page",
            "icon": "chart-area",
        },{
            "label": "Users",
            "view": "authenticated.users_page",
            "icon": "users-cog",
        },{
            "label": "Settings",
            "view": "authenticated.wk_settings",
            "icon": "cogs",
        }
    ],
    'manager': [
        {
            "label": "Projects",
            "view": "authenticated.workspace_homepage",
            "icon": "tachometer-alt",
        },{
            "label": "Timelines",
            "view": "authenticated.timelines",
            "icon": "calendar-week",
        },{
            "label": "My Skills",
            "view": "authenticated.my_skills_page",
            "icon": "sliders-h",
        },
        {
            "label": "Skills Matrix",
            "view": "authenticated.skills_matrix_page",
            "icon": "chart-area",
        }
    ],
    'developer':[
        {
            "label": "Projects",
            "view": "authenticated.workspace_homepage",
            "icon": "tachometer-alt",
        },{
            "label": "Timelines",
            "view": "authenticated.timelines",
            "icon": "calendar-week",
        },{
            "label": "My Skills",
            "view": "authenticated.my_skills_page",
            "icon": "sliders-h",
        }
    ]
}
