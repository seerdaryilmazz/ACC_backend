import requests
import os
from accompany.apis.sample import api
from accompany.utils import Response
from flask_restplus import Resource, fields
from flask_jwt_extended import jwt_required
from flask import current_app

response = Response()

a_sample_model = api.model('SampleModel',
                           {'first_field': fields.Integer('Valid first number', required=True, example=3),
                            'second_field': fields.String('Valid second number', required=True, example=5)})


@api.route("/sum")
class Sum(Resource):
    @jwt_required
    @api.doc(description='Return sum of first_number and second_number')
    @api.expect(a_sample_model)
    def post(self):
        first_number = api.payload['first_number']
        second_number = api.payload['second_number']
        return response.success(payload={'sum': first_number + second_number})


@api.route("/another_resource")
class AnotherResource(Resource):
    def get(self):
        return response.success(result_message='You Called Me')


@api.route("/caller")
class Caller(Resource):
    def get(self):
        return current_app.test_client().get(
            '{}/sample/another_resource'.format(current_app.config['API_BASE_URL'])).json


@api.route("/exception_test")
class ExceptionTest(Resource):
    def get(self):
        raise Exception('This is my apiaccompanytest exception')
        return "OK"
