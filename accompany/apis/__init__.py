from flask_restplus import Api
from .auth.api import api as auth_api
from .user.api import api as user_api
from .sample.api import api as sample_api
from .oneorder.api import api as oneorder_api
from .quadro.api import api as quadro_api



authorizations = {
    'Bearer Auth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    },
}

api = Api(version='1.0', title='Miracle Swagger', description='Miracle ApiDocs',
          prefix="/api/v1", security='Bearer Auth', authorizations=authorizations, doc="/api/v1/docs")

api.add_namespace(auth_api)
api.add_namespace(user_api)
api.add_namespace(sample_api)
api.add_namespace(oneorder_api)
api.add_namespace(quadro_api)

