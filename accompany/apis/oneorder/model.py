import json


class Account:
    def __init__(self, AccountCompanyId="", AccountName="", AccountSectorName="",AccountId="",CompanyDefaultLocationPhoneNumber="", AccountOwner=""):
        self.AccountCompanyId = AccountCompanyId
        self.AccountName = AccountName
        self.AccountSectorName = AccountSectorName
        self.AccountId = AccountId
        self.CompanyDefaultLocationPhoneNumber = CompanyDefaultLocationPhoneNumber
        self.AccountOwner = AccountOwner

    def make_account(self, json_object):
        self.AccountCompanyId = json_object['company']['id']
        self.AccountName = json_object['name']
        self.AccountSectorName = json_object['parentSector']['name']
        self.AccountId = json_object["id"]
        self.AccountOwner = json_object["accountOwner"]

        return self.toJSON()

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


class CompanyAndCompanyLocation:
    def __init__(self, CompanyId="", CompanyName="", CompanySector="", CompanyStatus="", CompanyCountry="",
                 CompanyContacts="", Company="", CompanyLocation="", CompanyServiceTypes=""):
        self.CompanyId = CompanyId
        self.CompanyName = CompanyName
        self.CompanySector = CompanySector
        self.CompanyStatus = CompanyStatus
        self.CompanyCountry = CompanyCountry
        self.CompanyContacts = CompanyContacts
        self.CompanyLocation = CompanyLocation
        self.Company = Company

    def make_company_and_company_location(self, json_object, locationId):
        self.Company = json_object
        self.CompanyId = json_object['id']
        self.CompanyName = json_object['name']
        companySector = json_object['sectors'][0]['sector']
        self.CompanySector = companySector['name'] if companySector['name'] != "No-Subsector" else companySector['parent']['name']
        location = next((x for x in json_object['companyLocations'] if x['id'] == int(locationId)), None)
        self.CompanyLocation = location
        # self.CompanyServiceTypes = location['companyServiceTypes']
        locationContacts = [x for x in json_object['companyContacts'] if x['companyLocation']['id'] == int(locationId)]

        if location['active']:
            self.CompanyStatus = "Aktif"
        else:
            self.CompanyStatus = "Pasif"
        self.CompanyCountry = location['postaladdress']['country']['countryName']
        self.CompanyContacts = locationContacts
        return self.toJSON()

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


class Company:
    def __init__(self, CompanyId="", CompanyName="", CompanySector="", CompanyContacts="", Company="", CompanyLocations="",):
        self.CompanyId = CompanyId
        self.CompanyName = CompanyName
        self.CompanySector = CompanySector
        self.CompanyContacts = CompanyContacts
        self.CompanyLocations = CompanyLocations
        self.Company = Company

    def make_company(self, json_object):
        self.Company = json_object
        self.CompanyId = json_object['id']
        self.CompanyName = json_object['name']
        companySector = next((sc for sc in json_object['sectors'] if sc['default'] is True))['sector']
        self.CompanySector = companySector['name'] if companySector['name'] != "No-Subsector" else companySector['parent']['name']
        self.CompanyLocations = json_object['companyLocations']
        self.CompanyContacts = json_object['companyContacts']
        return self.toJSON()

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


