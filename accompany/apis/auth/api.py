import requests
import json
from accompany import user_collection, blacklist_collection
from accompany.apis.auth import api
from accompany.utils import Response, generate_confirmation_token, handle_email, confirm_token, register
from accompany.enums import EmailTypes
from flask import current_app, redirect, request, g
from flask_jwt_extended import create_access_token, jwt_required, get_raw_jwt, get_jwt_identity, \
    jwt_refresh_token_required, create_refresh_token, fresh_jwt_required
from flask_restplus import Resource, fields
from pymongo.errors import DuplicateKeyError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from accompany import logger, cipher

a_login_user = api.model('AuthModel',
                         {'_id': fields.String('Valid username', required=True, example="cokomel", min_length=3),
                          'password': fields.String('Valid password', required=True, example="123456", min_length=3)})

response = Response()

@logger.register()
@api.route("/login")
class Login(Resource):
    @api.expect(a_login_user, validate=True)
    def post(self):
        raw = api.payload
        found = user_collection.find_one({'_id': raw["_id"]})
        if found and check_password_hash(found['password'], raw["password"]):
            access_token = create_access_token(identity=found["_id"], fresh=True)
            refresh_token = create_refresh_token(identity=found["_id"])
            payload = {
                'access_token': access_token,
                'refresh_token': refresh_token
            }
            return response.success(payload)

        return response.client_error(result_message='Kullanıcı adı ve parolayla eşleşen bir hesap bulunamadı.')

@logger.register()
@api.route("/register")
class Register(Resource):
    @api.expect(a_login_user)
    def post(self):
        raw = api.payload
        raw["password"] = generate_password_hash(raw["password"])
        raw["insertedAt"] = datetime.utcnow()
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


# Endpoint for revoking the current users access token
# TODO: Also revoke refresh token when refresh implemented
@logger.register()
@api.route("/logout")
class Logout(Resource):
    @jwt_required
    def delete(self):
        blacklist_collection.insert_one({'insertedAt': datetime.utcnow(), 'token': get_raw_jwt()['jti']})
        return response.success()

@logger.register()
@api.route("/check_user_is_admin")
class UserCheck(Resource):
    @jwt_required
    def get(self):
        identity = get_jwt_identity()
        found_user = user_collection.find_one({'_id': identity})

        if found_user and 'is_admin' in found_user :
            return response.success(payload={'is_admin':found_user['is_admin'],'admin_mail':found_user['admin_mail']})
        else:
            return response.server_error()



# TODO: Revoke old token and force to re-login OR refresh current access token
@logger.register()
@api.route("/reset_password")
class ResetPassword(Resource):
    @jwt_required
    def post(self):
        raw = api.payload
        identity = get_jwt_identity()
        if raw["password"] == raw["confirmPassword"]:
            found = user_collection.find_one({'_id': identity})
            if check_password_hash(found['password'], raw["oldPassword"]):
                if user_collection.update({'_id': identity},
                                          {'$set': {'password': generate_password_hash(raw["password"])}}):
                    return response.success()
            return response.client_error(result_message='WrongOldPassword.')
        return response.client_error(result_message='PasswordMismatch')

@logger.register()
@api.route("/request_password")
class RequestPassword(Resource):
    def post(self):
        raw = api.payload
        identity = get_jwt_identity()
        found = user_collection.find_one({'email': raw["email"]})
        if found:
            reset_url = "{}{}{}".format(current_app.config['WEB_CLIENT'], "auth/reset-password/",
                                        generate_confirmation_token(identity))
            handle_email(0, reset_url, raw["email"], EmailTypes.ResetPassword)
            return response.success()
        return response.client_error(result_message='Kullanıcı adı ve parolayla eşleşen bir hesap bulunamadı.')

    def put(self):
        raw = api.payload
        identity = get_jwt_identity()
        if confirm_token(identity):
            if raw["password"] == raw["confirmPassword"]:
                if user_collection.update({'_id': identity},
                                          {'$set': {'password': generate_password_hash(raw["password"])}}):
                    return response.success()
            return response.client_error(result_message='PasswordMismatch')
        return response.client_error(result_message='Expired')

@logger.register()
@api.route("/refresh")
class RefreshToken(Resource):
    @jwt_refresh_token_required
    def post(self):
        identity = get_jwt_identity()
        payload = {'access_token': create_access_token(identity, fresh=False)}
        return response.success(payload=payload)


# Sample usage of fresh token pattern: when user logged in, her first token is marked as fresh=True
# When user refresh her token with using refresh token, new token is marked as fresh=False.
# Example:
# This is useful for allowing fresh tokens to do some critical things (such as update an email address)
# but to deny those features to non-fresh tokens.
@logger.register()
@api.route("/fresh_ping")
class FreshPing(Resource):
    # @fresh_jwt_required
    def get(self):
        r = current_app.test_client().get('http://127.0.0.1:5000/api/v1/auth/fresh_ping2')

        return response.success(result_message="YouGotFreshRefreshToken")


@logger.register()
@api.route("/google_signin")
class OAuthLogin(Resource):
    def get(self):
        client_callback_url = cipher.encrypt(current_app.config['MY_CALLBACK_URL'])
        redirect_url = '{}?client_callback_url={}'.format(current_app.config['GOOGLE_AUTH_API_URL'],
                                                          client_callback_url)
        return redirect(redirect_url)

@logger.register()
@api.route("/on_google_succeed")
class OAuthLogin(Resource):
    def get(self):
        is_successful_callback = False
        print(request.args)
        if request.args.get('success', default=False):
            is_successful_callback = request.args.get('success')

        # Redirect to register screen in case of callback failure
        if not bool(is_successful_callback):
            return redirect(
                '{}/register?message={}'.format(current_app.config['WEB_CLIENT'], 'Failed'))

        callback_response = requests.post(url='{}'.format(current_app.config['IDENTITY_SERVER_VALIDATION_URL']),
                                          json={'id_token': request.args.get('id_token')})

        print("callback", callback_response.json())

        if callback_response.status_code == 200 and 'payload' in callback_response.json():
            try:
                payload = json.loads(cipher.decrypt(callback_response.json()['payload']))
                print(payload)
                g.user_email = payload['email']
                # TODO: Write your logic. I.e. register user, ask for password for new users etc.
                if user_collection.find_one({'_id': payload['email']}):
                    access_token = create_refresh_token(identity=payload['email'])
                    return redirect(
                        '{}/auth/google_result?t={}&e={}'.format(current_app.config['WEB_CLIENT'], access_token,
                                                                 payload['email']))
                # return redirect(
                #     '{}/register?message={}'.format(current_app.config['WEB_CLIENT'], 'No such user'))
                else:
                    raw = {'_id': payload['email'], 'password': '123456' , 'is_admin':False}
                    register_response = register(raw=raw, generate_password_hash=generate_password_hash, user_collection=user_collection,
                             create_access_token=create_access_token, response=response)

                    if(register_response['result_code'] == 200):
                        access_token = create_refresh_token(identity=payload['email'])
                        return redirect(
                            '{}/auth/google_result?t={}&e={}'.format(current_app.config['WEB_CLIENT'], access_token,
                                                                     payload['email']))

                # Redirect to register screen in case of validation failure
            except KeyError as err:
                return redirect(
                    '{}/register?t={}'.format(current_app.config['WEB_CLIENT'], "Couldn't validate: {}".format(err)))
