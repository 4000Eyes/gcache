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
                session.abort_transaction()



def initiate_team_buy(hsh_buyer, list_friend_circle):
    """

    :param list_buyer: should have product_price, expiration_date, product_id, friend_circle_id, occasion_id, occasion_date, user_id, first_name, last_name, phone_number, email_Address
    :param list_friend_circle: should have a list of user records with each user having first_name, last_name, phone_number, email_address
    :return:
    """

    try:
        objDB = MongoDBFunctions()
        db = g.db.get_database("sample_airbnb")
        gmm_message = pymongo.collection.Collection(db, "gmm_message")
        gmm_buyer_initiated_info = pymongo.collection.Collection(db, "gmm_team_buy_info")
        gmm_buyer_friend_circle = pymongo.collection.Collection(db, 'gmm_buyer_friend_circle')
        list_buyer = []
        with g.db.start_session() as session:
            while True:
                try:
                    if objDB.get_initiated_buyer_info(gmm_buyer_initiated_info,
                                                      list_buyer,
                                                      GMMBuyerIntiatedInfoReadQueryType.PROD_OCCASION_CIRCLE_BASED,
                                                      product_id=hsh_buyer["product_id"],
                                                      friend_circle_id=hsh_buyer["friend_circle_id"],
                                                      occasion_id=hsh_buyer["occasion_id"],
                                                      user_id=hsh_buyer["user_id"],
                                                      occasion_date=hsh_buyer["occasion_date"],
                                                      session=None):
                        if len(list_buyer) > 0:
                            current_app.logger.error(
                                "A transaction initiated by the user for this occasion and product exists")
                            return 2
                        with session.start_transaction():
                            obj_buyer = GMMInitiatedBuyInfo()
                            obj_buyer.transaction_id = str(uuid.uuid4())
                            obj_buyer.user_id = hsh_buyer["user_id"]
                            obj_buyer.occasion_id = hsh_buyer["occasion_id"]
                            obj_buyer.occasion_date = hsh_buyer["occasion_date"]
                            obj_buyer.occasion_name = hsh_buyer["occasion_name"] if "occasion_name" in hsh_buyer else None
                            obj_buyer.product_id = hsh_buyer["product_id"]
                            obj_buyer.friend_circle_id = hsh_buyer["friend_circle_id"]
                            obj_buyer.first_name = hsh_buyer["first_name"]
                            obj_buyer.last_name = hsh_buyer["last_name"]
                            obj_buyer.phone_number = hsh_buyer["phone_number"]
                            obj_buyer.email_address = hsh_buyer["email_address"]
                            obj_buyer.product_price = hsh_buyer["product_price"]
                            obj_buyer.total_members = len(list_friend_circle)
                            obj_buyer.time_zone = hsh_buyer["time_zone"]
                            obj_buyer.expiration_date = hsh_buyer["expiration_date"]
                            obj_buyer.misc_cost = hsh_buyer["misc_cost"]
                            obj_buyer.notes = hsh_buyer["notes"]
                            obj_buyer.transaction_status = TeamBuyStatus.IN_DISCUSSION
                            obj_buyer.paying_members = len(list_friend_circle)

                            if not objDB.insert_buyer_initiated_info(gmm_buyer_initiated_info, obj_buyer,
                                                                     session=session):
                                current_app.logger.error("Unable to insert the buyer info into the db")
                                session.abort_transaction()
                                return -1

                            per_user_share = round(obj_buyer.product_price / obj_buyer.total_members, 2)

                            ar_creator = {}

                            ar_creator["user_id"] = hsh_buyer["user_id"]
                            ar_creator["first_name"] = hsh_buyer["first_name"]
                            ar_creator["last_name"] = hsh_buyer["last_name"]
                            ar_creator["phone_number"] = hsh_buyer["phone_number"]
                            ar_creator["email_address"] = hsh_buyer["email_address"]
                            if len(list_friend_circle) > 0:
                                ar_creator["opt_in_date"] = list_friend_circle[len(list_friend_circle)-1]["opt_in_date"]
                            else:
                                ar_creator["opt_in_date"] = None
                            ar_creator["opt_in_flag"] = "Y"
                            ar_creator["user_type"] = "Admin"
                            list_friend_circle.append(ar_creator)

                            for user in list_friend_circle:
                                obj_buyer_friend_circle = GMMFriendCircleInfo()
                                obj_buyer_friend_circle.transaction_id = obj_buyer.transaction_id
                                obj_buyer_friend_circle.user_id = user["user_id"]
                                obj_buyer_friend_circle.first_name = user["first_name"]
                                obj_buyer_friend_circle.last_name = user["last_name"]
                                obj_buyer_friend_circle.phone_number = user["phone_number"]
                                obj_buyer_friend_circle.email_address = user["email_address"]
                                obj_buyer_friend_circle.per_user_share = per_user_share
                                obj_buyer_friend_circle.recommended_share = per_user_share
                                obj_buyer_friend_circle.opt_in_date = user["opt_in_date"]
                                obj_buyer_friend_circle.opt_in_flag = user["opt_in_flag"]
                                obj_buyer_friend_circle.transaction_status = TeamBuyStatus.IN_DISCUSSION
                                obj_buyer_friend_circle.paid_amount = 0
                                obj_buyer_friend_circle.last_paid_date = "NA"
                                if "user_type" not in user:
                                    obj_buyer_friend_circle.user_type = "Contributor"
                                else:
                                    obj_buyer_friend_circle.user_type = user["user_type"]

                                if not objDB.insert_buyer_friend_circle(gmm_buyer_friend_circle,
                                                                        obj_buyer_friend_circle, session=session):
                                    current_app.logger.error("Unable to insert the friend circle detail into the db")
                                    return -1

                            message = str(obj_buyer_friend_circle.first_name) + " " + str(obj_buyer.first_name) + \
                                            " has initiated team buy. It expires " + str(obj_buyer.expiration_date) + \
                                            ". You share will be " + str(per_user_share)

                            if not explode_message(obj_buyer.transaction_id,
                                                   obj_buyer.friend_circle_id, MessageType.TEAM_BUY_INITIATED, message, session):
                                current_app.logger.error(
                                    "Unable to publish message")
                                return -1
                        commit_with_retry(session)
                        session.end_session()
                        break
                except Exception as ex:
                    current_app.logger.error("There is an exception" + str(ex))
                    session.abort_transaction()
                    return -1
            return True

    except Exception as exc:
        current_app.logger.error("There is an exception" + str(exc))
        session.abort_transaction()
        return -1


