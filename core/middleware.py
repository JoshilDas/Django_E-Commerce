# core/middleware.py

import time
import logging

logger = logging.getLogger("api")


class APILoggingMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        start_time = time.time()

        response = self.get_response(request)

        duration = time.time() - start_time

        user = "anonymous"
        if request.user.is_authenticated:
            user = request.user.email

        logger.info(
            f"{request.method} {request.path} "
            f"status={response.status_code} "
            f"user={user} "
            f"time={duration:.3f}s"
        )

        return response