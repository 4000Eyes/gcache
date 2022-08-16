from flask_restful import Resource
from flask import request
from gmm.model.gmm_processor import *
import requests
import json
"""
Team up and buy (Team up and buy is about sharing the cost of the product):


Gemift will remind circle to vote 30 days before the occasion. 
Gemift will ask the circle to "initiate buy" 15 days before the occasion (Only voted product can be chosen)
Any one from the group can initiate buy from the voted products (call it initiate buy)

The user initiating buy can adjust the amount and add notes for others to see.
You can buy more than one gift per occasion.

Initiate buy will give the following options to the user initiating the buy.

Option 1: Team up and buy will have two options:
    - Go ahead and buy, but let the circle know that they are sharing cost
    - Wait for circle to acknowledge before buying (set expiration date for this option)
    
    For either use case, a notification will go to all circle members asking them to opt in or opt out
    - Payment detail (cost sharing) will go to each user right away or after the expiration date 
Option 2: I am buying 
    - You are not expecting anyone to share the cost. You love this product and ordering for your friend/family

Once the transaction started. Following actions will happen until the transaction closed

- Create a new transaction - transaction, transaction_detail
- Post an update 
- Post a payment - (transaction_id, user_id, amount)
- Remove member and restate ( transaction_id, user_id)
- Cancel transaction (transaction_id)
- Get current state ( transaction_id)
- Get delayed payments (transaction_id or user_id)
    
"""

# Scenario 1: Pay Before Buy (Admin Led)

# - Decide on the product (through voting)
# Team up and Buy
# - Admin to check interest on sharing the cost
# - Admin having the ability to assign designated buyer from the group.
# - Share the amount, timeline for payment, split %
# - Notify circle about placing order
# - Notify about receiving or shipping
# - Close transaction
# - Keep sharing the transaction summary

# Scenario 2: Buy and Collect Later
#
# - Decide on product - /api/gmm/product{product_id, cost} {transaction_id}
# - Assign designated buyer - /api/gmm/assignbuyer
# - Notify group about buying ahead - /api/gmm/notify
# - Buy product or service
# - Notify circle about placing order - /api/gmm/notify
# - Check interest on sharing cost - /api/gmm/useropt/
# - Share the amount, timeline for payment, split % - /api/gmm/costmix
# - Pay designated buyer - /api/gmm/pay
# - Notify about receiving the gift or shipping the gift - /api/gmm/notify
# - Close transaction
#     - can be forced closure
#     - total fully paid or over paid
# - Keep sharing the transaction summary - /api/gmm/status{transaction_id}
#     - transaction
#     - start date
#     - amount and amount to be owed
#     - amount to be owed by user (first name, last name, phone number)

"""
possible calls:
- Initiate buy
- Acknowledgment Management
- Create a new transaction - transaction, transaction_detail
- Post an update 
- Post a payment - (transaction_id, user_id, amount)
- Remove member and restate ( transaction_id, user_id)
- Cancel transaction (transaction_id)
- Get current state ( transaction_id)
- Get delayed payments (transaction_id or user_id)


Transacction detail key methods:
    - Get number of days  before or after deadline
    
"""

# Execution workflow:
#
# The transaction should have the
#     - product
#     - Cost
#     - Buyer
#     - Buy type
#     - Split percent
#     - Ship Mode
#         - Direct to the secret friend
#         - Received by the admin
#         - Received by the contributor

buy_type = dict(
    ADMIN_LED_PAY_BEFORE_BUY=1,
    ADMIN_LED_BUY_COLLECT_LATER=2,
    CONTRIBUTOR_LED_PAY_BEFORE_BUY=3,
    CONTRIBUTOR_LED_BUY_COLLECT_LATER=4
)


