from flask import current_app, g
import pymongo.collection, pymongo.errors
from datetime import datetime, date
from gmm.model.gmm_bl import *

class MongoDBFunctions():

    def get_current_date(self):
        today = date.today()
        return today.strftime("%d/%m/%Y")

    def insert_buyer_initiated_info(self, gmm_initiated_buyer_info: pymongo.collection, obj_buyer: GMMInitiatedBuyInfo, session=None ):

        try:
            gmm_initiated_buyer_info.insert_one({
                "user_id": obj_buyer.user_id,
                "product_id" : obj_buyer.product_id,
                "friend_circle_id": obj_buyer.friend_circle_id,
                "occasion_id" : obj_buyer.occasion_id,
                "total_members" : obj_buyer.total_members,
                "initiated_date" : obj_buyer.initiated_date,
                "status" : obj_buyer.status
            }, session=session)

            return True
        except pymongo.errors as e:
            current_app.logger.error(e)
            print("The error is ", e)
            return False
        except Exception as e:
            current_app.logger.error(e)
            print("The error is ", e)
            return False


    def get_initiated_buyer_info(self, gmm_initiated_buyer_info: pymongo.collection,
                                 obj_buyer,
                                 query_type: GMMBuyerIntiatedInfoReadQueryType,
                                 transaction_id=None,
                                 user_id = None,
                                 product_id = None,
                                 occasion_id = None,
                                 friend_circle_id = None,
                                 session=None):
        try:
            if obj_buyer.query_type == GMMBuyerIntiatedInfoReadQueryType.USER_BASED:
                result = gmm_initiated_buyer_info.find({"user_id": obj_buyer.user_id}, session=session)
            if obj_buyer.query_type == GMMBuyerIntiatedInfoReadQueryType.TXN_USER_OCCASION_PRODUCT_BASED:
                if obj_buyer.friend_circle_id is not None and obj_buyer.user_id is not None and obj_buyer.product_id is not None:
                    result = gmm_initiated_buyer_info.find({"$and": [
                        {"occasion_id": obj_buyer.user_id},
                        {"product_id": obj_buyer.product_id},
                        {"friend_circle_id": obj_buyer.friend_circle_id}
                    ]
                    })
            if result is not None:

                obj_buyer.user_id = result["user_id"]
                obj_buyer.product_id = result["product_id"]
                obj_buyer.friend_circle_id = result["friend_circle_id"]
                obj_buyer.buyer_txn_id = result["buyer_txn_if"]
                obj_buyer.occasion_id = result["occasion_id"]
                obj_buyer.initiated_date = result["initiated_date"]
                obj_buyer.total_members = result["total_members"]
                obj_buyer.status = result["status"]

            return True
        except pymongo.errors as exc:
            return False

    def update_initiated_buyer_info(self, gmm_initiated_buyer_info, obj_buyer: GMMInitiatedBuyInfo, session=None):
        try:
            result = gmm_initiated_buyer_info.update({"user_id":obj_buyer.user_id},
                                            {"$set":
                                                 [{
                                                     "product_id": obj_buyer.product_id,
                                                     "friend_circle_id": obj_buyer.friend_circle_id,
                                                     "initiated_date": obj_buyer.initiated_date,
                                                     "status": obj_buyer.status
                                                 }]
                                             }, session=session)

            return True
        except pymongo.errors as e:
            current_app.logger.error(e)
            print("The error is ", e)
            return False
        except Exception as e:
            current_app.logger.error(e)
            print("The error is ", e)
            return False

    def insert_buyer_friend_circle(self, gmm_buyer_friend_circle: pymongo.collection, obj_buyer_friend_circle: GMMFriendCircleInfo, session=None ):

        try:
            gmm_buyer_friend_circle.insert_one({
                "user_id": obj_buyer_friend_circle.user_id,
                "buyer_txn_id":obj_buyer_friend_circle.buyer_txn_id,
                "voted_date" : obj_buyer_friend_circle.voted_date,
                "voted_value": obj_buyer_friend_circle.voted_value
            }, session=session)

            return True
        except pymongo.errors as e:
            current_app.logger.error(e)
            print("The error is ", e)
            return False
        except Exception as e:
            current_app.logger.error(e)
            print("The error is ", e)
            return False


    def get_buyer_friend_circle(self, gmm_buyer_friend_circle: pymongo.collection, obj_friend_circle, transaction_id, user_id,  session=None):
        try:
            if obj_buyer_friend_circle.buyer_txn_id is not None:
                result = gmm_buyer_friend_circle.find({"buyer_txn_id": transaction_id}, session=session)
            else:
                if transaction_id is not None and user_id is not None :
                    result = gmm_buyer_friend_circle.find({"$and": [
                        {"buyer_txn_id": transaction_id},
                        {"user_id": user_id}
                    ]
                    })
            if result is not None:
                obj_friend_circle = GMMFriendCircleInfo()
                obj_friend_circle.user_id = result["user_id"]
                obj_friend_circle.buyer_txn_id = result["buyer_txn_id"]
                obj_friend_circle.email_address = result["email_address"]
                obj_friend_circle.phone_number = result["phone_number"]
                obj_friend_circle.first_name = result["first_name"]
                obj_friend_circle.last_name = result["last_name"]
                obj_friend_circle.voted_date = result["voted_date"]
                obj_friend_circle.voted_value = result["voted_value"]
            return True
        except pymongo.errors as exc:
            return False

    def update_buyer_friend_circle(self, gmm_buyer_friend_circle: pymongo.collection, obj_buyer_friend_circle: GMMFriendCircleInfo, session=None):
        try:
            result = gmm_buyer_friend_circle.update({"buyer_txn_id":obj_buyer_friend_circle.buyer_txn_id},
                                            {"$set":
                                                 [{
                                                     "voted_date": obj_buyer_friend_circle.voted_date,
                                                     "voted_value": obj_buyer_friend_circle.voted_value,
                                                     "user_id": obj_buyer_friend_circle.user_id
                                                 }]
                                             }, session=session)

            return True
        except pymongo.errors as e:
            current_app.logger.error(e)
            print("The error is ", e)
            return False
        except Exception as e:
            current_app.logger.error(e)
            print("The error is ", e)
            return False


    def get_transaction(self, gmm_collection: pymongo.collection, txn_id, obj: GMMTransaction, session=None):
        try:
            if obj.transaction_id is not None:
                result = gmm_collection.find({"transaction_id": txn_id}, session=session)
            else:
                if obj.friend_circle_id is not None and obj.occasion_id is not None and obj.occasion_date is not None:
                    result = gmm_collection.find({"$and":[
                                            {"occasion_id": obj.occasion_id},
                                            {"occasion_date":obj.occasion_date},
                                            {"friend_circle_id": obj.friend_circle_id}
                                                ]
                                                  })
            if result is not None:
                obj.transaction_id = result["transaction_id"]
                obj.cost = result["cost"]
                obj.per_user_amount = result["per_user_amount"]
                obj.buy_type = result["buy_type"]
                obj.designated_buyer_id = result["designated_buyer_id"]
                obj.product_id = result["product_id"]
                obj.split_percent = result["split_percent"]
                obj.total_members = result["total_members"]
                obj.created_dt = result["created_dt"]
                obj.updated_dt = result["updated_dt"]
                obj.friend_circle_id = result["friend_circle_id"]

            return True
        except pymongo.errors as exc:
            return False

    def insert_transaction(self, gmm_collection, obj_txn: GMMTransaction, session=None):
        try:
            gmm_collection.insert_one({
                "transaction_id": obj_txn.transaction_id,
                "product_id": obj_txn.product_id,
                "cost": obj_txn.cost,
                "designated_buyer_id": obj_txn.designated_buyer_id,
                "designated_received_id": obj_txn.designated_receiver_id,
                "split_percent": obj_txn.split_percent,
                "reference": obj_txn.friend_circle_id,
                "inserted_date": self.get_current_date(),
                "updated_date": "None"
            }, session=session)

            return True
        except pymongo.errors as e:
            current_app.logger.error(e)
            print("The error is ", e)
            return False
        except Exception as e:
            current_app.logger.error(e)
            print("The error is ", e)
            return False

    def update_transaction(self, gmm_collection, obj_txn: GMMTransaction, session=None):
        try:
            result = gmm_collection.update({"transaction_id":obj_txn.transaction_id},
                                            {"$set":
                                                 [{
                                                     "product_id": obj_txn.product_id,
                                                     "cost": obj_txn.cost,
                                                     "designated_buyer_id": obj_txn.designated_buyer_id,
                                                     "designated_received_id": obj_txn.designated_receiver_id,
                                                     "split_percent": obj_txn.split_percent,
                                                     "reference": obj_txn.friend_circle_id,
                                                     "updated_date": self.get_current_date()
                                                 }]
                                             }, session=session)


            return True
        except pymongo.errors as e:
            current_app.logger.error(e)
            print("The error is ", e)
            return False
        except Exception as e:
            current_app.logger.error(e)
            print("The error is ", e)
            return False



    def insert_transaction_detail(self, gmm_detail_collection: pymongo.collection, obj: GMMTransactionDetail,
                                  session=None):
        try:
            gmm_detail_collection.insert_one({
                "transaction_id": obj.transaction_id,
                "user_id": obj.user_id,
                "user_amount": obj.user_amount,
                "first_name":obj.first_name,
                "last_name":obj.last_name,
                "email_address": obj.email_address,
                "phone_number": obj.phone_number,
                "city":obj.city,
                "state":obj.state,
                "zip_code":obj.zip_code,
                "country":obj.country,
                "status":obj.status,
                "user_amount":obj.user_amount
            }, session=session)

            return True
        except pymongo.errors as e:
            current_app.logger.error(e)
            print("The error is ", e)
            return False
        except Exception as e:
            current_app.logger.error(e)
            print("The error is ", e)
            return False

    def get_transaction_detail(self, gmm_detail_collection: pymongo.collection, obj,
                               txn_id, user_id=None, session=None):
        try:
            if user_id is not None and txn_id is not None:
                result = gmm_detail_collection.find({"$and": [
                    {"transaction_id": txn_id},
                    {"user_id": user_id}
                       ]
                      })
            elif txn_id is not None:
                result = gmm_detail_collection.find({"transaction_id":txn_id})
            else:
                result = gmm_detail_collection.find({"user_id": user_id})

            if result is not None:
                for row in result:
                    obj = GMMTransactionDetail()
                    obj.transaction_id = result["transaction_id"]
                    obj.user_id = result["user_id"]
                    obj.first_name = result["first_name"]
                    obj.last_name = result["last_name"]
                    obj.email_address = result["email_address"]
                    obj.phone_number = result["phone_number"]
                    obj.city = result["city"]
                    obj.state = result["state"]
                    obj.zip_code = result["zip_code"]
                    obj.country = result["country"]
                    obj.status = result["status"]
                    obj.user_amount = result["user_amount"]
                    obj.all.append(obj)
            return True
        except pymongo.errors as exc:
            return False


    def update_transaction_detail(self, gmm_detail_collection: GMMTransactionDetail, obj: GMMTransactionDetail, session=None):
        try:
            result = gmm_detail_collection.update({"and":[{"transaction_id":obj.transaction_id}, {"user_id":obj.user_id}]},
                                                  {"set": {
                                            "transaction_id": obj.transaction_id,
                                            "user_id": obj.user_id,
                                            "user_amount": obj.user_amount,
                                            "first_name": obj.first_name,
                                            "last_name": obj.last_name,
                                            "email_address": obj.email_address,
                                            "phone_number": obj.phone_number,
                                            "city": obj.city,
                                            "state": obj.state,
                                            "zip_code": obj.zip_code,
                                            "country": obj.country,
                                            "status": obj.status,
                                            "user_amount": obj.user_amount,
                                            "user_paid": obj.user_paid,
                                            "updated_dt": self.get_current_date()
                                                  }}, session=session
                                                )
            return True
        except pymongo.errors as e:
            current_app.logger.error(e)
            print("The error is ", e)
            return False
        except Exception as e:
            current_app.logger.error(e)
            print("The error is ", e)
            return False

