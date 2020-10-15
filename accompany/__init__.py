from flask_executor import Executor
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from .config import decide_config
from flask import Flask, make_response, json as flask_json
from flask_mail import Mail
from pymongo import MongoClient, errors
from yntpy import MongoLogger, Cipher
from bson import json_util
from raven.contrib.flask import Sentry

# JWT
jwt = JWTManager()
# CORS
cors = CORS()
# Logger
logger = MongoLogger()
# Cipher
cipher = Cipher()
# Sentry
sentry = Sentry()
# Mail
mail = Mail()
executor = Executor()
client = db = user_collection = blacklist_collection = email_collection = counters_collection = \
    result_message_collection = log_collection = new_location_orders = complaints = todo_tasks = notifications = None
selected_config = None


def create_app(environment=''):
    app = Flask(__name__)
    environment_config = decide_config(environment)
    global selected_config
    selected_config = environment_config.__dict__
    app.config.from_object(environment_config)
    db_connected = create_collection_references(app.config['MONGO_URL'])
    create_collection_indexes()
    create_extensions(app, db_connected)
    return app


def create_collection_references(mongo_url):
    global client, db, user_collection, blacklist_collection, email_collection, counters_collection, \
        result_message_collection, log_collection, new_location_orders, complaints, todo_tasks, notifications
    client = MongoClient(mongo_url)
    db = client['AccompanyDB']
    user_collection = db['user']
    blacklist_collection = db['blacklist']
    email_collection = db['email']
    counters_collection = db['counters']
    result_message_collection = db['result_messages']
    log_collection = db['log_collection']
    new_location_orders = db['new_location_orders']
    complaints = db['complaints']
    todo_tasks = db['todo_tasks']
    notifications = db['notifications']
    try:
        client.server_info()
        return db
    except errors.ServerSelectionTimeoutError:
        raise Exception("Server Selection Timeout Error")


def create_extensions(app, db_connected):
    from accompany.apis import api
    api.init_app(app)
    register_json_representation(api)
    cors.init_app(app)
    jwt.init_app(app)
    jwt._set_error_handler_callbacks(api)
    mail.init_app(app)
    executor.init_app(app)
    logger.init_api(api)
    logger.init_mongo_logger(db_connected['log_collection'])
    logger.initialize_app_handlers()
    cipher.init_app(app.config['CIPHER_KEY'])
    if app.config['SENTRY_URL'] != '':
        sentry.init_app(app=app, dsn=app.config['SENTRY_URL'])
    setup_jwt()


def create_collection_indexes():
    if todo_tasks.index_information().get('TaskNumber') is None:
        todo_tasks.create_index([('TaskNumber', 1)], unique=True, name="TaskNumber")


def register_json_representation(api):
    @api.representation('application/json')
    def output_json(data, code, headers=None):
        resp = make_response(flask_json.dumps(data, default=json_util.default), code)
        resp.headers.extend(headers or {})
        return resp


def setup_jwt():
    # Create blacklist
    blacklist_collection.create_index("insertedAt", expireAfterSeconds=3600)

    from .utils import Response
    # This decorator sets the callback function that will be called
    # when a protected  endpoint is accessed and will
    # check if the JWT has been been revoked.
    @jwt.token_in_blacklist_loader
    def blacklisted(token):
        jti = token['jti']
        return blacklist_collection.find_one({'token': jti})

    # Using the expired_token_loader decorator, we will now call
    # this function whenever an expired but otherwise valid access
    # token attempts to access an endpoint
    @jwt.expired_token_loader
    def expired():
        return Response().client_error(result_message="TokenExpired", result_code=401), 200

    # This decorator sets the callback function that will be called if no
    # JWT can be found when attempting to access a protected endpoint.
    # The default implementation will return a 401 status code with the JSON:
    @jwt.unauthorized_loader
    def unauthorized(reason):
        return Response().client_error(result_message="NoTokenInHeader", result_code=401), 200

    # This decorator sets the callback function that will be called when
    # a protected endpoint is accessed and will check if the JWT
    # has been been revoked. By default, this callback is not used.
    @jwt.revoked_token_loader
    def revoke():
        return Response().client_error(result_message="RevokedToken", result_code=401), 200

    @jwt.invalid_token_loader
    def invalid(reason):
        return Response().client_error(result_message="InvalidToken", result_code=401), 200
