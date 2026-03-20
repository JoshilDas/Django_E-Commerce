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
from rest_framework.exceptions import ParseError


def extract_message(data, default):
    # Handles dict, list, string
    if isinstance(data, dict):
        # Try DRF standard
        if "detail" in data:
            return data["detail"]

        # Try first field error
        first_key = next(iter(data), None)
        if first_key:
            value = data[first_key]
            if isinstance(value, list) and value:
                return value[0]
            return str(value)

    elif isinstance(data, list) and data:
        return data[0]

    return default


def custom_exception_handler(exc, context):

    response = exception_handler(exc, context)

    if response is not None:
        message = extract_message(response.data, "An error occurred")
        code = getattr(exc, "default_code", None)

        if isinstance(exc, ValidationError):
            return ApiResponse.validation_error(
                errors=response.data,
                message="Validation failed",
                code="VALIDATION_ERROR",   
            )

        if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
            return ApiResponse.unauthorized(
                message=message,
                code=code or "AUTH_REQUIRED",
            )

        if isinstance(exc, ParseError):
            return ApiResponse.validation_error(
                message=message,
                errors=[message],
                code=getattr(exc, "default_code", "parse_error"),
            )

        if isinstance(exc, PermissionDenied):
            return ApiResponse.forbidden(
                message=message,
                code=code or "PERMISSION_DENIED",
            )

        if isinstance(exc, NotFound):
            return ApiResponse.not_found(
                message=message,
                code=code or "RESOURCE_NOT_FOUND",
            )

        if isinstance(exc, Throttled):
            return ApiResponse.throttled(
                message=message,
                code=code or "RATE_LIMIT_EXCEEDED",
            )

        return ApiResponse.error(
            message=message,
            code=code,
        )

    return ApiResponse.server_error(debug=str(exc))