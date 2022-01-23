import json
import pymongo
import pymongo.errors, pymongo.collection
import uuid
import enum
from datetime import date, datetime


class PaymentStatus(enum.Enum):
    TO_BE_PROCESSED = 1
    IN_PROCESS = 2
    PROCESSED = 3

class GMMUpdateQueryType(enum.Enum):
    TRANSACTION_BASED_UPDATE = 1
    STATUS_BASED_UPDATE = 2
    TXN_AMOUNT_UPDATE = 3

class GMMReadQueryType(enum.Enum):
    TRANSACTION_BASED = 1
    PRODUCT_BASED = 2
    FRIEND_CIRCLE_BASED = 3
    TRANSACTION_STATUS_BASED = 4

class GMMDetailReadQueryType(enum.Enum):
    TRANSACTION_BASED = 1
    STATUS_BASED = 2
    USER_TRANSACTION_BASED = 3

class GMMDetailUpdateQueryType(enum.Enum):
    TRANSACTION_BASED = 1
    STATUS_BASED = 2
    TRANSACTION_AMOUNT_BASED = 3

class GMMBuyerIntiatedInfoReadQueryType(enum.Enum):
    TRANSACTION_BASED = 1
    USER_BASED = 2
    TXN_USER_OCCASION_PRODUCT_BASED = 3

class GMMEncoder(json.JSONEncoder):
    @classmethod
    def to_Json(self, o):
        return {self.beautify_key(k): v for k, v in vars(o).items()}

    def beautify_key(str):
        index = str.index('__')
        if index <= 0:
            return str
        return str[index + 2:]

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
    def __int__(self):
        self.__buyer_txn_id = None
        self.__user_id = None
        self.__first_name = None
        self.__last_name = None
        self.__phone_number = None
        self.__email_address = None
        self.__product_id = None
        self.__occasion_id = None
        self.__friend_circle_id = None
        self.__initiated_date = None
        self.__total_members = -1
        self.__status = None


    @property
    def buyer_txn_id(self):
        return self.__buyer_txn_id

    @buyer_txn_id.setter
    def buyer_txn_id(self, value):
        self.__buyer_txn_id = value


    @property
    def product_id(self):
        return self.__product_id

    @product_id.setter
    def product_id(self, value):
        self.__product_id = value


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
        self.__total_members = value


    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, value):
        self.__status = value

    def get_hash(self):
        return self.__dict__


class GMMFriendCircleInfo(GMMQueryType, GMMUser):
    def __int__(self):
        self.__user_id = None
        self.__buyer_txn_id = None
        self.__voted_date = None
        self.__vote_value = None

    @property
    def buyer_txn_id(self):
        return self.__buyer_txn_id

    @buyer_txn_id.setter
    def buyer_txn_id(self, value):
        self.__buyer_txn_id = value


    @property
    def voted_date(self):
        return self.__voted_date

    @voted_date.setter
    def voted_date(self, value):
        self.__voted_date = value

    @property
    def voted_value(self):
        return self.__voted_value

    @voted_value.setter
    def voted_value(self, value):
        self.__voted_value = value



class GMMAddress:
    def __init__(self, address1, address2, city, state, zipcode, country):
        self.__address1 = address1
        self.__address2 = address2
        self.__city = city
        self.__state = state
        self.__zipcode = zipcode
        self.__country = country

class GMMTransactionDetail:

    all = []

    def __init__(self, **kwargs):

        for key, value in kwargs.items():
            if key == "user_id":
                self.__user_id = value
            if key == "first_name":
                self.__first_name = value
            if key == "last_name":
                self.__last_name = value
            if key == "email_address":
                self.__email_address = value
            if key == "phone_number":
                self.__phone_number = value
            if key == "address1":
                self.__address1 = value
            if key == "address2":
                self.__address2 = value
            if key == "state":
                self.__state = value
            if key == "city":
                self.__city = value
            if key == "zip_code":
                self.__zip_code = value
            if key == "country":
                self.__country = value
            if key == "user_amount":
                self.__user_amount = value
            if key == "user_paid":
                self.__user_paid = value
            if key == "query_type":
                self.__query_type = value

            if key == "expiration_date":
                self.__expiration_date = value

            if key == "query_type":
                self.__query_type = value


    @property
    def query_type(self):
        return self.__query_type

    @query_type.setter
    def query_type(self, value):
        self.__query_type = value

    @property
    def user_id(self):
        return self.__user_id

    @user_id.setter
    def user_id(self, value):
        self.__user_id = value

    @property
    def query_type(self):
        return self.__query_type

    @query_type.setter
    def query_type(self, value):
        self.__query_type = value

    @property
    def expiration_date(self):
        return self.__expiration_date

    @expiration_date.setter
    def expiration_date(self, value):
        self.__expiration_date = value

    @property
    def user_paid(self):
        return self.__user_paid

    @user_paid.setter
    def user_paid(self, value):
        self.__user_paid = value

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
    def email_address(self):
        return self.__email_address

    @email_address.setter
    def email_address(self, value):
        self.__email_address = value

    @property
    def phone_number(self):
        return self.__phone_number

    @phone_number.setter
    def phone_number(self, value):
        self.__phone_number = value

    @property
    def address1(self):
        return self.__address1

    @address1.setter
    def address1(self, value):
        self.__address1 = value

    @property
    def address2(self):
        return self.__address2

    @address2.setter
    def address2(self, value):
        self.__address2 = value

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, value):
        self.__state = value

    @property
    def city(self):
        return self.__city

    @city.setter
    def city(self, value):
        self.__city = value

    @property
    def zip_code(self):
        return self.__zip_code

    @zip_code.setter
    def zip_code(self, value):
        self.__zip_code = value

    @property
    def country(self):
        return self.__country

    @country.setter
    def country(self, value):
        self.__country = value

    @property
    def user_amount(self):
        return self.__user_amount

    @user_amount.setter
    def user_amount(self, value):
        self.__user_amount = value

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, value):
        self.__status = value

    @property
    def transaction_id(self):
        return self.__transaction_id

    @transaction_id.setter
    def transaction_id(self, value):
        self.__transaction_id = value

    @property
    def txn_amount(self):
        return self.__txn_amount

    @txn_amount.setter
    def status(self, value):
        self.txn_amount = value

    @property
    def split_percent(self):
        return self.__split_percent

    @status.setter
    def __split_percent(self, value):
        self.__split_percent = value

    def process_amount(self, amount_to_be_processed):
        self.txn_amount = self.txn_amount - amount_to_be_processed





