import json
import requests

from accompany import selected_config
from .model import *
from requests.auth import HTTPBasicAuth
from flask import current_app, request, redirect, url_for
from datetime import date, timedelta

auth = HTTPBasicAuth(selected_config['ONEORDER_API_USERNAME'], selected_config['ONEORDER_API_PASSWORD'])


def create_header():
    x_behalf_of_value = request.headers.get('X-On-Behalf-Of')
    x_user = request.headers.get('X-User')
    header = {'X-On-Behalf-Of': x_behalf_of_value, 'X-User': x_user}
    return header


def get(url):
    return requests.get(url, headers=create_header(), auth=auth)


def post(url, data=None, json=None, **kwargs):
    response = requests.post(url, json=json, headers=create_header(), auth=auth)
    return response


class OneorderBusiness:
    def __init__(self, oneorder_api_url):
        self.oneorder_api_url=oneorder_api_url

    def get_user_information(self, getAllSubhierarchy):
        response = get(self.oneorder_api_url + '/authorization-service/auth/user/sublevel-users?getSubhierarchy=' + getAllSubhierarchy)
        return response.json()

    def get_accounts_by_owners(self, accountOwnerNames):
        accounts = post(self.oneorder_api_url + '/crm-account-service/account/byAccountOwners', json=accountOwnerNames)
        accountList = list(map(lambda account: json.loads(Account().make_account(account)), accounts.json()))
        return accountList


