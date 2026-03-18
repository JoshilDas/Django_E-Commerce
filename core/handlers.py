from django.http import JsonResponse
from core.constants import RESPONSE_TYPE_NOT_FOUND


def custom_404_handler(request, exception):
    return JsonResponse(
        {
            "success": False,
            "type": RESPONSE_TYPE_NOT_FOUND,
            "message": "Endpoint not found",
            "code": "RESOURCE_NOT_FOUND",
        },
        status=404,
    )


def custom_500_handler(request):
    return JsonResponse(
        {
            "success": False,
            "type": "SERVER_ERROR",
            "message": "Internal server error",
        },
        status=500,
    )