def update_with_user_payment(transaction_id, user_id, paid_amount):
    """
    :param list_friend_circle: should have transaction_id, user_id, paid_amount
    :return:
    """
    try:
        objDB = MongoDBFunctions()
        db = g.db.get_database("sample_airbnb")
        gmm_message = pymongo.collection.Collection(db,"gmm_message")
        gmm_buyer_initiated_info = pymongo.collection.Collection(db, "gmm_team_buy_info")
        gmm_buyer_friend_circle = pymongo.collection.Collection(db, 'gmm_buyer_friend_circle')

        obj_friend_circle = None
        obj_buyer = None
        user_paid_in_full = 0
        transaction_closed_flag = 0
        with g.db.start_session() as session:
            try:
                with session.start_transaction():

                    """
                    three things can happen:
                        - user decline to opt in to share price
                        - user paying the share
                        - user or initiator updating share price
                    
                    What should happen when the user pay amount?
                    - Update buyer friend circle
                    - Update team buy info
                    - If updating the team buy closes the transaction send a notification to the group about completion
                    - If not update the team about progress
                    """

                    list_buyer = []
                    if not objDB.get_initiated_buyer_info(gmm_buyer_initiated_info,
                                                          list_buyer,
                                                          GMMBuyerIntiatedInfoReadQueryType.TRANSACTION_BASED,
                                                          transaction_id=transaction_id):
                        current_app.logger.error("Unable to get the transaction header data")
                        return False
                    if len(list_buyer) <= 0:
                        current_app.logger.error("No transaction with this transaction id exists " + str(transaction_id))
                        return False
                    obj_buyer = list_buyer.pop()
                    list_friend_circle = []
                    if not objDB.get_buyer_friend_circle(gmm_buyer_friend_circle,
                                                         list_friend_circle,
                                                         GMMBuyerFriendCircleReadQueryType.TXN_USER_BASED,
                                                         transaction_id=transaction_id,
                                                         user_id=user_id
                                                         ):
                        current_app.logger.error("Unable to get the first circle information")
                        return False
                    if len(list_friend_circle) <= 0:
                        current_app.logger.error("We have an issue. Couldn't identify the user")
                        return False
                    obj_friend_circle = list_friend_circle.pop()

                    obj_friend_circle.paid_amount = obj_friend_circle.paid_amount + round(
                        int(paid_amount), 2)

                    if obj_friend_circle.paid_amount == obj_friend_circle.per_user_share:
                        user_paid_in_full = 1
                    obj_buyer.paid_amount = obj_buyer.paid_amount + round(
                        int(paid_amount), 2)
                    if obj_buyer.paid_amount == obj_buyer.product_price + obj_buyer.misc_cost:
                        # the transaction should be closed
                        transaction_closed_flag = 1

                    if not objDB.update_initiated_buyer_info(gmm_buyer_initiated_info, obj_buyer, GMMBuyerIntiatedInfoUpdateQueryType.TRANSACTION_BASED, session=session):
                        current_app.logger.error("Error in updating the team buy info with the adjusted amount")
                        return False

                    if not objDB.update_buyer_friend_circle(gmm_buyer_friend_circle,
                                                        obj_friend_circle,
                                                        GMMBuyerFriendCircleUpdateQueryType.TXN_USER_BASED,
                                                        session=session):
                        current_app.logger.error("Error in updating the buyer_friend_circle")
                        return False

                    if transaction_closed_flag:
                        # Message the group that the transaction is closed
                        message = "Friends, We did it... All of you paid your dues. Thank you! "
                        if not explode_message(obj_buyer.transaction_id,obj_buyer.friend_circle_id,MessageType.TRANSACTION_CLOSED, message, session=session):
                            current_app.logger.error("Unable to publish message")
                            return False
                        return True

                    if user_paid_in_full:
                        message = "Group " + str(
                            obj_friend_circle.first_name) + "paid his share. Just let you all know "
                        if not explode_message(obj_buyer.transaction_id,obj_buyer.friend_circle_id,MessageType.USER_PAID, message, session=session):
                            current_app.logger.error("Unable to publish message to broadcast the amount paid by " + str(obj_friend_circle.first_name))
                            return False

            except Exception as ex:
                return False
    except Exception as exc:
        current_app.logger.error("There is an exception" + str(exc))
        session.abort_transaction()
        return False


