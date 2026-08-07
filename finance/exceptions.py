from rest_framework.exceptions import APIException


class ResourceConflict(APIException):
    status_code = 409
    default_detail = "The resource cannot be modified because it is in use."
    default_code = "resource_conflict"
