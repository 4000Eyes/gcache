import json
import pymongo
import pymongo.errors, pymongo.collection
import uuid
from enum import IntEnum

from datetime import date, datetime


class TeamBuyStatus(IntEnum):
    IN_DISCUSSION = 1
    ACTIVATED = 2
    IN_PROGRESS = 30
    COMPLETE = 40
    CANCELLED = 50

class MessageType(IntEnum):
    TEAM_BUY_INITIATED = 999100
    SHARE_CHANGED = 999200
    PRODUCT_BOUGHT = 999300
    TRANSACTION_FORCE_CLOSED = 999400
    TRANSACTION_CLOSED = 999500
    USER_PAID = 999600
    USER_OPTED_OUT = 999700
    TRANSACTION_ACTIVATED = 999800

class GMMBuyerIntiatedInfoReadQueryType(IntEnum):
    TRANSACTION_BASED = 1
    USER_BASED = 2
    TXN_USER_OCCASION_PRODUCT_BASED = 3
    PROD_OCCASION_CIRCLE_BASED = 4

class GMMBuyerIntiatedInfoUpdateQueryType(IntEnum):
    TRANSACTION_BASED = 1
    TXN_USER_BASED = 2
    TXN_USER_OCCASION_PRODUCT_BASED = 3
    PROD_OCCASION_CIRCLE_BASED = 4
    UPDATE_STATUS = 5
    PAYING_MEMBERS = 6

class GMMBuyerFriendCircleReadQueryType(IntEnum):
    TRANSACTION_BASE = 1
    TXN_USER_BASED = 2
    USER_BASED = 3

class GMMBuyerFriendCircleUpdateQueryType(IntEnum):
    TRANSACTION_BASE = 1
    TXN_USER_BASED = 2

class GMMEncoder(json.JSONEncoder):
    @classmethod
    def to_Json(self, o):
        return {self.beautify_key(k): v for k, v in vars(o).items()}

    def beautify_key(str):
        index = str.index('__')
        if index <= 0:
            return str
        return str[index + 2:]

class GMMMessage():
    all = []
    def __init__(self):

        self.__friend_circle_id = None
        self.__user_id = None
        self.__message = None
        self.__message_type = None
        self.__transaction_id = None
        self.__message_datetime = None

    @property
    def user_id(self):
        return self.__user_id

    @user_id.setter
    def user_id(self, value):
        self.__user_id = value

    @property
    def message_datetime(self):
        return self.__message_datetime

    @message_datetime.setter
    def message_datetime(self, value):
        self.__message_datetime = value

    @property
    def transaction_id(self):
        return self.__transaction_id

    @transaction_id.setter
    def transaction_id(self, value):
        self.__transaction_id = value

    @property
    def friend_circle_id(self):
        return self.__friend_circle_id

    @friend_circle_id.setter
    def friend_circle_id(self, value):
        self.__friend_circle_id = value

    @property
    def message(self):
        return self.__message

    @message.setter
    def message(self, value):
        self.__message = value

    @property
    def message_type(self):
        return self.__message_type

    @message_type.setter
    def message_type(self, value):
        self.__message_type = value


class GMMUser:
    def __init__(self, user_id, first_name, last_name, email_address, phone_number):
        self.__user_id = user_id
        self.__first_name = first_name
        self.__last_name = last_name
        self._email_address = email_address
        self.__phone_number = phone_number

    @property
    def user_id(self):
        return self.__user_id

    @user_id.setter
    def user_id(self, value):
        self.__user_id = value

    @property
    def first_name(self):
        return self.__first_name

    @first_name.setter
    def first_name(self, value):
        self.__first_name = value

    @property
    def last_name(self):
        return self.__last_name

    @last_name.setter
    def last_name(self, value):
        self.__last_name = value

    @property
    def phone_number(self):
        return self.__phone_number

    @phone_number.setter
    def phone_number(self, value):
        self.__phone_number = value

    @property
    def email_address(self):
        return self.__email_address

    @email_address.setter
    def email_address(self, value):
        self.__email_address = value

class GMMQueryType:
    def __init__(self):
        self.__query_type = None

    @property
    def query_type(self):
        return self.__query_type

    @query_type.setter
    def query_type(self, value):
        self.__query_type = value