def opt_out( transaction_id, user_id,opt_in_flag):
    try:
        objDB = MongoDBFunctions()
        db = g.db.get_database("sample_airbnb")
        gmm_message = pymongo.collection.Collection(db, "gmm_message")
        gmm_buyer_initiated_info = pymongo.collection.Collection(db, "gmm_team_buy_info")
        gmm_buyer_friend_circle = pymongo.collection.Collection(db, 'gmm_buyer_friend_circle')
        zero_members_flag = 0
        with g.db.start_session() as session:
            try:
                with session.start_transaction():

                    transaction_closed_flag = 0
                    list_buyer = []
                    if not objDB.get_initiated_buyer_info(gmm_buyer_initiated_info,
                                                          list_buyer,
                                                          GMMBuyerIntiatedInfoReadQueryType.TRANSACTION_BASED,
                                                          transaction_id=transaction_id):
                        current_app.logger.error("Unable to get the transaction header data")
                        return False


                    if list_buyer is None or len(list_buyer) <= 0:
                        current_app.logger.error("Unable to extract the transaction header for " + str(transaction_id))
                        return False

                    obj_buyer = list_buyer.pop()

                    if obj_buyer.paying_members >= 1:
                        # check if there is already adjustment to the per user amount
                        # check if a user has agreed to pay more or lesser than the original suggested amount
                        # if the changes come after the transaction has started, the net change should go to
                        # the initiator
                        obj_buyer.paying_members = obj_buyer.paying_members - 1
                        if not obj_buyer.paying_members >=1:
                            zero_members_flag = 1
                            current_app.logger.info("Transaction should be closed. No user available to take the adjusted amount")
                            return False
                    else:
                        current_app.logger.error("opting out in one member circle is not possible")
                        return False

                    obj_friend_circle = []
                    if not objDB.get_buyer_friend_circle(gmm_buyer_friend_circle,
                                                         obj_friend_circle,
                                                         GMMBuyerFriendCircleReadQueryType.TRANSACTION_BASE,
                                                         transaction_id=transaction_id
                                                         ):
                        current_app.logger.error("Unable to get the first circle information")
                        return False
                    if len(obj_friend_circle) <= 0:
                        current_app.logger.error("We have an issue. Couldn't identify the user")
                        return False

                    owed_amount = 0
                    for user in obj_friend_circle:
                        if user_id == user.user_id and user.opt_in_flag == "Y": # ensure we are opting out user who is opted in otherwise we will screw up the per shar
                            owed_amount = user.per_user_share

                    if owed_amount == 0:
                        # Need to decide what to do
                        pass

                    new_adjusted_per_share_amount = 0
                    message_first_name = None
                    message_last_name = None
                    for new_obj_friend_circle in obj_friend_circle:
                        if obj_buyer.transaction_status == TeamBuyStatus.IN_DISCUSSION:
                            if user_id == new_obj_friend_circle.user_id:
                                new_obj_friend_circle.opt_in_flag = opt_in_flag
                                message_last_name = new_obj_friend_circle.last_name
                                message_first_name = new_obj_friend_circle.first_name
                                new_obj_friend_circle.per_user_share = 0
                                new_obj_friend_circle.opt_in_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                            else:
                                new_obj_friend_circle.per_user_share = new_obj_friend_circle.per_user_share + \
                                                                       owed_amount/obj_buyer.paying_members

                            if not objDB.update_buyer_friend_circle(gmm_buyer_friend_circle, new_obj_friend_circle,
                                                                GMMBuyerFriendCircleUpdateQueryType.TXN_USER_BASED,
                                                                session=session):
                                current_app.logger.error("Issue updating the buyer circle for user " + str(new_obj_friend_circle.user_id))
                                return False

                    obj_buyer.adjusted_per_user_amount = obj_buyer.adjusted_per_user_amount + (owed_amount/obj_buyer.paying_members)

                    if not objDB.update_initiated_buyer_info(gmm_buyer_initiated_info, obj_buyer, GMMBuyerIntiatedInfoUpdateQueryType.PAYING_MEMBERS):
                        current_app.logger.error("Unable to update the team buy info with the adjusted total members" + str(obj_buyer.transaction_id_))
                        return False

                    message = "Just FYI. " + str(message_first_name)  + " " + str(message_last_name) + " has opted out"
                    message_date_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    active_status = 1
                    if not objDB.insert_message(gmm_message,obj_buyer.friend_circle_id,obj_buyer.user_id, obj_buyer.transaction_id,
                                                MessageType.USER_OPTED_OUT.value,message,message_date_time,active_status,session=session):
                        current_app.logger.error("Unable to publish the message for opt-out" + str(obj_buyer.user_id))
                        session.abort_transaction()
                        return False
                commit_with_retry(session)
                session.end_session()
                return True
            except Exception as e:
                current_app.logger.error("There is an except during opt-out handling" + str(e))
                return  False
    except Exception as e:
        current_app.logger.error("There is an except during opt-out handling" + str(e))
        return False

        # calculate new per share value for each user

        # update team buy info with the adjusted amount

