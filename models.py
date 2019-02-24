from google.appengine.ext import ndb


# Account Data
class AccountDetails(ndb.Model):
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    mobile_number = ndb.StringProperty()
    password = ndb.StringProperty()
    # possible roles = 'dev','manager','super-dev','super-admin'
    role = ndb.StringProperty()
    organization = ndb.KeyProperty(kind='OrganizationDetails')
    is_active = ndb.BooleanProperty()
    is_verified = ndb.BooleanProperty()
    verification_hash = ndb.StringProperty()

    def org_name(self):
        org_object = OrganizationDetails.get_by_id(self.organization.id())
        return org_object.org_name


class OrganizationDetails(ndb.Model):
    org_name = ndb.StringProperty()
    org_phone = ndb.StringProperty()
    org_open = ndb.DateTimeProperty()
    org_close = ndb.DateTimeProperty()
