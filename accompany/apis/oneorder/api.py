from io import BytesIO
import requests
from flask_jwt_extended import jwt_required
from accompany.apis.oneorder import api
from .business import OneorderBusiness
from accompany.utils import Response, create_concurrent_request
from flask_restplus import Resource
from requests.auth import HTTPBasicAuth
from .model import *
import json
from flask import current_app, request, send_file
from accompany import logger, selected_config
from datetime import datetime as dt


server_response = Response()
oneorder_business = OneorderBusiness(selected_config['ONEORDER_API_URL'])
auth = HTTPBasicAuth(selected_config['ONEORDER_API_USERNAME'], selected_config['ONEORDER_API_PASSWORD'])


def create_header():
    x_behalf_of_value = request.headers.get('X-On-Behalf-Of')
    x_user = request.headers.get('X-User')
    header = {'X-On-Behalf-Of': x_behalf_of_value, 'X-User': x_user}
    return header


@logger.register()
@api.route("/get_my_information")
class GetMyInformation(Resource):
    @jwt_required
    @api.doc(description='Get user information by token')
    def get(self):
        getAllSubhierarchy = request.args.get('getAllSubhierarchy', default=True)
        return oneorder_business.get_user_information(getAllSubhierarchy)


@logger.register()
@api.route("/getUserCalendar/<string:username>")
@api.route("/getUserCalendar/<string:username>/<string:accountId>")
class GetUserCalendar(Resource):
    # jwt_required
    @api.doc(description='Get user information by token')
    def get(self, username, accountId=None):
        response = requests.get(
            current_app.config['ONEORDER_API_URL'] + '/crm-activity-service/activity/search?pageSize=100&username=' + username,
            headers=create_header(),
            auth=auth)
        visitList = []
        if accountId != None:
            visits = response.json()['content']
            for visit in visits:
                visitAccountId = json.dumps(visit['account']['id'])
                if visitAccountId == accountId:
                    visitList.append(visit)
            return visitList
        else:
            return json.loads(response.content)

@logger.register()
@api.route("/getInternalParticipants")
class GetInternalParticipants(Resource):
    @jwt_required
    @api.doc(description='Get user information by token')
    def get(self):
        response = requests.get(current_app.config['ONEORDER_API_URL'] + '/user-service/users/list',
                                headers=create_header(),
                                auth=auth)
        return json.loads(response.content)

@logger.register()
@api.route("/getCalendarEventById/<string:id>")
class GetCalendarEventById(Resource):
    @jwt_required
    @api.doc(description='Get user calendar types')
    def get(self, id):
        response = requests.get(
            current_app.config['ONEORDER_API_URL'] + '/crm-activity-service/activity/' + id,
            headers=create_header(),
            auth=auth)
        return json.loads(response.content)


@logger.register()
@api.route("/get_company_by_id/<string:id>")
class GetCompanyById(Resource):
    @jwt_required
    @api.doc(description='Get translation by language key')
    def get(self, id):
        response = requests.get(current_app.config['ONEORDER_API_URL'] + '/kartoteks-service/company/' + id,
                                headers=create_header(),
                                auth=auth)
        return json.loads(Company().make_company(response.json()))


@logger.register()
@api.route("/get_company_location_by_id/<string:id>/<string:locationId>")
class GetCompanyById(Resource):
    @jwt_required
    @api.doc(description='Get translation by language key')
    def get(self, id, locationId):
        response = requests.get(current_app.config['ONEORDER_API_URL'] + '/kartoteks-service/company/' + id,
                                headers=create_header(),
                                auth=auth)
        return json.loads(CompanyAndCompanyLocation().make_company_and_company_location(response.json(), locationId))


@logger.register()
@api.route("/get_company_locations_by_id/<string:id>")
class GetCompanyById(Resource):
    @jwt_required
    @api.doc(description='Get translation by language key')
    def get(self, id):
        response = requests.get(current_app.config['ONEORDER_API_URL'] + '/kartoteks-service/company/' + id,
                                headers=create_header(),
                                auth=auth)
        return response.json()['companyLocations']