def update_team_buy_status(transaction_id, transaction_status):
    try:
        objDB = MongoDBFunctions()
        db = g.db.get_database("sample_airbnb")
        gmm_message = pymongo.collection.Collection(db, "gemift_messages")
        gmm_buyer_initiated_info = pymongo.collection.Collection(db, "gmm_team_buy_info")

        obj_buyer = None
        with g.db.start_session() as session:
            try:
                with session.start_transaction():

                    transaction_closed_flag = 0
                    list_buyer = []
                    if not objDB.get_initiated_buyer_info(gmm_buyer_initiated_info,list_buyer,GMMBuyerIntiatedInfoReadQueryType.TRANSACTION_BASED,
                                                          transaction_id=transaction_id,  session=session):
                        current_app.logger.error("Unable to get the team buy info for transaction id" + str(transaction_id))
                        return False
                    obj_buyer = list_buyer.pop()
                    obj_buyer.transaction_id = transaction_id
                    obj_buyer.transaction_status = transaction_status

                    if not objDB.update_initiated_buyer_info(gmm_buyer_initiated_info,obj_buyer, GMMBuyerIntiatedInfoUpdateQueryType.UPDATE_STATUS,
                                                        session=session):
                        current_app.logger.error(
                            "Issue updating the buyer circle for user " + str(obj_buyer.transaction_id))
                        return False
                    if transaction_status == 1: # cancel
                        message = "Team " + str(obj_buyer.first_name) + " has cancelled the buy. That is a bummer"
                    elif transaction_status == 2: # activate
                        message = "Team " + str(obj_buyer.first_name) + " has activated the buy. Pl pay before the expiration date. Be Kind to your friend :)"
                    elif transaction_status == 3: # complete
                        message = "Team " + str(obj_buyer.first_name) + " has completed the transaction . Good job everyone"

                    if not explode_message(obj_buyer.transaction_id,obj_buyer.friend_circle_id,MessageType.TRANSACTION_ACTIVATED,message,session=session):
                        current_app.logger.error("Unable to send the transaction activated message to the group")
                        return False
                commit_with_retry(session)
                session.end_session()
                return True
            except Exception as e:
                current_app.logger.error("Facing an exception" + str(e))
                return False
    except Exception as e:
        current_app.logger.error("Facing an exception" + str(e))
        return False

