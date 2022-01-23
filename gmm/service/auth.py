from flask import Response, request, current_app, g
from flask_jwt_extended import create_access_token, decode_token
from app.model.models import UserHelperFunctions
from app.model.gdbmethods import GDBUser
from flask_restful import Resource
import datetime
import json


class SignupApi(Resource):
    def post(self):
        try:
            print ("Entering /api/auth/signup")
            body = request.get_json()
            if body is None:
                current_app.logger.error("No parameters send into the sign up api (post). Check")
                return {"status": "failure"}, 500
            data = {}
            print(body)
            user_hash = {}
            user_hash["email_address"] = body["email"]
            user_hash["password"] = body["password"]
            user_hash["user_type"] = body["user_type"]
            user_hash["user_status"] = 0 # Meaning inactive
            user_hash["phone_number"] = body["phone_number"]
            user_hash["gender"] = body["gender"]
            user_hash["first_name"] = body["first_name"]
            user_hash["last_name"] = body["last_name"]
            user_hash["mongo_indexed"] = "N"

            if user_hash.get("email_address") is None or user_hash.get("user_type") is None or user_hash.get("password") is None or user_hash.get("phone_number") is None or user_hash.get("gender") is None or user_hash.get("first_name") is None or user_hash.get("last_name") is None:
                current_app.logger.error("Missing one or many inputs including email, phone, password, gender, first_name, last_name, user_type")
                return {"status": "Missing one or many inputs including email, phone, password, gender, first_name, last_name, user_type"}, 400

            objGDBUser = GDBUser()
            print("Before calling get user")
            if objGDBUser.get_user(user_hash.get("email_address"), data):
                if len(data) > 0:
                    current_app.logger.info("User id exists for " + user_hash.get("email_address") + "user id is" + data.get("user_id") )
                    return {'status': ' User already exists'}, 400
            else:
                current_app.logger.error("User with this email address already exists" + user_hash.get("email_address"))
                return {'status': ' User already exists for ' + user_hash.get("email_address")}, 400

            data = {}

            objHelper = UserHelperFunctions()

            pwd = objHelper.hash_password(user_hash.get("password"))
            print ("The password is ", pwd, user_hash.get("password"))
            user_hash["password"] = pwd
            if not objGDBUser.insert_user(user_hash, data):
                current_app.logger.error("There is an issue in inserting the user")
                return {'status': ' User already exists'}, 400
            """
            objEmail = EmailManagement()
            registration_token = objHelper.generate_confirmation_token(user_hash["email_address"])

            if registration_token is not None:
                confirmation_url = 'https://www.gemift.com/token=' + registration_token
                if objEmail.send_signup_email(user_hash["email_address"], user_hash["first_name"], user_hash["last_name"], confirmation_url):
                    current_app.logger.error("Error completing registration. Unable to send email to the user")
                    return {"Status" : "Failure in completing registration. Unable to send the email or the email is invalid"}, 401
            """
            return {'data': json.dumps(data)}, 200
                # Check if there is an approved invitation request for this user. If so, automatically add them to the circle
                # and take them to the circle home page.
        except Exception as e:
                # Check and delete from graph and mongodb as implementing transaction at this point looks major refactoring.
                print ("The erros is", e)
                current_app.logger.error(e)
                return {'status': 'Failure in inserting the user'}, 500

class RegistrationConfirmation(Resource):
    def post(self):
        content = request.get_json()
        token = content["token"]
        if token is None:
            return {"Status" : "Unable to validate the user"}, 400
        objHelper = UserHelperFunctions()
        objGDBUser = GDBUser()
        loutput = []
        email_address = objHelper.confirm_token(token)
        if email_address is not None:
            if not objGDBUser.get_user_by_email(email_address,loutput):
                if not objGDBUser.activate_user(loutput[0]):
                    current_app.logger.error("Unable to activate the user " +  email_address)
                    return {"status" : "Failure. Unable to activate the user"}, 400
                return {"status": "Successfully activated"}, 200
            else:
                return {"status": "Failure. Unable to find the user information"}, 400
        else:
            return {"status" : "Failure. Invalid email address"}, 400


class LoginApi(Resource):
    def post(self):
        try:
            print ("I am inside the login api function")
            body = request.get_json()
            if body is None:
                current_app.logger.error("No parameters send into the login api (post). Check")
                return {"status":"failure"}, 500
            objGDBUser = GDBUser()
            objUser = UserHelperFunctions()
            ack_hash = {}
            ack_hash["user_id"] = None
            ack_hash["authorized"] = False
            if not objUser.validate_login(body["email"], body["password"], ack_hash):
                return {'error': 'System issue. Unable to verify the credentials'}, 401
            if not ack_hash["authorized"]:
                return {"error": "password didnt match"}, 401
            print ("The password from the db is ", ack_hash["authorized"])
            if ack_hash["user_id"] is None:
                return {"Error": "User id is empty. Some technical issues"}, 401
            expires = datetime.timedelta(days=7)
            access_token = create_access_token(identity=str(ack_hash["user_id"]), expires_delta=expires)
            loutput = []
            if not objGDBUser.get_friend_circles(ack_hash["user_id"], loutput):
                current_app.logger.error("Unable to get friend circles for user" + ack_hash["user_id"])
                return {"status": "failure"}, 401
            loutput.append({"user_id" : ack_hash["user_id"]})
            return {'token': access_token, 'data' : json.dumps(loutput)}, 200
        except Exception as e:
            print ("The error is ", e)
            return {'token': 'n/a'}, 400

class ForgotPassword(Resource):
    def post(self):
        url = request.host_url + 'reset/'
        try:
            body = request.get_json()
            if body is None:
                current_app.logger.error("No parameters send into the forgot password api (post). Check")
                return {"status":"failure"}, 500
            email = body.get('email')
            if not email:
                return None
            objUser = UserHelperFunctions()
            output_hash = {}
            if objUser.get_user_info(body["email"], output_hash):
                if "user_id" in output_hash:
                    expires = datetime.timedelta(hours=24)
                    reset_token = create_access_token(str(output_hash["user_id"]), expires_delta=expires)
                    return reset_token
            return {'Error': 'Unable to find the user with the email address'}, 400
        except Exception as e:
            current_app.logger.error("Error executing this function " + e)
            return {'Error': 'Unable to execute the forgot password function'}, 400


class ResetPassword(Resource):
    def post(self):
        url = request.host_url + 'reset/'
        try:
            objUser = UserHelperFunctions()
            body = request.get_json()
            if body is None:
                current_app.logger.error("No parameters send into the reset api (post). Check")
                return {"status":"failure"}, 500
            reset_token = body.get('reset_token')
            password = body.get('password')
            if not reset_token or not password:
                current_app.logger.error("The expected values password and oor reset token is missing")
                return {'Error' : 'The expected values password or reset token are missing'}
            user_id = decode_token(reset_token)['identity']
            if objUser.modify_user_credentials(user_id, password):
                return {"status" : "successfully reset"},  200
            return {"status": "Unsuccessful in resetting the password"}, 400
        except Exception as e:
            current_app.logger.error("Error executing this function " + e)
            return {'Error': 'Unable to execute the reset password function'},400