@logger.register()
@api.route("/getCompanyContacts/<string:id>")
class GetCompanyContacts(Resource):
    @jwt_required
    @api.doc(description='Get translation by language key')
    def get(self, id):
        response = requests.get(current_app.config['ONEORDER_API_URL'] + '/kartoteks-service/company/' + id + '/contacts',
                                headers=create_header(),
                                auth=auth)
        return response.json()


@logger.register()
@api.route("/getAccountContacts/<string:id>")
class GetCompanyContacts(Resource):
    @jwt_required
    @api.doc(description='Get account contacts by account id')
    def get(self, id):
        response = requests.get(current_app.config['ONEORDER_API_URL'] + '/crm-account-service/contact/byAccount/' + id,
                                headers=create_header(),
                                auth=auth)
        return response.json()


@logger.register()
@api.route("/get_accounts_by_query")
class GetCompanyById(Resource):
    @jwt_required
    @api.doc(description='Get accounts by query')
    def get(self):
        name = request.args.get('name')
        page = request.args.get('page')
        pageSize = request.args.get('pageSize')
        accountOwner = request.args.get('accountOwner')

        query = "?page=" + page + "&pageSize=" + pageSize
        if accountOwner is not None:
            query += "&accountOwner=" + accountOwner
        if name is not None:
            query += "&name=" + name

        response = requests.get(
            current_app.config[
                'ONEORDER_API_URL'] + '/crm-account-service/account/search' + query,
            headers=create_header(),
            auth=auth)
        total_count = response.json()['totalElements']
        accountList = []
        urls = []
        for x in response.json()['content']:
            accountList.append(json.loads(Account().make_account(x)))
            urls.append(current_app.config['ONEORDER_API_URL'] + '/kartoteks-service/company/' + str(
                        x['company']['id']) + '/default-location')

        responseList = create_concurrent_request(urls, [create_header()], auth=auth)

        for defaultLocation in responseList:
            if defaultLocation and defaultLocation['company'] is not None:
                account = next((x for x in accountList if x['AccountCompanyId'] == defaultLocation['company']['id']),
                               None)
                if account is not None:
                    if len(defaultLocation['phoneNumbers']) > 0:
                        phoneNumber = defaultLocation['phoneNumbers'][0]['phoneNumber']
                        account['CompanyDefaultLocationPhoneNumber'] = "+" + str(phoneNumber['countryCode']) + str(
                            phoneNumber['regionCode']) + str(phoneNumber['phone'])
        return {"AccountList": accountList, "TotalCount": total_count}


@logger.register()
@api.route("/get_accounts_by_account_owner_name_for/<string:accountOwnerName>")
class GetAccountsByOwner(Resource):
    # @jwt_required
    @api.doc(description='Get translation by language key')
    def get(self, accountOwnerName):
        response = requests.get(
            current_app.config[
                'ONEORDER_API_URL'] + '/crm-account-service/account/byAccountOwner?accountOwner=' + accountOwnerName,
            headers=create_header(),
            auth=auth)
        accountList = []
        for x in response.json():
            accountList.append(json.loads(Account().make_account(x)))
        return accountList


@logger.register()
@api.route("/get_accounts_by_query")
class GetAccountsByOwners(Resource):
    @api.doc(description='Get translation by language key')
    def post(self):
        response = requests.post(current_app.config['ONEORDER_API_URL'] + "/crm-search-service/search/searchAccounts",
                                 json=api.payload,
                                 headers=create_header(),
                                 auth=auth)
        accountList = list(map(lambda account: json.loads(Account().make_account(account)), response.json()['content']))
        return accountList