def adjusted_user_share(transaction_id, user_id, adjusted_price ):

    try:
        objDB = MongoDBFunctions()
        db = g.db.get_database("sample_airbnb")
        gmm_message = pymongo.collection.Collection(db, "gmm_message")
        gmm_buyer_initiated_info = pymongo.collection.Collection(db, "gmm_team_buy_info")
        gmm_buyer_friend_circle = pymongo.collection.Collection(db, 'gmm_buyer_friend_circle')
        obj_friend_circle = None
        obj_buyer = None
        adjusted_per_user_share = 0
        with g.db.start_session() as session:
            try:
                with session.start_transaction():
                    transaction_closed_flag = 0
                    list_buyer = []
                    if not objDB.get_initiated_buyer_info(gmm_buyer_initiated_info,
                                                          list_buyer,
                                                          GMMBuyerIntiatedInfoReadQueryType.TRANSACTION_BASED,
                                                          transaction_id=transaction_id):
                        current_app.logger.error("Unable to get the transaction header data")
                        return False
                    if len(list_buyer) <= 0:
                        current_app.logger.error("Detail for the given transaction id doesnt exist" + str(transaction_id))
                        return False
                    obj_buyer = list_buyer.pop()

                    list_friend_circle = []

                    if not objDB.get_buyer_friend_circle(gmm_buyer_friend_circle,
                                                         list_friend_circle,
                                                         GMMBuyerFriendCircleReadQueryType.TRANSACTION_BASE,
                                                         transaction_id=transaction_id
                                                         ):
                        current_app.logger.error("Unable to get the first circle information")
                        return False
                    if len(list_friend_circle) <= 0:
                        current_app.logger.error("We have an issue. Couldn't identify the user")
                        return False
                    balance = 0
                    for adjusted_user_info in list_friend_circle:
                        if adjusted_user_info.user_id == user_id and adjusted_user_info.opt_in_flag == "Y":
                            balance = round(adjusted_user_info.per_user_share - adjusted_price, 2)
                            break
                    if not balance:
                        current_app.logger.info("There is not adjustment required as the user is not decrementing or incrementing the amount")
                        return True
                    new_adjusted_per_share_amount = 0

                    for new_obj_friend_circle in list_friend_circle:
                        if new_obj_friend_circle.opt_in_flag == 'N':
                            continue
                        if user_id == new_obj_friend_circle.user_id:
                            new_obj_friend_circle.per_user_share = adjusted_price
                            new_obj_friend_circle.recommended_share = adjusted_price
                        else:
                            if obj_buyer.paying_members - 1 <= 0:
                                break

                            adjusted_per_user_share = new_obj_friend_circle.per_user_share + (
                                        balance / (obj_buyer.paying_members - 1))
                            new_obj_friend_circle.per_user_share = new_obj_friend_circle.per_user_share + (balance/(obj_buyer.paying_members -1))

                        if not objDB.update_buyer_friend_circle(gmm_buyer_friend_circle, new_obj_friend_circle,
                                                            GMMBuyerFriendCircleUpdateQueryType.TXN_USER_BASED,
                                                            session=session):

                            current_app.logger.error("Issue updating the buyer circle for user " + str(new_obj_friend_circle.user_id))
                            return False

                    obj_buyer.adjusted_per_user_share = adjusted_per_user_share
                    if not objDB.update_initiated_buyer_info(gmm_buyer_initiated_info,obj_buyer,GMMBuyerIntiatedInfoUpdateQueryType.PAYING_MEMBERS, session=session):
                        current_app.logger.error("unable to update buyer info with the adjusted share value")
                        return False

                    if balance > 0:
                        str_message = str(balance) + " will be added to each one of your account"
                    else:
                        str_message = str(balance) + " will be reduce from each one of your share"

                    active_status = 1
                    message_datetime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

                    if not objDB.insert_message(gmm_message,obj_buyer.friend_circle_id,obj_buyer.user_id,obj_buyer.transaction_id,
                                                MessageType.SHARE_CHANGED.value,str_message,message_datetime,active_status,
                                                commodity_id=obj_buyer.product_id,session=session):
                        current_app.logger.error("Unable to insert message into the table")
                        session.abort_transaction()
                        return False

                commit_with_retry(session)
                session.end_session()
                return True
            except Exception as e:
                current_app.logger.error("There is an exception" + str(e))
                return  False
    except Exception as e:
        current_app.logger.error("There is an exception" + str(e))
        return False

