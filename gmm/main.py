import logging
import os
import sys
"""
sys.path.insert(0,'/app')
sys.path.insert(0,'/app/service')
sys.path.insert(0,'/app/model')
"""
from datetime import datetime as dt
from werkzeug.local import LocalProxy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_mongoengine import MongoEngine
from flask_pymongo import PyMongo
from flask import Flask, request, g
from gmm.config import config_by_name
from gmm.model.extensions import NeoDB
from gmm.service.extensions import logs

flask_bcrypt = Bcrypt()
jwt = JWTManager()
api = Api()
dbx = MongoEngine()
cloud_mongodb = PyMongo()

def create_app(config_name: str):
    """Main app factory, runs all the other sections"""
    app = Flask(__name__.split(".")[0])
    app.config.from_object(config_by_name[config_name])
    print ("The env is", config_by_name[config_name])
    print ("The environment that google says", os.environ.get("BOILERPLATE_ENV"))

    dbconnectionstring = app.config['FTEYES_HOST'] + ":" + str(app.config['FTEYES_PORT']) + "/" + app.config['FTEYES_DB']
    app.config['MONGODB_SETTINGS'] = {
        'host': dbconnectionstring,
        'username': app.config['FTEYES_USERNAME'],
        'password': app.config['FTEYES_PASSWORD']
    }
    app.config['MONGO_URI'] = "mongodb+srv://krisraman:1RyrVRJQCBMIdG77@gemiftcluster.qwn4p.mongodb.net/"
    app.config['SECURITY_PASSWORD_SALT'] = 'Dx^&32hjeh'
    print ("Connected to mongo db ")
    jwt.init_app(app)
    flask_bcrypt.init_app(app)
    dbx.init_app(app)

    #loud_mongodb.db.test_collection.insert_one({"From Flask": "Working through Flask23"})

    with app.app_context():
        from gmm.controller.routes import initialize_routes
        #from service.auth import LoginApi, SignupApi
        #api.add_resource(SignupApi, '/api/auth/signup')
        #api.add_resource(LoginApi, '/api/login')
        initialize_routes(api)
        api.init_app(app)
        register_extensions(app)
        cloud_mongodb.init_app(app)
    print ("After initializing the context")
    @app.before_request
    def before_request():
        print ("Before request I see this")
        g.db = cloud_mongodb.cx
        print ("After assigning the db hangle to g variable", g.db)

    @app.after_request
    def after_request(response):
        """ Logging after every request. """
        logger = logging.getLogger("app.access")
        logger.info(
            "%s [%s] %s %s %s %s %s %s %s",
            request.remote_addr,
            dt.utcnow().strftime("%d/%b/%Y:%H:%M:%S.%f")[:-3],
            request.method,
            request.path,
            request.scheme,
            response.status,
            response.content_length,
            request.referrer,
            request.user_agent,
        )
        return response
    @app.route('/test', methods=['GET'])
    def home():
        try:
            # print ("Before ")
            # mdb = g.db.get_database("sample_airbnb")
            # print ("After")
            # with g.db.start_session() as session:
            #     user_collection = mdb.get_collection("user")
            #     result = user_collection.find()
            #     for row in result:
            #         print(row)
            #     session.commit_transaction()

            # with client.start_session() as session:
            #     session.start_transaction()
            #     result = user_collection.find()
            #     for row in result:
            #         print (row)
            #     session.commit_transaction()
            return "<h1>Test</h1><p>Welccome to service. Hope this keeps working. Thank you,. Thank you</p>"
        except Exception as e:
            print (e)
    return app


def register_extensions(app):
    logs.init_app(app)
    NeoDB.init_app(app, app.config['FTEYES_GDB_URI'], app.config['FTEYES_GDB_DB'], app.config['FTEYES_GDB_USER'],
                   app.config['FTEYES_GDB_PWD'])
    #RedisCache.init_app(app, app.config['REDIS_HOST'], app.config['REDIS_PORT'], app.config['REDIS_PASSWORD'], app.config['REDIS_DBNAME'])
    #from service.cachebuilder import load_category_cache, load_subcat_brand_cache
    #load_category_cache()
    #load_subcat_brand_cache()
    return None


def run():
    app= create_app(os.environ.get('BOILERPLATE_ENV') or 'dev')
    print("The environment variable is",  os.environ.get('BOILERPLATE_ENV'))
    #app.run(use_reloader=False,host="0.0.0.0",port=8081, debug=True)
    app.run( use_reloader=False, host="localhost", port=5000, debug=True)

if __name__ == '__main__':
    run()


