from rest_framework.exceptions import APIException


class InvalidUserException(APIException):
    status_code = 400
    default_detail = "Invalid user"
    default_code = "INVALID_USER"


class InvalidOTPException(APIException):
    status_code = 400
    default_detail = "Invalid OTP"
    default_code = "INVALID_OTP"


class OTPExpiredException(APIException):
    status_code = 400
    default_detail = "OTP expired"
    default_code = "OTP_EXPIRED"


class OTPBlockedException(APIException):
    status_code = 400
    default_detail = "Too many OTP attempts"
    default_code = "OTP_BLOCKED"