def get_team_buy_status(transaction_id, list_output_json: list):
    try:
        objDB = MongoDBFunctions()
        db = g.db.get_database("sample_airbnb")
        gmm_buyer_initiated_info = pymongo.collection.Collection(db, "gmm_team_buy_info")
        gmm_buyer_friend_circle = pymongo.collection.Collection(db, 'gmm_buyer_friend_circle')
        list_friend_circle = []
        list_buyer = []

        if not objDB.get_initiated_buyer_info(gmm_buyer_initiated_info,
                                              list_buyer,
                                              GMMBuyerIntiatedInfoReadQueryType.TRANSACTION_BASED,
                                              transaction_id=transaction_id):
            current_app.logger.error("Unable to get the first circle information")
            return False

        list_output_json.append(GMMEncoder.to_Json(list_buyer.pop()))


        if not objDB.get_buyer_friend_circle(gmm_buyer_friend_circle, list_friend_circle, GMMBuyerFriendCircleReadQueryType.TRANSACTION_BASE, transaction_id=transaction_id):
            current_app.logger.error("Unable to get the buyer details for transaction_id" + transaction_id)
            return False

        for user in list_friend_circle:
            list_output_json.append(GMMEncoder.to_Json(user))

        return True

    except Exception as exc:
        current_app.logger.error("Error in reading the initiated buy status" + str(exc))
        return False