@logger.register()
@api.route("/get_all_parameters")
class GetCompanyById(Resource):
    # jwt_required
    @api.doc(description='Get translation by language key')
    def get(self):
        urls = [current_app.config['ONEORDER_API_URL'] + '/kartoteks-service/contact-department',
                current_app.config['ONEORDER_API_URL'] + '/kartoteks-service/contact-title',
                current_app.config['ONEORDER_API_URL'] + '/kartoteks-service/business-segment-type',
                current_app.config['ONEORDER_API_URL'] + '/crm-activity-service/lookup/activity-scope',
                current_app.config['ONEORDER_API_URL'] + '/crm-activity-service/lookup/activity-tool',
                current_app.config['ONEORDER_API_URL'] + '/kartoteks-service/phone-type',
                current_app.config['ONEORDER_API_URL'] + '/kartoteks-service/usage-type',
                current_app.config['ONEORDER_API_URL'] + '/crm-activity-service/lookup/activity-type',
                current_app.config['ONEORDER_API_URL'] + '/user-service/users/list',
                current_app.config['ONEORDER_API_URL'] + '/note-service/lookup/note-type',
                current_app.config['ONEORDER_API_URL'] + '/crm-account-service/lookup/country',
                ]

        responseList = create_concurrent_request(urls, [create_header()], auth=auth)

        return {"ContactDepartments": responseList[0],
                "ContactTitles": responseList[1],
                "BusinessSegmentTypes": responseList[2],
                "ActivityScopes": responseList[3],
                "ActivityTools": responseList[4],
                "PhoneTypes": responseList[5],
                "UsageTypes": responseList[6],
                "CalendarEventTypes": responseList[7],
                "CalendarSegmentTypes": responseList[2],
                "UserList": responseList[8],
                "NoteTypes": responseList[9],
                "Countries": responseList[10],
                }


@logger.register()
@api.route("/createActivity")
class CreateActivity(Resource):
    @jwt_required
    @api.doc(description='Create activity')
    def post(self):
        taskNumber = request.args.get('task', default=None)
        url = '/crm-activity-service/activity'
        if taskNumber:
            url += '?task=' + taskNumber

        response = requests.post(current_app.config['ONEORDER_API_URL'] + url,
                                 json=api.payload,
                                 headers=create_header(),
                                 auth=auth)
        if response:
            return server_response.success()
        else:
            return server_response.server_error(result_message=response.json())


@logger.register()
@api.route("/updateActivity/<string:eventid>")
class GetCompanyById(Resource):
    @jwt_required
    @api.doc(description='Get translation by language key')
    def post(self, eventid):
        response = requests.put(current_app.config['ONEORDER_API_URL'] + '/crm-activity-service/activity/' + eventid,
                                json=api.payload,
                                headers=create_header(),
                                auth=auth)
        if response:
            return server_response.success()
        else:
            return server_response.server_error(result_message=response.json())


@logger.register()
@api.route("/save_contact_to_location")
class SaveContactToLocation(Resource):
    # @jwt_required
    @api.doc(description='Get translation by language key')
    def post(self):

        validateResponse = requests.put(current_app.config['ONEORDER_API_URL'] + '/kartoteks-service/contact/validate',
                                        json=api.payload, headers=create_header(),
                                        auth=auth)

        if validateResponse.status_code == 200:
            contactSaveResponse = requests.post(current_app.config['ONEORDER_API_URL'] + '/kartoteks-service/contact/',
                                                json=api.payload, headers=create_header(),
                                                auth=auth)
            if contactSaveResponse.status_code == 200:
                contactSaveResponseJSON = contactSaveResponse.json()
                accountResponse = requests.get(
                    current_app.config['ONEORDER_API_URL'] + '/crm-account-service/account/byCompany?companyId=' + str(
                        api.payload['company']['id']), headers=create_header(),
                    auth=auth)
                crmContactSaveRequest = {"account": accountResponse.json(),
                                         "companyContactId": contactSaveResponseJSON['id'],
                                         "firstName": contactSaveResponseJSON['firstName'],
                                         "lastName": contactSaveResponseJSON['lastName']}
                crmContactSaveResponse = requests.post(
                    current_app.config['ONEORDER_API_URL'] + '/crm-account-service/contact/' + str(
                        accountResponse.json()['id']),
                    json=crmContactSaveRequest, headers=create_header(),
                    auth=auth)
                if crmContactSaveResponse.status_code == 200:
                    return server_response.success()

        return server_response.server_error()


