import functools

import jwt
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response


def custom_exception_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (
            jwt.exceptions.ExpiredSignatureError,
            jwt.exceptions.InvalidTokenError,
        ) as e:
            return Response(
                data={"error": "InvalidTokenError", "error_message": str(e)},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except NotFound as e:
            return Response(
                data={"error": "NotFound", "error_message": str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )
        except PermissionError as e:
            return Response(
                data={"error": "PermissionError", "error_message": str(e)},
                status=status.HTTP_403_FORBIDDEN,
            )
        except IntegrityError as e:
            return Response(
                data={"error": "IntegrityError", "error_message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except ValidationError as e:
            return Response(
                data={"error": "ValidationError", "error_message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ObjectDoesNotExist as e:
            return Response(
                data={"error": "ObjectDoesNotExist", "error_message": str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                data={"error": "InternalServerError", "error_message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    return wrapper
