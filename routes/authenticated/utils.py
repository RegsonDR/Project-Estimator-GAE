from models import OrganizationDetails, AccountDetails, UserProfile
from flask import flash


def create_org(org_name, org_phone, user_key):
    org_data = OrganizationDetails(
        org_name=org_name,
        org_phone=org_phone
    )
    org_data.put()

    user_profile= UserProfile(
        User=user_key,
        Org=org_data.key,
        role='super-admin'
    )
    user_profile.put()
    flash('Organization successfully created.', 'success')
    return org_data


def get_user_data_by_email(email):
    return AccountDetails.query(AccountDetails.email == email.lower()).get()


def get_user_data_by_id(datastore_id):
    return AccountDetails.get_by_id(datastore_id)

def get_org_data_by_id(datastore_id):
    return OrganizationDetails.get_by_id(datastore_id)

def check_access(org_key,user_key):
    return UserProfile.query(UserProfile.Org == org_key,UserProfile.User == user_key).get()
