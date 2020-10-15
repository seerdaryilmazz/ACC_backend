from flask_restplus import Namespace

api = Namespace('auth', description='Auth Endpoints', validate=True)