class GMMInitiatedBuyInfo(GMMQueryType, GMMUser):
    all = []
    def __init__(self):
        self.__transaction_id = None
        self.__user_id = None
        self.__first_name = None
        self.__last_name = None
        self.__phone_number = None
        self.__email_address = None
        self.__product_id = None
        self.__product_price = 0
        self.__misc_cost = 0
        self.__notes = None
        self.__occasion_id = None
        self.__occasion_name = None
        self.__occasion_date = None
        self.__friend_circle_id = None
        self.__initiated_date = None
        self.__total_members = -1
        self.__transaction_status = None
        self.__expiration_date = None
        self.__time_zone = None
        self.__paid_amount = 0
        self.__paying_members = 0
        self.__adjusted_per_user_amount = 0

    @property
    def transaction_id(self):
        return self.__transaction_id

    @transaction_id.setter
    def transaction_id(self, value):
        self.__transaction_id = value

    @property
    def product_id(self):
        return self.__product_id

    @product_id.setter
    def product_id(self, value):
        self.__product_id = value

    @property
    def paying_members(self):
        return self.__paying_members

    @paying_members.setter
    def paying_members(self, value):
        self.__paying_members = value

    @property
    def product_price(self):
        return self.__product_price

    @product_price.setter
    def product_price(self, value):
        assert type(value) == int or float, "value is not a number"
        self.__product_price = round(value,2)

    @property
    def paid_amount(self):
        return self.__paid_amount

    @paid_amount.setter
    def paid_amount(self, value):
        assert type(value) == int or float, "value is not a number"
        self.__paid_amount = round(value,2)

    @property
    def adjusted_per_user_amount(self):
        return self.__adjusted_per_user_amount

    @adjusted_per_user_amount.setter
    def adjusted_per_user_amount(self, value):
        assert type(value) == int or float, "value is not a number"
        self.__adjusted_per_user_amount = round(value,2)

    @property
    def misc_cost(self):
        return self.__misc_cost

    @misc_cost.setter
    def misc_cost(self, value):
        assert type(value) == int or float, "value is not a number"
        self.__misc_cost = round(value,2)

    @property
    def notes(self):
        return self.__notes

    @notes.setter
    def notes(self, value):
        self.__notes = value

    @property
    def expiration_date(self):
        return self.__expiration_date

    @expiration_date.setter
    def expiration_date(self, value):
        self.__expiration_date = value

    @property
    def time_zone(self):
        return self.__time_zone

    @time_zone.setter
    def time_zone(self, value):
        self.__time_zone = value

    @property
    def occasion_name(self):
        return self.__occasion_name

    @occasion_name.setter
    def occasion_name(self, value):
        self.__occasion_name = value
    @property
    def occasion_id(self):
        return self.__occasion_id

    @occasion_id.setter
    def occasion_id(self, value):
        self.__occasion_id = value

    @property
    def friend_circle_id(self):
        return self.__friend_circle_id

    @friend_circle_id.setter
    def friend_circle_id(self, value):
        self.__friend_circle_id = value

    @property
    def initiated_date(self):
        return self.__initiated_date

    @initiated_date.setter
    def initiated_date(self, value):
        self.__initiated_date = value


    @property
    def total_members(self):
        return self.__total_members

    @total_members.setter
    def total_members(self, value):
        assert type(value) == int or float, "value is not a number"
        self.__total_members = value


    @property
    def transaction_status(self):
        return self.__transaction_status

    @transaction_status.setter
    def transaction_status(self, value):
        self.__transaction_status = value


    @property
    def occasion_date(self):
        return self.__occasion_date

    @occasion_date.setter
    def occasion_date(self, value):
        self.__occasion_date = value


    def get_hash(self):
        return self.__dict__


class GMMFriendCircleInfo(GMMQueryType, GMMUser):
    all = []
    def __int__(self):
        self.__user_id = None
        self.__transaction_id = None
        self.__per_user_share = None
        self.__paid_amount = 0
        self.__last_paid_date = None
        self.__recommended_share = 0
        self.__opt_in_date = None
        self.__opt_in_flag = None
        self.__transaction_status = None
        self.__user_type = None
    @property
    def transaction_id(self):
        return self.__transaction_id

    @transaction_id.setter
    def transaction_id(self, value):
        self.__transaction_id = value

    @property
    def transaction_status(self):
        return self.__transaction_status

    @transaction_status.setter
    def transaction_status(self, value):
        self.__transaction_status = value

    @property
    def opt_in_date(self):
        return self.__opt_in_date

    @opt_in_date.setter
    def opt_in_date(self, value):
        self.__opt_in_date = value

    @property
    def opt_in_flag(self):
        return self.__opt_in_flag

    @opt_in_flag.setter
    def opt_in_flag(self, value):
        self.__opt_in_flag = value

    @property
    def user_type(self):
        return self.__user_type

    @user_type.setter
    def user_type(self, value):
        self.__user_type = value

    @property
    def per_user_share(self):
        return self.__per_user_share

    @per_user_share.setter
    def per_user_share(self, value):
        assert type(value) == int or float, "value is not a number"
        self.__per_user_share = round(value,2)

    @property
    def recommended_share(self):
        return self.__recommended_share

    @recommended_share.setter
    def recommended_share(self, value):
        assert type(value) == int or float, "value is not a number"
        self.__recommended_share = round(value,2)

    @property
    def paid_amount(self):
        return self.__paid_amount

    @paid_amount.setter
    def paid_amount(self, value):
        assert type(value) == int or float, "value is not a number"
        self.__paid_amount = round(value,2)

    @property
    def last_paid_date(self):
        return self.__last_paid_date

    @last_paid_date.setter
    def last_paid_date(self, value):
        self.__last_paid_date = value



