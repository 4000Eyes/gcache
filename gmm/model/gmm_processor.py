import uuid
from flask import current_app, g
from gmm.model.gmm_db import MongoDBFunctions
from gmm.model.gmm_bl import *
import pymongo
import uuid


def commit_with_retry(session):
    while True:
        try:
            # Commit uses write concern set at transaction start.
            session.commit_transaction()
            print("Transaction committed.")
            break
        except (pymongo.errors.ConnectionFailure, pymongo.errors.OperationFailure) as exc:
            # Can retry commit
            if exc.has_error_label("UnknownTransactionCommitResult"):
                print("UnknownTransactionCommitResult, retrying "
                      "commit operation ...")
                continue
            else:
                print("Error during commit ...")
                raise


def process_transaction():
    try:
        detail_data = [
            {"user_id": "xyz1", "first_name": "Kris", "last_name": "Raman", "email_address": "Krisraman@gmail.com",
             "phone_number": "14252815459", "address1": "101, SE st", "address2": "None", "city": "Sammamish",
             "zip_code": "98074", "country": "USA"},
            {"user_id": "xyz2", "first_name": "Kris", "last_name": "Raman",
             "email_address": "Krisraman1@gmail.com", "phone_number": "14252815461",
             "address1": "101, SE st", "address2": "None", "city": "Sammamish",
             "zip_code": "98074", "country": "USA"},
            {"user_id": "xyz3", "first_name": "Kris", "last_name": "Raman",
             "email_address": "Krisraman2@gmail.com", "phone_number": "14252815460",
             "address1": "101, SE st", "address2": "None", "city": "Sammamish",
             "zip_code": "98074", "country": "USA"}
        ]
        db = g.db.get_database("sample_airbnb")
        gmm_collection = pymongo.collection.Collection(db, "gmm_transaction")
        gmm_detail_collection = pymongo.collection.Collection(db, 'gmm_transaction_detail')
        with g.db.start_session() as session:

            while True:
                try:
                    with session.start_transaction():

                        obj_txn = GMMTransaction(product_id="1234",
                                                 cost=124.43,
                                                 split_percent=.23,
                                                 designated_buyer_id="XYZ",
                                                 designated_receiver_id="ABD",
                                                 buy_type=1,
                                                 transaction_id=str(uuid.uuid4())
                                                 )

                        obj_txn.total_members = len(detail_data)
                        obj_txn.calculate_user_amount()
                        objDB = MongoDBFunctions()
                        if not objDB.insert_transaction(gmm_collection, obj_txn, session):
                            current_app.logger.error("Unable to insert row in gmm transaction")
                            return False
                        for item in detail_data:
                            obj_txn_detail = GMMTransactionDetail(**item,
                                                                  transaction_id=obj_txn.transaction_id,
                                                                  user_amount=GMMTransaction.per_user_amount)
                            if not objDB.insert_transaction_detail(gmm_detail_collection, obj_txn_detail, session):
                                current_app.logger.error('Unable to insert row into gmm transaction detail')
                                return False
                        commit_with_retry(session)
                        session.end_session()
                        break

                except (pymongo.errors.ConnectionFailure, pymongo.errors.OperationFailure) as exc:
                    # If transient error, retry the whole transaction
                    if exc.has_error_label("TransientTransactionError"):
                        print("TransientTransactionError transaction ...")
                        continue
                    else:
                        session.abort_transaction()
                        raise Exception

                return True
    except Exception as exc:
        session.abort_transaction()
        session.end_session()
        current_app.logger.error("Some exception has occured" + str(exc))
        return False


