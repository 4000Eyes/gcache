#from app.app import g
#import pymongo.collection
from flask import current_app, g
import pymongo.collection, pymongo.errors
from flask_bcrypt import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
class UserHelperFunctions():
    def hash_password(self, pwd):
        return generate_password_hash(pwd).decode('utf8')

    def check_password(self, pwd, upwd):
        return check_password_hash(pwd, upwd)

    def validate_login(self, email,pwd, ack_hash):
        try:
            mongo_user = pymongo.collection.Collection(g.db, "user")
            result = mongo_user.find({"email": email})
            if result is not None:
                for row in result:
                    ack_hash["authorized"] = self.check_password(row["password"], pwd)
                    ack_hash["user_id"] = row["user_id"]
            return True
        except pymongo.errors as e:
            current_app.logger.error(e)
            print("The error is ", e)
            return False
        except Exception as e:
            current_app.logger.error(e)
            print("The error is ", e)
            return False

    def get_user_info(self, email, output_hash):
        try:
            mongo_user = pymongo.collection.Collection(g.db, "User")
            result = mongo_user.find({"email_address": email})
            if result is not None:
                output_hash["user_id"] = result["user_id"]
                return True
            return False
        except pymongo.errors as e:
            current_app.logger.error(e)
            print("The error is ", e)
            return False
        except Exception as e:
            current_app.logger.error(e)
            print("The error is ", e)
            return False

    def modify_user_credentials(self, user_id, password):
        try:
            mongo_user = pymongo.collection.Collection(g.db, "user")
            result = mongo_user.find({"user_id": user_id})
            if result is not None:
                hsh_pwd = self.hash_password(password)
                xres = mongo_user.update_one({"user_id":user_id}, {"password":hsh_pwd},upsert=False)
                if xres is not None:
                    return True
            return False

        except pymongo.errors as e:
            current_app.logger.error(e)
            print("The error is ", e)
            return False
        except Exception as e:
            current_app.logger.error(e)
            print("The error is ", e)
            return False

    def generate_confirmation_token(self, email):
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return serializer.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])

    def confirm_token(self, token, expiration=3600):
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            email = serializer.loads(token,
                                     salt = current_app.config['SECURITY_PASSWORD_SALT'],
                                     max_age= expiration)
            return email
        except Exception as e:
            return None
