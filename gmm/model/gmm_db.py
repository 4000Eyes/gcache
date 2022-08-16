from flask import current_app, g
import pymongo.collection, pymongo.errors
from datetime import datetime, date
from gmm.model.gmm_bl import *
from enum import IntEnum

class MongoDBFunctions():

    def get_current_date(self):
        today = date.today()
        return today.strftime("%d/%m/%Y")

    def insert_buyer_initiated_info(self, gmm_initiated_buyer_info: pymongo.collection, obj_buyer: GMMInitiatedBuyInfo, session=None ):

        try:
            while True:
                try:
                    gmm_initiated_buyer_info.insert_one({
                        "user_id": obj_buyer.user_id,
                        "transaction_id":obj_buyer.transaction_id,
                        "product_id" : obj_buyer.product_id,
                        "friend_circle_id": obj_buyer.friend_circle_id,
                        "occasion_id" : obj_buyer.occasion_id,
                        "occasion_name": obj_buyer.occasion_name,
                        "occasion_date": obj_buyer.occasion_date,
                        "total_members" : obj_buyer.total_members,
                        "initiated_date" : obj_buyer.initiated_date,
                        "total_members": obj_buyer.total_members,
                        "product_price" : obj_buyer.product_price,
                        "misc_cost" : obj_buyer.misc_cost,
                        "first_name" : obj_buyer.first_name,
                        "last_name" : obj_buyer.last_name,
                        "phone_number" : obj_buyer.phone_number,
                        "email_address" : obj_buyer.email_address,
                        "transaction_id": obj_buyer.transaction_id,
                        "paying_members" : obj_buyer.paying_members,
                        "adjusted_per_user_amount" : obj_buyer.adjusted_per_user_amount,
                        "notes" : obj_buyer.notes,
                        "transaction_status" : int(obj_buyer.transaction_status)
                    }, session=session)
                    break
                except (pymongo.errors.ConnectionFailure, pymongo.errors.OperationFailure) as exc:
                    # If transient error, retry the whole transaction
                    if exc.has_error_label("TransientTransactionError"):
                        print("TransientTransactionError transaction ...")
                        continue
                    else:
                        raise Exception
            return True
        except Exception as e:
            current_app.logger.error(str(e))
            print("The error is ", str(e))
            return False


    def get_initiated_buyer_info(self, gmm_initiated_buyer_info: pymongo.collection,
                                 list_buyer,
                                 query_type: GMMBuyerIntiatedInfoReadQueryType,
                                 transaction_id=None,
                                 user_id = None,
                                 product_id = None,
                                 occasion_id = None,
                                 occasion_date = None,
                                 friend_circle_id = None,
                                 session=None):

        try:
            if query_type == GMMBuyerIntiatedInfoReadQueryType.USER_BASED:
                result = gmm_initiated_buyer_info.find({"user_id": user_id}, session=session)
            if query_type == GMMBuyerIntiatedInfoReadQueryType.TXN_USER_OCCASION_PRODUCT_BASED:
                if friend_circle_id is not None and user_id is not None and product_id is not None:
                    result = gmm_initiated_buyer_info.find({"$and": [
                        {"occasion_id": user_id},
                        {"product_id": product_id},
                        {"friend_circle_id": friend_circle_id}
                    ]
                    })
            if query_type == GMMBuyerIntiatedInfoReadQueryType.TRANSACTION_BASED:
                result = gmm_initiated_buyer_info.find({"transaction_id": transaction_id}, session=session)
            if query_type == GMMBuyerIntiatedInfoReadQueryType.PROD_OCCASION_CIRCLE_BASED:
                result = gmm_initiated_buyer_info.find({"$and": [
                    {"occasion_id": occasion_id},
                    {"product_id": product_id},
                    {"friend_circle_id": friend_circle_id},
                    {"occasion_date": occasion_date}
                ]
                })
            for row in result:
                obj_buyer = GMMInitiatedBuyInfo()
                obj_buyer.user_id = row["user_id"]
                obj_buyer.first_name = row["first_name"]
                obj_buyer.last_name = row["last_name"]
                obj_buyer.email_address = row["email_address"]
                obj_buyer.phone_number = row["phone_number"]
                obj_buyer.product_id = row["product_id"]
                obj_buyer.friend_circle_id = row["friend_circle_id"]
                obj_buyer.transaction_id = row["transaction_id"]
                obj_buyer.occasion_id = row["occasion_id"]
                obj_buyer.occasion_name = row["occasion_name"] if "occasion_name" in row else None
                if row["initiated_date"] is not None and isinstance(row["initiated_date"], datetime):
                    obj_buyer.initiated_date = row["initiated_date"].strftime('%Y/%m/%d')
                else:
                    obj_buyer.initiated_date = row["initiated_date"]
                obj_buyer.initiated_date = row["initiated_date"]
                obj_buyer.total_members = row["total_members"]
                obj_buyer.transaction_status = row["transaction_status"]
                obj_buyer.notes = row["notes"]
                obj_buyer.product_price = row["product_price"]
                obj_buyer.misc_cost = row["misc_cost"]
                obj_buyer.paying_members = row["paying_members"]
                obj_buyer.adjusted_per_user_amount = row["adjusted_per_user_amount"]
                list_buyer.append(obj_buyer)
            return True
        except Exception as e:
            print ("The error is ", e)
            return  False

    def update_initiated_buyer_info(self, gmm_initiated_buyer_info, obj_buyer: GMMInitiatedBuyInfo,
                                    query_type: GMMBuyerIntiatedInfoUpdateQueryType, session=None):
        try:
            while True:
                try:
                    if query_type == GMMBuyerIntiatedInfoUpdateQueryType.TRANSACTION_BASED:
                        result = gmm_initiated_buyer_info.update_one({"transaction_id":obj_buyer.transaction_id},
                                                        {"$set":
                                                             {
                                                                "user_id": obj_buyer.user_id ,
                                                                "product_id": obj_buyer.product_id,
                                                                "friend_circle_id":obj_buyer.friend_circle_id,
                                                                "occasion_id":obj_buyer.occasion_id,
                                                                "occasion_name":obj_buyer.occasion_name,
                                                                "initiated_date": obj_buyer.initiated_date,
                                                                "total_members":obj_buyer.total_members,
                                                                "transaction_status":obj_buyer.transaction_status,
                                                                "notes":obj_buyer.notes ,
                                                                "product_price": obj_buyer.product_price,
                                                                "misc_cost": obj_buyer.misc_cost,
                                                                 "adjusted_per_user_amount": obj_buyer.adjusted_per_user_amount
                                                             }
                                                         },upsert=False,session=session)
                    if query_type == GMMBuyerIntiatedInfoUpdateQueryType.UPDATE_STATUS:
                        result = gmm_initiated_buyer_info.update_one({"transaction_id":obj_buyer.transaction_id},
                                                        {"$set":
                                                             {
                                                                "transaction_status": obj_buyer.transaction_status
                                                             }}, upsert=False, session=session)

                    if query_type == GMMBuyerIntiatedInfoUpdateQueryType.PAYING_MEMBERS:
                        result = gmm_initiated_buyer_info.update_one({"transaction_id":obj_buyer.transaction_id},
                                                        {"$set":
                                                             {
                                                                "paying_members": obj_buyer.paying_members,
                                                                 "adjusted_per_user_amount" : obj_buyer.adjusted_per_user_amount

                                                             }}, upsert=False, session=session)


                    break

                except (pymongo.errors.ConnectionFailure, pymongo.errors.OperationFailure) as exc:
                    # If transient error, retry the whole transaction
                    if exc.has_error_label("TransientTransactionError"):
                        print("TransientTransactionError transaction ...")
                        continue
                    else:
                        raise Exception
            return True
        except Exception as e:
            current_app.logger.error(e)
            print("The error is ", e)
            return False

    def insert_buyer_friend_circle(self, gmm_buyer_friend_circle: pymongo.collection, obj_buyer_friend_circle: GMMFriendCircleInfo, session=None ):
        try:
            while True:
                try:
                    gmm_buyer_friend_circle.insert_one({
                        "user_id": obj_buyer_friend_circle.user_id,
                        "transaction_id":obj_buyer_friend_circle.transaction_id,
                        "first_name" : obj_buyer_friend_circle.first_name,
                        "last_name" : obj_buyer_friend_circle.last_name,
                        "email_address" : obj_buyer_friend_circle.email_address,
                        "phone_number" : obj_buyer_friend_circle.phone_number,
                        "per_user_share" : obj_buyer_friend_circle.per_user_share,
                        "opt_in_flag": obj_buyer_friend_circle.opt_in_flag,
                        "opt_in_date" : obj_buyer_friend_circle.opt_in_date,
                        "paid_amount": obj_buyer_friend_circle.paid_amount,
                        "last_paid_date": obj_buyer_friend_circle.last_paid_date,
                        "transaction_status": obj_buyer_friend_circle.transaction_status,
                        "recommended_share": obj_buyer_friend_circle.recommended_share,
                        "user_type" : obj_buyer_friend_circle.user_type
                    }, session=session)
                    break
                except (pymongo.errors.ConnectionFailure, pymongo.errors.OperationFailure) as exc:
                    # If transient error, retry the whole transaction
                    if exc.has_error_label("TransientTransactionError"):
                        print("TransientTransactionError transaction ...")
                        continue
                    else:
                        raise Exception
            return True

        except Exception as e:
            current_app.logger.error(e)
            print("The error is ", e)
            return False


    def get_buyer_friend_circle(self, gmm_buyer_friend_circle: pymongo.collection,
                                list_friend_circle,
                                query_type: GMMBuyerFriendCircleReadQueryType, transaction_id=None, user_id=None,  session=None):
        try:
            if query_type == GMMBuyerFriendCircleReadQueryType.TRANSACTION_BASE is not None:
                r_cursor = gmm_buyer_friend_circle.find({"transaction_id": transaction_id}, session=session)
            if query_type == GMMBuyerFriendCircleReadQueryType.TXN_USER_BASED:
                if transaction_id is not None and user_id is not None :
                    r_cursor = gmm_buyer_friend_circle.find({"$and": [
                        {"transaction_id": transaction_id},
                        {"user_id": user_id}
                    ]
                    })
                else:
                    current_app.logger.error("Required arguments are not sent user id + transaction id")
                    return False
            if query_type == GMMBuyerFriendCircleReadQueryType.USER_BASED:
                if user_id is not None:
                    r_cursor = gmm_buyer_friend_circle.find({"$and": [
                        {"transaction_status": {"$in": [TeamBuyStatus.IN_DISCUSSION, TeamBuyStatus.ACTIVATED]}},
                        {"user_id": user_id}
                    ]
                    })

            for result in r_cursor:
                obj_friend_circle = GMMFriendCircleInfo()
                obj_friend_circle.user_id = result["user_id"]
                obj_friend_circle.transaction_id = result["transaction_id"]
                obj_friend_circle.email_address = result["email_address"]
                obj_friend_circle.phone_number = result["phone_number"]
                obj_friend_circle.first_name = result["first_name"]
                obj_friend_circle.last_name = result["last_name"]
                obj_friend_circle.per_user_share = result["per_user_share"]
                obj_friend_circle.opt_in_flag = result["opt_in_flag"]
                if result["opt_in_date"] is not None and isinstance(result["opt_in_date"], datetime):
                    obj_friend_circle.opt_in_date = result["opt_in_date"].strftime('%Y/%m/%d')
                else:
                    obj_friend_circle.opt_in_date = result["opt_in_date"]
                if result["last_paid_date"] is not None and isinstance(result["last_paid_date"], datetime):
                    obj_friend_circle.opt_in_date = result["last_paid_date"].strftime('%Y/%m/%d')
                else:
                    obj_friend_circle.opt_in_date = result["last_paid_date"]

                obj_friend_circle.paid_amount = result["paid_amount"]
                obj_friend_circle.transaction_status = result["transaction_status"]
                obj_friend_circle.recommended_share = result["recommended_share"]
                obj_friend_circle.user_type = result["user_type"]
                list_friend_circle.append(obj_friend_circle)
            return True
        except Exception as exc:
            current_app.logger.error("The exception is" + str(exc))
            return False

    def update_buyer_friend_circle(self, gmm_buyer_friend_circle: pymongo.collection,
                                   obj_buyer_friend_circle: GMMFriendCircleInfo,
                                   query_type:GMMBuyerFriendCircleUpdateQueryType,
                                   session=None):
        try:
            while True:
                try:
                    if query_type == GMMBuyerFriendCircleUpdateQueryType.TXN_USER_BASED:
                        result = gmm_buyer_friend_circle.update_one(
                                        {"$and": [
                                            {"transaction_id": obj_buyer_friend_circle.transaction_id},
                                            {"user_id": obj_buyer_friend_circle.user_id}
                                        ]
                                        },
                                    {"$set":
                                         {
                                             "first_name": obj_buyer_friend_circle.first_name,
                                             "last_name": obj_buyer_friend_circle.last_name,
                                             "email_address": obj_buyer_friend_circle.email_address,
                                             "phone_number": obj_buyer_friend_circle.phone_number,
                                             "per_user_share": obj_buyer_friend_circle.per_user_share,
                                             "opt_in_flag": obj_buyer_friend_circle.opt_in_flag,
                                             "opt_in_date": obj_buyer_friend_circle.opt_in_date,
                                             "paid_amount": obj_buyer_friend_circle.paid_amount,
                                             "last_paid_date": obj_buyer_friend_circle.last_paid_date,
                                             "transaction_status": obj_buyer_friend_circle.transaction_status,
                                             "recommended_share" : obj_buyer_friend_circle.recommended_share,
                                             "user_type":obj_buyer_friend_circle.user_type
                                         }
                                     }, upsert=False, session=session)
                    break
                except (pymongo.errors.ConnectionFailure, pymongo.errors.OperationFailure) as exc:
                    # If transient error, retry the whole transaction
                    if exc.has_error_label("TransientTransactionError"):
                        print("TransientTransactionError transaction ...")
                        continue
                    else:
                        raise Exception

            return True
        except Exception as e:
            current_app.logger.error(e)
            print("The error is ", e)
            return False


    def insert_message(self, gmm_message, friend_circle_id, user_id, transaction_id,
                       message_type, message, message_datetime, active_status, commodity_id=None, session=None):
        try:
            json_payload = {"commodity_id":commodity_id,"description":message}
            while True:
                try:
                    gmm_message.insert_one({
                        "transaction_id": transaction_id,
                        "message_id": str(uuid.uuid4()),
                        "user_id": user_id,
                        "friend_circle_id": friend_circle_id,
                        "type_id" : message_type,
                        "created_dt": message_datetime,
                        "pay_load": json_payload,
                        "is_active": 1,
                        "is_seen": "N"
                    }, session=session)
                    break
                except (pymongo.errors.ConnectionFailure, pymongo.errors.OperationFailure) as exc:
                    # If transient error, retry the whole transaction
                    if exc.has_error_label("TransientTransactionError"):
                        print("TransientTransactionError transaction ...")
                        continue
                    else:
                        raise Exception
                    return True
            return True
        except Exception as e:
            current_app.logger.error(e)
            print("The error is ", e)
            return False

    def update_message(self, gmm_message,  user_id, transaction_id, message_type, active_status, session=None):
        try:
            while True:
                try:
                    gmm_message.update_many(
                                        {"$and": [
                                            {"transaction_id": transaction_id},
                                            {"user_id": user_id},
                                            {"type_id":message_type}
                                        ]
                                        },
                        {"$set":
                            {
                                "is_active": active_status,
                            }
                        }, upsert=False, session=session
                    )
                    break
                except (pymongo.errors.ConnectionFailure, pymongo.errors.OperationFailure) as exc:
                    # If transient error, retry the whole transaction
                    if exc.has_error_label("TransientTransactionError"):
                        print("TransientTransactionError transaction ...")
                        continue
                    else:
                        raise Exception
                    return True
            return True
        except Exception as e:
            current_app.logger.error(e)
            print("The error is ", e)
            return False


    def publish_message(self, gmm_message, obj_message, user_id,  session=None):
        try:
            while True:
                try:
                    r_cursor = gmm_message.find({"$and": [
                        {"is_active": 1},
                        {"user_id": user_id}
                    ]
                    },
                                                session=session)

                    for record in r_cursor:
                        obj_message = GMMMessage()
                        obj_message.message = record["message"]
                        obj_message.message_type = record["message_type"]
                        obj_message.user_id = record['user_id']
                        obj_message.friend_circle_id = record["friend_circle_id"]
                        obj_message.transaction_id = record["transaction_id"]
                        obj_message.message_datetime = record["message_datetime"]
                        obj_message.all.append(obj_message)
                    break
                except (pymongo.errors.ConnectionFailure, pymongo.errors.OperationFailure) as exc:
                    # If transient error, retry the whole transaction
                    if exc.has_error_label("TransientTransactionError"):
                        print("TransientTransactionError transaction ...")
                        continue
                    else:
                        raise Exception
                    return True
            return True
        except Exception as e:
            current_app.logger.error(e)
            print("The error is ", e)
            return False

