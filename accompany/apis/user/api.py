import json

from bson import ObjectId
from flask import request, current_app

from accompany import user_collection, notifications
from accompany.apis.user import api
from accompany.utils import Response
from flask_restplus import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

response = Response()


@api.route("/me")
class Me(Resource):
    @jwt_required
    @api.doc(description='Get user information by token')
    def get(self):
        identity = get_jwt_identity()
        found = user_collection.find_one({'_id': identity}, {'password': False})
        if found:
            return response.success(payload=found)
        return response.client_error()


@api.route("/notifications")
class Notifications(Resource):
    @jwt_required
    @api.doc(description='Get user notifications')
    def get(self):
        x_behalf_of_value = request.headers.get('X-On-Behalf-Of')
        nots = list(notifications.find({'User': x_behalf_of_value}))
        return nots


@api.route("/read_notifications")
class Notifications(Resource):
    @jwt_required
    @api.doc(description='Read notifications')
    def get(self):
        x_behalf_of_value = request.headers.get('X-On-Behalf-Of')
        notificationId = request.args.get('notificationId')
        print(notificationId)
        try:
            if notificationId is not None:
                notifications.update_one({'_id': ObjectId(notificationId)}, {'$set': {'Read': True}})
            else:
                notifications.update_many({'User': x_behalf_of_value}, {'$set': {'Read': True}})
            return response.success()
        except Exception as exception:
            return response.server_error("Sunucuda bir hata oluştu",
                                         result_message="Exception: " + exception.__str__())

