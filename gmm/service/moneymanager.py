from flask_restful import Resource
from flask import request
from gmm.model.gmm_processor import process_transaction

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
            return {"status" : "request_type required"}

        # initiate team buy

        # vote for team buy

        # start transaction

        # pay amount

        # cancel transaction

        # remove user

        # adjust transaction amount

        # close transaction


    def get(self):

        request_type = request.args.get("request_type")


        # get transaction


        # get current status

        # get user info

        # get delayed payments

        # get about to be delayed payments


