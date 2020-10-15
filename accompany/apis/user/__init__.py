from flask_restplus import Namespace

api = Namespace('user', description='User Related Endpoints', validate=True)
