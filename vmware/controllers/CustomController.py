import jwt

from django.conf import settings

from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication

from vmware.helpers.Log import Log


class CustomController(APIView):
    if not settings.DISABLE_AUTHENTICATION:
        permission_classes = [IsAuthenticated]
        authentication_classes = [JWTTokenUserAuthentication]



    @staticmethod
    def loggedUser(request: Request) -> dict:
        if settings.DISABLE_AUTHENTICATION:
            user = {
                "authDisabled": True,
                "groups": []
            }
        else:
            # Retrieve user from the JWT token.
            authenticator = request.successful_authenticator
            user = jwt.decode(
                authenticator.get_raw_token(authenticator.get_header(request)),
                settings.SIMPLE_JWT['VERIFYING_KEY'],
                settings.SIMPLE_JWT['ALGORITHM'],
                do_time_check=True
            )
            user["authDisabled"] = False

        return user



    @staticmethod
    def exceptionHandler(e: Exception) -> tuple:
        Log.logException(e)

        data = dict()
        headers = { "Cache-Control": "no-cache" }

        if e.__class__.__name__ == "TimeoutError" or (e.__class__.__name__ == "OSError" and e.strerror == "No route to host"):
            httpStatus = status.HTTP_504_GATEWAY_TIMEOUT
            data["error"] = {
                "network error": "No route to the vCenter server. "+e.__str__()
            }
        elif e.__class__.__name__ in ("ConnectionResetError", "ConnectionError", "ConnectTimeout", "Timeout", "TooManyRedirects", "SSLError", "HTTPError", "vim.fault.InvalidLogin") or (e.__class__.__name__ == "OSError" and e.errno == 0):
            httpStatus = status.HTTP_503_SERVICE_UNAVAILABLE
            data["error"] = {
                "network error": e.__str__()
            }
        elif e.__class__.__name__ in ("NoValidConnectionsError", "ChannelException", "BadHostKeyException", "SSHException", "timeout", "gaierror"):
            httpStatus = status.HTTP_503_SERVICE_UNAVAILABLE
            data["error"] = {
                "network error": e.__str__()
            }
        elif e.__class__.__name__ == "CustomException":
            httpStatus = e.status
            data["error"] = e.payload
        elif e.__class__.__name__ in ("AuthenticationException", "BadAuthenticationType"):
            data["error"] = {
                "network error": "Wrong ssh credentials or authentication type for the target. "+e.__str__()
            }
            httpStatus = status.HTTP_400_BAD_REQUEST # SshSupplicant: paramiko auth failed on target.
        elif e.__class__.__name__ == "ParseError":
            data = None
            httpStatus = status.HTTP_400_BAD_REQUEST # json parse.
        else:
            data = None
            httpStatus = status.HTTP_500_INTERNAL_SERVER_ERROR # generic.

        return data, httpStatus, headers
