from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

from core.constants import (
    RESPONSE_TYPE_SUCCESS,
    RESPONSE_TYPE_ERROR,
    RESPONSE_TYPE_VALIDATION_ERROR,
    RESPONSE_TYPE_NOT_FOUND,
    RESPONSE_TYPE_UNAUTHORIZED,
    RESPONSE_TYPE_FORBIDDEN,
    RESPONSE_TYPE_THROTTLED,
    RESPONSE_TYPE_SERVER_ERROR,
)


class ApiResponse:

    @staticmethod
    def _build_response(
        *,
        success: bool,
        message: str,
        response_type: str,
        status_code: int,
        data=None,
        errors=None,
        code=None,
        meta=None,
        debug=None,
    ):
        body = {
            "success": success,
            "type": response_type,
            "message": message,
        }

        if success and data is not None:
            body["data"] = data

        if not success and errors is not None:
            body["errors"] = errors

        if code:
            body["code"] = code

        if meta:
            body["meta"] = meta

        if settings.DEBUG and debug is not None:
            body["debug"] = debug

        return Response(body, status=status_code)

    # ---------- SUCCESS ----------

    @staticmethod
    def success(data=None, message="Success", meta=None):
        return ApiResponse._build_response(
            success=True,
            message=message,
            response_type=RESPONSE_TYPE_SUCCESS,
            status_code=status.HTTP_200_OK,
            data=data,
            meta=meta,
        )

    @staticmethod
    def created(data=None, message="Created successfully"):
        return ApiResponse._build_response(
            success=True,
            message=message,
            response_type=RESPONSE_TYPE_SUCCESS,
            status_code=status.HTTP_201_CREATED,
            data=data,
        )

    @staticmethod
    def no_content(message="Deleted successfully"):
        return ApiResponse._build_response(
            success=True,
            message=message,
            response_type=RESPONSE_TYPE_SUCCESS,
            status_code=status.HTTP_204_NO_CONTENT,
        )

    # ---------- ERRORS ----------

    @staticmethod
    def error(message="An error occurred", code=None):
        return ApiResponse._build_response(
            success=False,
            message=message,
            response_type=RESPONSE_TYPE_ERROR,
            status_code=status.HTTP_400_BAD_REQUEST,
            code=code,
        )

    @staticmethod
    def validation_error(errors=None, message="Validation failed"):
        return ApiResponse._build_response(
            success=False,
            message=message,
            response_type=RESPONSE_TYPE_VALIDATION_ERROR,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            errors=errors,
        )

    @staticmethod
    def unauthorized(message="Authentication required", code="AUTH_REQUIRED"):
        return ApiResponse._build_response(
            success=False,
            message=message,
            response_type=RESPONSE_TYPE_UNAUTHORIZED,
            status_code=status.HTTP_401_UNAUTHORIZED,
            code=code,
        )

    @staticmethod
    def forbidden(message="Permission denied", code="PERMISSION_DENIED"):
        return ApiResponse._build_response(
            success=False,
            message=message,
            response_type=RESPONSE_TYPE_FORBIDDEN,
            status_code=status.HTTP_403_FORBIDDEN,
            code=code,
        )

    @staticmethod
    def not_found(message="Resource not found", code="RESOURCE_NOT_FOUND"):
        return ApiResponse._build_response(
            success=False,
            message=message,
            response_type=RESPONSE_TYPE_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
            code=code,
        )

    @staticmethod
    def throttled(message="Too many requests", code="RATE_LIMIT_EXCEEDED"):
        return ApiResponse._build_response(
            success=False,
            message=message,
            response_type=RESPONSE_TYPE_THROTTLED,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            code=code,
        )

    @staticmethod
    def server_error(message="Internal server error", debug=None):
        return ApiResponse._build_response(
            success=False,
            message=message,
            response_type=RESPONSE_TYPE_SERVER_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            debug=debug,
        )