@logger.register()
@api.route("/edit_contact")
class SaveContactToLocation(Resource):
    # @jwt_required
    @api.doc(description='Get translation by language key')
    def post(self):

        validateResponse = requests.put(current_app.config['ONEORDER_API_URL'] + '/kartoteks-service/contact/validate',
                                        json=api.payload, headers=create_header(),
                                        auth=auth)

        if validateResponse.status_code == 200:
            contactSaveResponse = requests.put(
                current_app.config['ONEORDER_API_URL'] + '/kartoteks-service/contact/' + str(api.payload['id']),
                json=api.payload, headers=create_header(),
                auth=auth)

            if contactSaveResponse.status_code == 200:
                contactSaveResponseJSON = contactSaveResponse.json()
                accountResponse = requests.get(
                    current_app.config['ONEORDER_API_URL'] + '/crm-account-service/account/byCompany?companyId=' + str(
                        api.payload['company']['id']), headers=create_header(),
                    auth=auth)
                crmContactSaveRequest = {"account": accountResponse.json(),
                                         "companyContactId": contactSaveResponseJSON['id'],
                                         "firstName": contactSaveResponseJSON['firstName'],
                                         "lastName": contactSaveResponseJSON['lastName']}
                crmContactSaveResponse = requests.post(
                    current_app.config['ONEORDER_API_URL'] + '/crm-account-service/contact/' + str(
                        accountResponse.json()['id']),
                    json=crmContactSaveRequest, headers=create_header(),
                    auth=auth)
                if crmContactSaveResponse.status_code == 200:
                    return server_response.success()
        return server_response.server_error()


@logger.register()
@api.route("/get_dashboard_account_and_calendar_counts_by_account_owner_name/<string:username>")
class GetAccountAndCalendarCounts(Resource):
    @jwt_required
    @api.doc(description='Get account and calendar counts by username')
    def get(self, username):
        urls = [current_app.config[
                    'ONEORDER_API_URL'] + '/crm-account-service/account/byAccountOwner?accountOwner=' + username,
                current_app.config['ONEORDER_API_URL'] + '/crm-activity-service/activity/search?username=' + username]

        responseList = create_concurrent_request(urls, [create_header()], auth=auth)
        calendarSize = 0
        if responseList[1] != None:
            for calendar in responseList[1]['content']:
                if calendar["calendar"] != None and calendar["calendar"]['status']['id'] != "EXPIRED":
                    calendarSize = calendarSize + 1

        accountSize = responseList[0]
        model = {
            "AccountSize": len(accountSize),
            "CalendarSize": calendarSize
        }
        return model


@logger.register()
@api.route("/DeleteContact/<string:contactId>")
class ExpenseOrders(Resource):
    # @jwt_required
    @api.doc(description='DeleteContact,send contact id as string')
    def delete(self, contactId):
        deleteContact = requests.delete(
            current_app.config['ONEORDER_API_URL'] + '/kartoteks-service/contact/' + contactId
            , headers=create_header(),
            auth=auth)
        if deleteContact:
            return server_response.success()
        else:
            return server_response.server_error()


@logger.register()
@api.route("/DeleteActivity/<string:activityid>")
class ExpenseOrders(Resource):
    # @jwt_required
    @api.doc(description='Delete Activity,send activity id as string')
    def delete(self, activityid):
        deleteActivity = requests.delete(
            current_app.config['ONEORDER_API_URL'] + '/crm-activity-service/activity/' + activityid
            , headers=create_header(),
            auth=auth)
        if deleteActivity:
            return server_response.success()
        else:
            return server_response.server_error(result_message=deleteActivity.json())


@logger.register()
@api.route("/validate_calendar")
class ExpenseOrders(Resource):
    # @jwt_required
    @api.doc(description='Validates activity')
    def post(self):
        isValidated = requests.post(
            current_app.config[
                'ONEORDER_API_URL'] + '/crm-activity-service/activity/validate-calendar',
            json=api.payload, headers=create_header(), auth=auth)
        if isValidated:
            return server_response.success()
        else:
            return isValidated.json()


@logger.register()
@api.route("/update_activity_status/<string:activityid>/<string:status>")
class ExpenseOrders(Resource):
    # @jwt_required
    @api.doc(description='Updates activity status')
    def get(self, activityid, status):
        updatedActivity = requests.patch(
            current_app.config[
                'ONEORDER_API_URL'] + '/crm-activity-service/activity/' + activityid + '/status/' + status,
            headers=create_header(), auth=auth)
        if updatedActivity:
            return server_response.success()
        else:
            return server_response.server_error(result_message=updatedActivity.json())


