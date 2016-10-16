from google.appengine.ext import db


class RentalAgreement(db.Model):
    address = db.StringProperty(required=True)
    tenants = db.StringProperty(required=True)
    emails = db.StringProperty(required=True)
    names = db.StringProperty(required=True)
    phone_number = db.StringProperty(required=True)
    landlord = db.StringProperty(required=True)