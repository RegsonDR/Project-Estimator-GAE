from google.appengine.ext import ndb


# Account Data
class AccountDetails(ndb.Model):
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    mobile_number = ndb.StringProperty()
    password = ndb.StringProperty()
    email = ndb.StringProperty()
    organizations = ndb.KeyProperty(kind='OrganizationDetails', repeated=True)
    is_active = ndb.BooleanProperty()
    is_verified = ndb.BooleanProperty()
    verification_code = ndb.StringProperty()
    # def get_org_data(self):
    #     org_object = OrganizationDetails.get_by_id(self.organization.id())
    #     return org_object


class OrganizationDetails(ndb.Model):
    org_name = ndb.StringProperty()
    org_phone = ndb.StringProperty()


class UserProfile(ndb.Model):
    User = ndb.KeyProperty(kind='AccountDetails')
    Org = ndb.KeyProperty(kind='OrganizationDetails')
    # possible roles = 'dev','manager','super-dev','super-admin'
    role = ndb.StringProperty()


# org_one = OrganizationDetails(
#     org_name="CompanyOne",
#     org_phone="432423"
# )
#
#
# org_two = OrganizationDetails(
#     org_name="CompanyTwo",
#     org_phone="432434223"
# )
#
# user_data = AccountDetails(
#     first_name="TestFirst",
#     last_name="TestLast",
#     mobile_number="MN".replace(' ', ''),
#     password="1",
#     email="regson@test.com".lower(),
#     role='super-admin',
#     is_active=False,
#     is_verified=False,
#     verification_code="123"
# )
#
# user_data.organizations.append(org_one.put())
# user_data.organizations.append(org_two.put())
# user_data.put()
