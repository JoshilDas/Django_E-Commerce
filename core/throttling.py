from rest_framework.throttling import SimpleRateThrottle
from rest_framework.throttling import UserRateThrottle
from rest_framework.throttling import AnonRateThrottle


class UserThrottle(UserRateThrottle):
    scope = "user"


class AnonThrottle(AnonRateThrottle):
    scope = "anon"


class LoginIPThrottle(SimpleRateThrottle):
    """
    Throttle login attempts based on client IP address
    """

    scope = "login_ip"

    def get_cache_key(self, request, view):

        ident = self.get_ident(request)

        if ident is None:
            return None

        return self.cache_format % {
            "scope": self.scope,
            "ident": ident
        }