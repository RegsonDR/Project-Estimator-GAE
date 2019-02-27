from models import OrganizationDetails, AccountDetails
from flask import flash


def create_org(org_name, org_phone):
    org_data = OrganizationDetails(
        org_name=org_name,
        org_phone=org_phone
    )
    org_data.put()
    flash('Organization successfully created.', 'success')
    return org_data


def get_user_data_by_email(email):
    return AccountDetails.query(AccountDetails.email == email.lower()).get()
