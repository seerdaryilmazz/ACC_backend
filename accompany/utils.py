import json
import sys
from concurrent import futures
from copy import deepcopy
from datetime import date, datetime
from decimal import Decimal

import requests
from flask import current_app, request
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from pymongo.errors import DuplicateKeyError
from requests.utils import default_user_agent

from accompany import counters_collection, email_collection, result_message_collection, notifications, mail, logger, \
    selected_config, sentry


class Response(object):
    def base(self, payload, result_message, result_code):
        language = get_language()
        found = result_message_collection.find_one({"_id": result_message, language: {"$exists": True}})
        if found:
            result_message = found[language]
        return json.loads(json.dumps({'payload': payload, 'result_message': result_message,
                                      'result_code': result_code}))

    def success(self, payload={}, result_message='Succeed', result_code=200):
        return self.base(payload, result_message, result_code)

    def server_error(self, payload={}, result_message='Failed', result_code=500):
        return self.base(payload, result_message, result_code)

    def client_error(self, payload={}, result_message='ClientError', result_code=400):
        return self.base(payload, result_message, result_code)


def get_sequence(sequence_name):
    if counters_collection.count_documents(filter={"_id": sequence_name}) == 0:
        create_sequence(sequence_name)
    return counters_collection.find_and_modify(query={"_id": sequence_name}
                                               , update={"$inc": {"seq": 1}}
                                               , upsert=True)["seq"]


def create_sequence(sequence_name):
    return counters_collection.insert_one({"_id": sequence_name, "seq": 1})


def notify_user(data, recipients):
    bulkNotifications = []
    try:
        for recipient in set(recipients):
            newData = deepcopy(data)
            newData['User'] = recipient
            newData['Read'] = False
            bulkNotifications.append(newData)
        notifications.insert_many(bulkNotifications)
    except Exception as exception:
        now = datetime.now()
        logger.log_to_db({'exception': exception.__repr__(), 'create_date': now})
        sentry.captureException(exc_info=sys.exc_info(), date=now)


def send_text_email(body, recipients, subject="Accompany Bildirim"):
    try:
        msg = Message(subject=subject, sender=selected_config.get('MAIL_DEFAULT_SENDER'), recipients=list(set(recipients)), body=body)
        mail.send(msg)
    except Exception as exception:
        now = datetime.now()
        logger.log_to_db({'exception': exception.__repr__(), 'create_date': now})
        sentry.captureException(exc_info=sys.exc_info(), date=now)


def generate_confirmation_token(identity):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(identity, current_app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        identity = serializer.loads(
            token,
            salt=current_app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return identity


def handle_email(sent, body, recipient, type):
    email_collection.find_one_and_update({'sent': sent, 'recipient': recipient, 'type': type},
                                         {'$set': {'sent': sent, 'body': body, 'recipient': recipient,
                                                   'type': type}},
                                         upsert=True)


def get_language():
    if request.accept_languages.best:
        split = request.accept_languages.best.split("-")
        if split[0] == "":
            return "tr"
        return split[0]
    return "tr"


def collection_paginator(collection, response, page_size, page_number):
    if page_number > 0:
        skips = page_size * (page_number - 1)
        # Sadece _id ve localizations alanlari listeleme icin yeterli
        cursor = collection.find({}, {'_id': True, 'localizations': True}).skip(skips).limit(page_size)
        total_items = cursor.count()
        number_of_pages = total_items // page_size

        if total_items % page_size != 0:
            number_of_pages = number_of_pages + 1

        if page_number > number_of_pages:
            return response.client_error([], result_message='NoSuchPage')

        next_page = None
        if total_items - (page_number * page_size) > 0:
            next_page = page_number + 1

        previous_page = None
        if page_number > 1:
            previous_page = page_number - 1

        return response.success(
            payload={'result': [x for x in cursor], 'next_page': next_page, 'current_page': page_number,
                     'previous_page': previous_page, 'number_of_pages': number_of_pages})

    return response.client_error(payload={}, result_message='NoPageNumberSupplied', result_code=400)


def json_convert_helper(obj):
    if isinstance(obj, Decimal):
        return float(obj)

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Object of type '%s' is not JSON serializable" % type(obj).__name__)


def type_helper(records):
    return list(json.loads(json.dumps(records, default=json_convert_helper)))


def register(raw, generate_password_hash, user_collection, create_access_token, response):
    raw["password"] = generate_password_hash(raw["password"])

    try:
        created = user_collection.insert_one(raw).inserted_id
        if created:
            access_token = create_access_token(identity=created)
            payload = {
                'access_token': access_token
            }
            return response.success(payload)

    except DuplicateKeyError:
        return response.client_error('UserExists')

    return response.server_error()



def create_concurrent_request(url_list, headers_list=[], json_body_list=[], method_list=[], auth="",
                              params_list=[]):
    default_headers = {
        'User-Agent': default_user_agent(),
        'Accept-Encoding': ', '.join(('gzip', 'deflate')),
        'Accept': '*/*',
        'Connection': 'keep-alive',
    }
    # monkey patch for fixing proxy

    if len(headers_list) != 0:
        default_headers = headers_list[0]
    while len(headers_list) != len(url_list) and len(headers_list) < len(url_list):
        headers_list.append(default_headers)

    while len(params_list) != len(url_list) and len(params_list) < len(url_list):
        params_list.append(None)

    while len(json_body_list) != len(url_list) and len(json_body_list) < len(url_list):
        default_json = {}
        json_body_list.append(default_json)

    while len(method_list) != len(url_list) and len(method_list) < len(url_list):
        default_method = 'GET'
        method_list.append(default_method)

    def send_concurrent_request(url, headers, json_body, method, param):
        response = None
        if method.upper() in ['POST', 'PUT', 'DELETE']:
            response = requests.request(method.upper(), url=url, json=json_body, headers=headers)

        if method.upper() == 'GET':
            response = requests.request(method.upper(), url=url, json=json_body, headers=headers, auth=auth,
                                        params=param)
        if response:
            try:
                return response.json()
            except ValueError:
                return response.text

        return None

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        res = executor.map(send_concurrent_request, url_list, headers_list, json_body_list, method_list, params_list)
    return list(res)
