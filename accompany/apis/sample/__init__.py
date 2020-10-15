from flask_restplus import Namespace

api = Namespace('sample', description='Sample Endpoints', validate=True)
