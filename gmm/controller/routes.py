from flask_restful import Resource

# from app.service.auth import SignupApi, LoginApi, ResetPassword, ForgotPassword, RegistrationConfirmation
from gmm.service.moneymanager import MoneyManager

from gmm.main import api


def initialize_routes(api):
    #   api.add_resource(SignupApi, '/api/auth/signup')
    api.add_resource(MoneyManager, '/api/gmm/txn')

    return 0
