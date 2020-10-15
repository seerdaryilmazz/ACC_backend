from datetime import timedelta


class Config(object):
    DEBUG = True
    SECRET_KEY = b'H0\x9e\xdf\xd7\x19\x06tz\xfe\xdc\xd7\xc9>&`g\x8c\x1a\x8b\xb6p\xe5D'
    JWT_ERROR_MESSAGE_KEY = "result_message"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=10000)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_SECRET_KEY = b':\xfc\xed3\xac\x1b\xdef7\x8e\xb2\xc9\x0b\x1e<\x0egL\x08gA\xa19\xa4'
    SECURITY_PASSWORD_SALT = b'l?\xb5m~\xb9\xdd\x80e\xbdO?\x1a)`\xffq+\x8b.k\xf3eV'
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    WEB_CLIENT = 'http://localhost:4200'
    CIPHER_KEY = b'64B4h-3Nrw6ep_8zyEkqzr4Xzb_3jTqo29gkaRLmjbY='
    MY_CALLBACK_URL = 'http://127.0.0.1:5000/api/v1/auth/on_google_succeed'
    GOOGLE_AUTH_API_URL = 'https://access.ekol.com/api/google_oauth2/login_with_google'
    IDENTITY_SERVER_VALIDATION_URL = 'https://access.ekol.com/api/google_oauth2/validate'
    JSON_AS_ASCII = False
    API_BASE_URL = 'http://127.0.0.1:5000/api/v1'
    USER_EMAIL = ''
    QUADRO_API_URL = 'http://10.5.20.7/api/accompany/getOrders/'
    ONEORDER_API_URL = 'https://oneorder-test.ekol.com:8443'
    ONEORDER_API_USERNAME = 'accompany'
    ONEORDER_API_PASSWORD = 'accompany'
    MONGO_URL = 'mongodb://127.0.0.1:27017'
    SENTRY_URL = 'https://01d06f51c2ff44de89b446d244225e38@app-devops.ekol.com/2'
    MAIL_SERVER = '10.1.70.1'
    MAIL_PORT = 25
    MAIL_USE_SSL = False
    MAIL_DEFAULT_SENDER = 'accompany-test@ekol.com'
    EXECUTOR_TYPE = 'thread'
    EXECUTOR_MAX_WORKERS = 10


class DEVConfig(Config):
    DEBUG = True


class TESTConfig(Config):
    DEBUG = False
    MY_CALLBACK_URL = 'https://apiaccompanytest.ekol.com/api/v1/auth/on_google_succeed'
    WEB_CLIENT = 'https://accompanytest.ekol.com'
    MONGO_URL = "mongodb://accompany_db_user:eCpvC8WTUhRYPFoP@127.0.0.1:27017/AccompanyDB"
    QUADRO_API_URL = 'http://10.5.20.7/api/accompany/getOrders/'
    ONEORDER_API_URL = 'https://oneorder-test.ekol.com:8443'
    ONEORDER_API_USERNAME = 'accompany'
    ONEORDER_API_PASSWORD = 'accompany'



class PRODConfig(Config):
    MONGO_URL = ''
    SENTRY_URL = ''
    MY_CALLBACK_URL = 'https://apiaccompany.ekol.com/api/v1/auth/on_google_succeed'
    WEB_CLIENT = 'https://accompany.ekol.com'
    # PRODlar belli olunca değişecek.
    QUADRO_API_URL = 'http://10.5.20.7/api/accompany/getOrders/'
    ONEORDER_API_URL = 'https://oneorder-test.ekol.com:8443'
    DEBUG = False


def decide_config(environment):
    try:
        return eval('{}Config'.format(environment))
    except NameError:
        return Config
