from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    ValidationError,
    NotAuthenticated,
    AuthenticationFailed,
    PermissionDenied,
    NotFound,
    Throttled,
)

from core.api_response import ApiResponse

def extract_message(data, default):
    if isinstance(data, dict):
        return data.get("detail", default)
    return default

def custom_exception_handler(exc, context):

    response = exception_handler(exc, context)

    if response is not None:

        if isinstance(exc, ValidationError):
            return ApiResponse.validation_error(errors=response.data,message="Validation failed")

        if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
            return ApiResponse.unauthorized(message=extract_message(response.data, "Authentication required"))

        if isinstance(exc, PermissionDenied):
            return ApiResponse.forbidden(message=extract_message(response.data, "Permission denied"))

        if isinstance(exc, NotFound):
            return ApiResponse.not_found(message=extract_message(response.data, "Resource not found"))

        if isinstance(exc, Throttled):
            return ApiResponse.throttled(message=extract_message(response.data,  "Too many requests"))

        return ApiResponse.error(message=extract_message(response.data, "An error occurred"))

    return ApiResponse.server_error(debug=str(exc))