class MoneyManager(Resource):
    def post(self):

        hsh_input = request.get_json()

        if hsh_input["request_type"] is None:
            return {"status": "request_type required"}

        # initiate team buy
        """
        :param
        list_buyer: should
        have
        product_price, expiration_date, product_id, friend_circle_id, occasion_id, occasion_date, user_id, first_name, last_name, phone_number, email_Address
        :param
        list_friend_circle: should
        have
        a
        list
        of
        user
        records
        with each user having first_name, last_name, phone_number, email_address
        """



        if hsh_input["request_type"] == "initiate_team_buy":
            if ("friend_circle_id" not in hsh_input or hsh_input["friend_circle_id"] is None ):
                current_app.logger.error("Friend circle id cannot be null")
                return {"status": "Missing element: Friend circle id is null"}, 400

            if ("product_id" not in hsh_input or hsh_input["product_id"] is None):
                current_app.logger.error("product id cannot be null")
                return {"status": "Missing element: product id is null"}, 400

            if ("expiration_date" not in hsh_input or hsh_input["expiration_date"] is None ):
                current_app.logger.error("expiration date cannot be null")
                return {"status": "Missing element: expiration is null"}, 400

            parameters = {
                "request_id": 1,
                "friend_circle_id" : hsh_input["friend_circle_id"]
            }
            response = requests.get("https://gemift-social-dot-gemift.uw.r.appspot.com/api/friend/circle", params=parameters)

            hsh_json_output = {}
            hsh_json_output = json.loads(response.text)
            list_json_output = hsh_json_output["friend_circle_id"]
            for indx in range(0, len(list_json_output)):
                if (list_json_output[indx]["relationship"] == "SECRET_FRIEND" or
                        list_json_output[indx]["user_id"] == hsh_input["user_id"]):
                    del list_json_output[indx]
                    continue

                list_json_output[indx].update({"opt_in_flag": "Y", "opt_in_date": datetime.now()})

            if len(list_json_output) <= 0:
                current_app.logger.error("There is no friend in the group to share the cost.")
                return {"Error": "There is no friend to share the cost. quitting team share"}, 400

            ret = initiate_team_buy(hsh_input, list_json_output)
            if ret == -1:
                current_app.logger.error("Error in creating a tteam buy record")
                return {"status": "Failure"}, 400
            if ret == 2:
                current_app.logger.info("The transaction already exists")
                return {"status": "Transaction exists"}, 400

            return {"status": "Success"}, 200


        # pay amount
        if hsh_input["request_type"] == "pay_amount":
            """
            transaction_id = "f35cb3df-1e6e-4431-bd42-f4e6f72ba3ac"
            user_id = "a1"
            paid_amount = 25.13
            
            """
            if not update_with_user_payment(hsh_input["transaction_id"],hsh_input["user_id"], hsh_input["paid_amount"]):
                current_app.logger.error("Unable to update the amount paid by the user")
                return {"status": "Failure"}, 400
            return {"status": "Success"}, 200
        """
        payload: 
        user_id, transaction_id, amount_to_be_applied, request_type = "pay amount"
        
        """

        # cancel transaction
        if hsh_input["request_type"] == "cancel_transaction":
            status_id = 4
            if not update_team_buy_status(hsh_input["transaction_id"], status_id):
                return {"status": "Failure in updating the status of the transaction"},400
            return {"status": "successfully adjusted the transaction"}, 200

        if hsh_input["request_type"] == "activate_transaction":
            status_id = 2
            if not update_team_buy_status(hsh_input["transaction_id"], status_id):
                return {"status": "Failure in updating the status of the transaction"},400
            return {"status": "successfully adjusted the transaction"}, 200

        if hsh_input["request_type"] == "complete_transaction":
            status_id = 3
            if not update_team_buy_status(hsh_input["transaction_id"], status_id):
                return {"status": "Failure in updating the status of the transaction"},400
            return {"status": "successfully adjusted the transaction"}, 200

        if hsh_input["request_type"] == "opt_out":
            transaction_id = "0501d255-ee74-42dd-8ec1-818ee2c8824b"
            user_id = "a3"
            opt_in_flag = "N"
            if not opt_out(hsh_input["transaction_id"], hsh_input["user_id"], hsh_input["opt_in_flag"]):
                return {"status" : "Failure in opting out"},400
            return {"status": "successfully executed the transaction"}, 200

        if hsh_input["request_type"] == "adjusted_user_share":
            adjusted_cost = 10
            transaction_id = "0501d255-ee74-42dd-8ec1-818ee2c8824b"
            user_id = "a1"
            if not adjusted_user_share(hsh_input["transaction_id"], hsh_input["user_id"], hsh_input["adjusted_cost"]):
                return {"status" : "Unable to set adjusted price"}, 400
            return {"status": "successfully adjusted the transaction"}, 200




    def get(self):

        request_type = request.args.get("request_type")
        transaction_id = request.args.get("transaction_id")
        user_id = request.args.get("user_id")

        list_output = []

        # get transaction status

        if request_type == "get_team_buy_status":
            if not get_team_buy_status(transaction_id, list_output):
                return {"status": "Unable to get the transaction status"}, 400
            return {"message": json.loads(json.dumps(list_output))}

        if request_type == "get_team_buy_status_by_user":
            if not get_team_buy_status_by_user(user_id, list_output):
                return {"status": "Unable to get the transaction status"}, 400
            return {"message": json.loads(json.dumps(list_output))}

        if request_type == "publish_message":
            if not publish_message(user_id, list_output):
                return {"status": "Unable to get the messsages for the given user_id"}, 400
            return {"message": json.loads(json.dumps(list_output))}
        # get delayed payments

        # get about to be delayed payments