@logger.register()
@api.route("/update_notes_activity/<string:activityId>")
class ExpenseOrders(Resource):
    # @jwt_required
    @api.doc(description='Updated notes of activity')
    def post(self, activityId):
        updatedActivity = requests.put(
            current_app.config[
                'ONEORDER_API_URL'] + '/crm-activity-service/activity/' + activityId + '/notes',
            json=api.payload, headers=create_header(), auth=auth)
        return updatedActivity.json()


@logger.register()
@api.route("/save_note/")
@api.route("/save_note/<string:noteId>")
class ExpenseOrders(Resource):
    # @jwt_required
    @api.doc(description='Saves note')
    def post(self, noteId=None):
        if noteId:
            note = requests.put(
                current_app.config[
                    'ONEORDER_API_URL'] + '/note-service/note/' + str(noteId),
                json=api.payload, headers=create_header(), auth=auth)
        else:
            note = requests.post(
                current_app.config[
                    'ONEORDER_API_URL'] + '/note-service/note/',
                json=api.payload, headers=create_header(), auth=auth)
        return note.json()


@logger.register()
@api.route("/get_note/<string:noteId>")
class GetActivity(Resource):
    @jwt_required
    @api.doc(description='Get note by note id')
    def get(self, noteId):
        note = requests.get(
            current_app.config['ONEORDER_API_URL'] + '/note-service/note/' + noteId,
            headers=create_header(), auth=auth)
        return note.json()


@logger.register()
@api.route("/get_related_activity_by_task/<string:taskNumber>")
class GetActivity(Resource):
    @jwt_required
    @api.doc(description='Get related activity to task')
    def get(self, taskNumber):
        activity = requests.get(
            current_app.config['ONEORDER_API_URL'] +
            '/crm-activity-service/activity/search?activityAttributeKey=task&activityAttributeValue=' +
            taskNumber, headers=create_header(), auth=auth)
        return activity.json()['content']


@logger.register()
@api.route("/get_agreements_by_accountId")
class GetCompanyById(Resource):
    # jwt_required
    @api.doc(description='Get agreements by account')
    def post(self):
        raw = api.payload
        accountId = raw.get('accountId')
        page = raw.get('page')
        size = raw.get('size')
        agreements = requests.get(current_app.config['ONEORDER_API_URL'] +
                                  "/agreement-service/agreement/list-by-accountId",
                                  params={'accountId': accountId},
                                  headers=create_header(), auth=auth)
        return agreements.json()


@logger.register()
@api.route("/download_file/<string:id>")
class GetCompanyById(Resource):
    # jwt_required
    @api.doc(description='Download by document id')
    def get(self, id):
        response = requests.get(current_app.config['ONEORDER_API_URL'] +
                                "/file-service/" + id + "/download",
                                params={"contentDisposition": "inline"},
                                headers=create_header(), auth=auth)
        return send_file(BytesIO(response.content), mimetype=response.headers['Content-Type'])


@logger.register()
@api.route("/get_opportunities_by_query")
class GetCompanyById(Resource):
    @jwt_required
    @api.doc(description='Get opportunities by query')
    def post(self):
        opportunities = requests.post(current_app.config['ONEORDER_API_URL'] +
                                      "/crm-search-service/search/searchOpportunitiesForHomePage",
                                      json=api.payload, headers=create_header(), auth=auth)
        return opportunities.json()['content']


@logger.register()
@api.route("/get_opportunity/<string:id>")
class GetCompanyById(Resource):
    @jwt_required
    @api.doc(description='Get opportunities by id')
    def get(self, id):
        opportunity = requests.get(current_app.config['ONEORDER_API_URL'] +
                                   "/crm-opportunity-service/opportunity/" + id,
                                   headers=create_header(), auth=auth)
        return opportunity.json()


@logger.register()
@api.route("/get_quotes_by_query")
class GetAccountsByOwners(Resource):
    @jwt_required
    @api.doc(description='Get quotes by query')
    def post(self):
        response = requests.post(current_app.config['ONEORDER_API_URL'] + "/crm-search-service/search/searchQuotes",
                                 json=api.payload,
                                 headers=create_header(),
                                 auth=auth)
        return response.json()['content']