def get_team_buy_status_by_user(user_id, list_output_json: list):
    try:
        objDB = MongoDBFunctions()
        db = g.db.get_database("sample_airbnb")
        gmm_buyer_initiated_info = pymongo.collection.Collection(db, "gmm_team_buy_info")
        gmm_buyer_friend_circle = pymongo.collection.Collection(db, 'gmm_buyer_friend_circle')
        list_friend_circle = []
        list_buyer = []

        if not objDB.get_initiated_buyer_info(gmm_buyer_initiated_info,
                                              list_buyer,
                                              GMMBuyerIntiatedInfoReadQueryType.USER_BASED,
                                              user_id=user_id):
            current_app.logger.error("Unable to get the first circle information")
            return False
        hsh_buyer = {}
        for txn in list_buyer:
            hsh_buyer[txn.transaction_id] = txn
            #list_output_json.append(GMMEncoder.to_Json(txn))

        if not objDB.get_buyer_friend_circle(gmm_buyer_friend_circle, list_friend_circle,
                                         GMMBuyerFriendCircleReadQueryType.USER_BASED, user_id=user_id):
            current_app.logger.error("Unable to get the buyer details for transaction_id" + str(user_id))
            return False
        hsh_user = {}
        for user in list_friend_circle:

            if user.transaction_id in hsh_buyer:

                hsh_user["friend_circle_id"] = hsh_buyer[user.transaction_id].friend_circle_id
                hsh_user["product_id"] = hsh_buyer[user.transaction_id].product_id
                hsh_user["occasion_id"] = hsh_buyer[user.transaction_id].occasion_id
                hsh_user["initiated_date"] = hsh_buyer[user.transaction_id].initiated_date
                hsh_user["expiration_date"] = hsh_buyer[user.transaction_id].expiration_date
                hsh_user["total_members"] = hsh_buyer[user.transaction_id].total_members
                hsh_user["product_price"] = hsh_buyer[user.transaction_id].product_price
                hsh_user["paid_amount"] = hsh_buyer[user.transaction_id].paid_amount

                hsh_user["user_type"] = user.user_type
                hsh_user["opt_in_flag"] = user.opt_in_flag
                hsh_user["per_user_share"] = user.per_user_share
                hsh_user["transaction_status"] = user.transaction_status
                hsh_user["transaction_id"] = user.transaction_id
                hsh_user["user_id"] = user.user_id

                list_output_json.append(hsh_user)

            else:
                current_app.logger.error("A detail transaction exist without a header for " + str(user.transaction_id))
                return False
        return True

    except Exception as exc:
        current_app.logger.error("Error in reading the initiated buy status" + str(exc))
        return False

def publish_message(user_id,list_output_json: list):

    try:
        objDB = MongoDBFunctions()
        db = g.db.get_database("sample_airbnb")
        gmm_message = pymongo.collection.Collection(db, "gemift_messages")
        obj_message = GMMMessage()
        if not objDB.publish_message(gmm_message,obj_message,user_id):
            current_app.logger.error("Unable to retrieve messages for the given user_id")
            return user_id

        for m in obj_message.all:
            list_output_json.append(GMMEncoder.to_Json(m))
        return True
    except Exception as exc:
        current_app.logger.error("Error in reading the initiated buy status" + str(exc))
        return False

def explode_message(transaction_id, friend_circle_id, message_type, message, session):
    try:
        objDB = MongoDBFunctions()
        db = g.db.get_database("sample_airbnb")
        gmm_message = pymongo.collection.Collection(db, "gemift_messages")
        gmm_buyer_friend_circle = pymongo.collection.Collection(db, 'gmm_buyer_friend_circle')
        w_friend_circle = []
        if not objDB.get_buyer_friend_circle(gmm_buyer_friend_circle,
                                             w_friend_circle,
                                             GMMBuyerFriendCircleReadQueryType.TRANSACTION_BASE,
                                             transaction_id=transaction_id,
                                             session=session
                                             ):
            current_app.logger.error("Unable to get the first circle information")
            return False
        if len(w_friend_circle) <= 0:
            current_app.logger.error("We have an issue. Couldn't identify the user")
            return False

        for obj_friend in w_friend_circle:
            message_datetime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            active_status = 1
            if obj_friend.opt_in_flag == "Y":
                if message_type != MessageType.SHARE_CHANGED:
                    if obj_friend.user_type == "Admin" and message_type == MessageType.TEAM_BUY_INITIATED:
                        admin_message = "The team buy details have been successfully broadcasted to the group"
                        if not objDB.insert_message(gmm_message,friend_circle_id, obj_friend.user_id, obj_friend.transaction_id,
                                                    message_type.value,admin_message, message_datetime, active_status, session=session):
                            current_app.logger.error("Unable to create message for the given transaction type")
                            return False
                    else:
                        if not objDB.insert_message(gmm_message,friend_circle_id, obj_friend.user_id, obj_friend.transaction_id,
                                                    message_type.value,message, message_datetime, active_status, session=session):
                            current_app.logger.error("Unable to create message for the given transaction type")
                            return False
                else:
                    active_status = 0
                    if not objDB.update_message(gmm_message,obj_friend.user_id, obj_friend.transaction_id,
                                                MessageType.TEAM_BUY_INITIATED.value, active_status, session=session):
                        current_app.logger.error("Unable to adjust message")
                        return False

        return True
    except Exception as exc:
        current_app.logger.error("Error in reading the initiated buy status" + str(exc))
        return False