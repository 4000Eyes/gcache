class UserAddError(Exception):
    pass


class FriendCircleAddError(Exception):
    pass


class SchemaValidationError(Exception):
    pass


class EmailDoesNotExistError(Exception):
    pass


class UserInsertionError(Exception):
    pass


errors = {
    "UserAddError": {
        "message": "Issues managing the user",
        "status": 400
    },
    "FriendCircleAddError": {
        "message": "Issues adding the friend circle",
        "status": 400
    },

    "SchemaValidationError": {
        "message": "Unable to get email from JSON",
        "status": 400
    },

    "EmailDoesNotExistError": {
        "message": "Valid email address doesnt exist in JSON",
        "status": 400
    },
    "UserInsertionError": {
        "message": "Unable to insert the user or user already exists",
        "status": 400
    }

}
