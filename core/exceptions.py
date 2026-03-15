from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Global DRF exception handler.
    Converts all errors into a standardized response format.
    """

    response = exception_handler(exc, context)

    if response is not None:
        message = "An error occurred"

        if isinstance(response.data, dict):
            message = response.data.get("detail", message)

        return Response(
            {
                "success": False,
                "message": message,
                "errors": response.data
            },
            status=response.status_code
        )

    # Handle unexpected errors (500)
    return Response(
        {
            "success": False,
            "message": "Internal server error",
            "errors": None
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )