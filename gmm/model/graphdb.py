import neo4j
from neo4j import __version__ as neo4j_version, TRUST_ALL_CERTIFICATES
# print (neo4j_version)

from neo4j import GraphDatabase
import neo4j.exceptions
from flask_restful import Resource
from flask import current_app, Response, request

class NeoDBConnection(Resource):

    def __init__(self):
        self.app = None
        self.__driver = None


    def init_app(self, app, uri, db, user, pwd):
        self.app = app
        self.__uri = uri
        self.__db = db
        self.__user = user
        self.__pwd = pwd
        self.connect()


    def connect(self):
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
            current_app.logger.info("i am testing this pattern. connected to the database successfully")
            print ("I am connected to the graph db with %s %s", self.__uri, self.__user, self.__pwd)
        except Exception as e:
            print("Failed to create the driver", e)

    def get_session(self):
        print ("Inside getting session")
        try:
            if not self.__driver:
                self.connect()
            return self.__driver.session(database=self.__db) if self.__db is not None else self.__driver.session()
        except neo4j.exceptions.Neo4jError as e:
            print ("The driver exception is ", e.message)
            return None

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def query(self, query):
        assert self.__driver is not None, "Driver not initialized"
        session = None
        response = None
        try:
            session = self.__driver.session(database=self.__db) if self.__db is not None else self.__driver.session()
            print("Before running the query" + query)
            response = list(session.run(query))
            print("The response is ready")
        except Exception as e:
            print("Query Failed" + str(e))
        finally:
            if session is not None:
                session.close()
        return response
