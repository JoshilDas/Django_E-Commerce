from rest_framework.response import Response


def success_response(data=None, message="Success", status=200):
    """
    Standard success response wrapper
    """

    return Response(
        {
            "success": True,
            "message": message,
            "data": data
        },
        status=status
    )


def error_response(message="Error", errors=None, status=400):
    """
    Standard error response wrapper
    """

    return Response(
        {
            "success": False,
            "message": message,
            "errors": errors
        },
        status=status
    )