def process_payment(transaction_id, user_id, amount_to_be_processed):
    """
    :param transaction_id:
    :param user_id:
    :param amount_to_be_processed:
    :return:
    """
    try:
        """
        Get the amount to be applied
        Apply it to the user.
        If the amount is lesser than owed, apply to the user,  and apply the amount to the total, send a message to the group
        
        If the amount is greater than owed , 
            apply to the user, 
            revise the owed amount for the rest of the group
            apply the amount to the total, 
            send message to the group with the adjusted amount
        
        The GMM Detail Object in both cases should return the balance (-ve or +ve).
        
        """
        objDB = MongoDBFunctions()
        db = g.db.get_database("sample_airbnb")
        gmm_collection = pymongo.collection.Collection(db, "gmm_transaction")
        gmm_detail_collection = pymongo.collection.Collection(db, 'gmm_transaction_detail')
        with g.db.start_session() as session:

            while True:
                try:
                    with session.start_transaction():
                        obj_txn = GMMTransaction(
                            transaction_id=transaction_id
                        )
                        obj_user_txn_detail = GMMTransactionDetail(
                            transaction_id=transaction_id,
                            user_id=user_id)
                        obj_user_txn_detail.process_amount(
                            amount_to_be_processed)  # This will reset the transaction amount for the user
                        if obj_user_txn_detail.txn_amount > 0:
                            obj_txn.adjust_cost(obj_user_txn_detail.txn_amount)
                            if obj_txn.cost < 0:
                                # The last applied amount exceeded the cost of the transaction
                                # restate the user amount for the rest of the group
                                new_amount_to_be_applied = -obj_txn.cost / (obj_txn.total_members - 1)
                                obj_circle_detail = GMMTransactionDetail(transaction_id=transaction_id)

                                for obj_user_detail in obj_circle_detail.all:
                                    if obj_user_detail.user_id != user_id:
                                        obj_user_detail.txn_amount = new_amount_to_be_applied
                                    else:
                                        obj_user_detail.txn_amount = obj_user_txn_detail.txn_amount
                                    obj_user_detail.query_type = GMMDetailUpdateQueryType.TRANSACTION_AMOUNT_BASED
                                    if objDB.update_transaction_detail(gmm_detail_collection,
                                                                       obj_user_detail if obj_user_detail.user_id != user_id else obj_user_txn_detail,
                                                                       session):
                                        current_app.logger.update("Unable to update the transaction_detail")
                                        session.abort_transaction()
                                        return False
                                    # Update Message for app notification.
                                else:
                                    # The net transaction amount is lesser than the cost
                                    obj_user_txn_detail.query_type = GMMDetailUpdateQueryType.TRANSACTION_AMOUNT_BASED
                                    if objDB.update_transaction_detail(gmm_detail_collection,
                                                                       obj_user_txn_detail,
                                                                       session):
                                        current_app.logger.update("Unable to update the transaction_detail")
                                        session.abort_transaction()
                                        return False
                        obj_txn.query_type = GMMUpdateQueryType.TXN_AMOUNT_UPDATE
                        if objDB.update_transaction(gmm_collection, obj_txn, session):
                            current_app.logger.error("Unable to update the transaction" + obj_txn.transaction_id)
                            return False
                        commit_with_retry(session)
                        session.end_session()
                        break
                except (pymongo.errors.ConnectionFailure, pymongo.errors.OperationFailure) as exc:
                    # If transient error, retry the whole transaction
                    if exc.has_error_label("TransientTransactionError"):
                        print("TransientTransactionError transaction ...")
                        continue
                    else:
                        session.abort_transaction()
                        raise Exception
                return True
    except Exception as exc:
        session.abort_transaction()
        session.end_session()
        current_app.logger.error("Some exception has occured" + str(exc))
        return False


def initiate_team_buy(list_buyer, list_friend_circle):
    """

    :param list_buyer: should have product_id, friend_circle_id, occasion_id, occasion_date, user_id, first_name, last_name, phone_number, email_Address
    :param list_friend_circle: should have a list of user records with each user having first_name, last_name, phone_number, email_address
    :return:
    """

    try:
        objDB = MongoDBFunctions()
        db = g.db.get_database("sample_airbnb")
        gmm_buyer_initiated_info = pymongo.collection.Collection(db, "gmm_buyer_initiation")
        gmm_buyer_friend_circle = pymongo.collection.Collection(db, 'gmm_buyer_friend_circle')
        obj_buyer = None
        with g.db.start_session() as session:
            if objDB.get_initiated_buyer_info(gmm_buyer_initiated_info,
                                              obj_buyer,
                                              GMMBuyerIntiatedInfoReadQueryType.TXN_USER_OCCASION_PRODUCT_BASED,
                                              product_id=list_buyer["product_id"],
                                              friend_circle_id = list_buyer["friend_circle_id"],
                                              occasion_id = list_buyer["occasion_id"],
                                              user_id = list_buyer["user_id"],
                                              occasion_date = list_buyer["occasion_date"],
                                              session=session):
                if obj_buyer.total_members >= 0:
                    current_app.logger.error( "A transaction initiated by the user for this occasion and product exists")
                    return False

                obj_buyer = GMMInitiatedBuyInfo()
                obj_buyer.user_id = list_buyer["user_id"]
                obj_buyer.occasion_id = list_buyer["occasion_id"]
                obj_buyer.product_id = list_buyer["product_id"]
                obj_buyer.friend_circle_id = list_buyer["friend_circle_id"]
                obj_buyer.first_name = list_buyer["first_name"]
                obj_buyer.last_name = list_buyer["last_name"]
                obj_buyer.phone_number = list_buyer["phone_number"]
                obj_buyer.email_address = list_buyer["email_address"]
                obj_buyer.total_members = len(list_friend_circle)

                if not objDB.insert_buyer_initiated_info(gmm_buyer_initiated_info,obj_buyer,session=session):
                    current_app.logger.error("Unable to insert the buyer info into the db")
                    return False

                for user in list_friend_circle:
                    obj_buyer_friend_circle = GMMFriendCircleInfo()
                    obj_buyer_friend_circle.buyer_txn_id = obj_buyer.buyer_txn_id
                    obj_buyer_friend_circle.user_id = user["user_id"]
                    obj_buyer_friend_circle.first_name = user["first_name"]
                    obj_buyer_friend_circle.last_name = user["last_name"]
                    obj_buyer_friend_circle.phone_number = user["phone_number"]
                    obj_buyer_friend_circle.email_address = user["email_address"]
                    obj_buyer_friend_circle.voted_date = user["voted_date"]
                    obj_buyer_friend_circle.voted_value = user["voted_value"]

                    if not objDB.insert_buyer_friend_circle(gmm_buyer_friend_circle,obj_buyer_friend_circle,session=session):
                        current_app.logger.error("Unable to insert the friend circle detail into the db")
                        return False

    except Exception as exc:
        current_app.logger.error("There is an exception" + str(exc))
        session.abort_transaction()
        return False

def vote_team_buy(list_friend_circle):
    """

    :param list_friend_circle:
    :return:
    """
    try:
        objDB = MongoDBFunctions()
        db = g.db.get_database("sample_airbnb")
        gmm_buyer_friend_circle = pymongo.collection.Collection(db, 'gmm_buyer_friend_circle')
        obj_friend_circle = None
        with g.db.start_session() as session:
            try:
                with session.start_transaction():
                    if not objDB.get_buyer_friend_circle(gmm_buyer_friend_circle,
                                                     obj_friend_circle,
                                                     list_friend_circle["transaction_id"],
                                                     list_friend_circle["user_id"]
                                                    ):
                        current_app.logger.error("Unable to get the first circle information")
                        return False
                    if obj_friend_circle.first_name is not None:
                        obj_friend_circle = GMMFriendCircleInfo()
                        obj_friend_circle.user_id = list_friend_circle["user_id"]
                        obj_friend_circle.buyer_txn_id = list_friend_circle["transaction_id"]
                        obj_friend_circle.voted_value = list_friend_circle["voted_value"]
                        obj_friend_circle.voted_date = list_friend_circle["voted_date"]
                        if objDB.update_buyer_friend_circle(gmm_buyer_friend_circle, obj_friend_circle,session=session):
                            current_app.logger.error("Error in updating the buyer_friend_circle")
                            return False
                    else:
                        obj_buyer_friend_circle = GMMFriendCircleInfo()
                        obj_buyer_friend_circle.buyer_txn_id = list_friend_circle["transaction_id"]
                        obj_buyer_friend_circle.user_id = list_friend_circle["user_id"]
                        obj_buyer_friend_circle.first_name = list_friend_circle["first_name"]
                        obj_buyer_friend_circle.last_name = list_friend_circle["last_name"]
                        obj_buyer_friend_circle.phone_number = list_friend_circle["phone_number"]
                        obj_buyer_friend_circle.email_address = list_friend_circle["email_address"]
                        obj_buyer_friend_circle.voted_date = list_friend_circle["voted_date"]
                        obj_buyer_friend_circle.voted_value = list_friend_circle["voted_value"]

                        if not objDB.insert_buyer_friend_circle(gmm_buyer_friend_circle, obj_buyer_friend_circle,
                                                                session=session):
                            current_app.logger.error("Unable to insert the friend circle detail into the db")
                            return False
            except Exception as ex:
                return False
    except Exception as exc:
        current_app.logger.error("There is an exception" + str(exc))
        session.abort_transaction()
        return False

def get_initiated_buy_status(transaction_id, list_output_json: list):
    try:
        objDB = MongoDBFunctions()
        db = g.db.get_database("sample_airbnb")
        gmm_buyer_initiated_info = pymongo.collection.Collection(db, "gmm_buyer_initiation")
        gmm_buyer_friend_circle = pymongo.collection.Collection(db, 'gmm_buyer_friend_circle')
        obj_friend_circle = None
        obj_buyer = None

        if not objDB.get_initiated_buyer_info(gmm_buyer_initiated_info,
                                              obj_buyer,
                                              GMMBuyerIntiatedInfoReadQueryType.TRANSACTION_BASED,
                                              transaction_id=transaction_id):
            current_app.logger.error("Unable to get the first circle information")
            return False

        list_output_json.append(GMMEncoder.to_Json(obj_buyer))

        if objDB.get_buyer_friend_circle(gmm_buyer_friend_circle,obj_friend_circle,transaction_id=transaction_id):
            current_app.logger.error("Unable to get the buyer details for transaction_id" + transaction_id)
            return False

        for user in obj_friend_circle.all:
            list_output_json.append(GMMEncoder.to_Json(user))

        return True

    except Exception as exc:
        current_app.logger.error("Error in reading the initiated buy status" + str(exc))
        return False