class GMMTransaction:

    __per_user_amount = 0

    def __init__(self, **kwargs):

        self.__transaction_id = None

        for key, value in kwargs.items():
            if key == "product_id":
                self.__product_id = value
            if key == "buy_type":
                self.__buy_type = value
            if key == "cost":
                self.__cost = value
            if key == "designated_buyer_id":
                self.__designated_buyer_id = value
            if key == "designated_receiver_id":
                self.__designated_receiver_id = value
            if key == "split_percent":
                self.__split_percent = value
            if key == "friend_circle_id":
                self.__friend_circle_id = value
            if key == "transaction_id":
                self.__transaction_id = value
            if key == "total_members":
                self.__total_members = value
            if key == "occasion_id":
                self.__occasion_id = value
            if key == "occasion_date":
                self.__occasion_date = value
            if key == "created_dt":
                self.__created_dt = value
            if key == "updated_dt":
                self.__updated_dt = value

            if key == "query_type":
                self.__query_type = value

    @property
    def created_dt(self):
        return self.__created_dt

    @created_dt.setter
    def created_dt(self, value):
        self.__created_dt = value

    @property
    def query_type(self):
        return self.__query_type

    @query_type.setter
    def query_type(self, value):
        self.__query_type = value

    @property
    def updated_dt(self):
        return self.__updated_dt

    @updated_dt.setter
    def updated_dt(self, value):
        self.__updated_dt = value

    @property
    def occasion_id(self):
        return self.__occasion_id

    @occasion_id.setter
    def occasion_id(self, value):
        self.__occasion_id = value

    @property
    def occasion_date(self):
        return self.__occasion_date

    @occasion_date.setter
    def occasion_date(self, value):
        self.__occasion_date = value

    @property
    def product_id(self):
        return self.__product_id

    @product_id.setter
    def product_id(self, value):
        self.__product_id = value

    @property
    def buy_type(self):
        return self.__buy_type

    @buy_type.setter
    def buy_type(self, value):
        self.__buy_type = value

    @property
    def cost(self):
        return self.__cost

    @cost.setter
    def cost(self, value):
        self.__cost = value

    @property
    def designated_buyer_id(self):
        return self.__designated_buyer_id

    @designated_buyer_id.setter
    def designated_buyer_id(self, value):
        self.__designated_buyer_id = value

    @property
    def designated_receiver_id(self):
        return self.__designated_receiver_id

    @designated_receiver_id.setter
    def designated_receiver_id(self, value):
        self.designated_receiver_id = value

    @property
    def split_percent(self):
        return self.__split_percent

    @split_percent.setter
    def split_percent(self, value):
        self.__split_percent = value

    @property
    def friend_circle_id(self):
        return self.__friend_circle_id

    @friend_circle_id.setter
    def friend_circle_id(self, value):
        self.__friend_circle_id = value

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, value):
        if self.__status is None:
            self.__status = 0
        self.__status = value

    @property
    def transaction_id(self):
        return self.__transaction_id

    @transaction_id.setter
    def transaction_id(self, value):
        self.__transaction_id = value


    @property
    def per_user_amount(self):
        return GMMTransaction.__per_user_amount

    @per_user_amount.setter
    def per_user_amount(self, value):
        GMMTransaction.__per_user_amount = value

    @property
    def total_members(self):
        return self.__total_members

    @total_members.setter
    def total_members(self, value):
        self.__total_members = value

    def init_transaction(self):
        """ This will read the transaction and the details"""
        pass


    def calculate_user_amount(self):
        assert self.total_members > 0, "total members cannot be zero"
        assert self.split_percent > 0, "split percent cannot be zero"
        self.per_user_amount =  (self.cost * self.split_percent) / self.total_members
        assert self.per_user_amount > 0, "transaction amount cannot be less than zero"

    def adjust_cost(self, amount_to_be_applied):
        self.cost = self.cost - amount_to_be_applied



    def kill_transaction(self):
        pass


