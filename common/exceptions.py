import functools

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.response import Response

import jwt


def exception_handler(cls):
    """
    Django에서 발생하는 에러들을 한 번에 처리하기 위한 클래스 데코레이터.
    """

    class WrappedClass(cls):
        def __getattribute__(self, item):
            try:
                attr = super().__getattribute__(item)
                if callable(attr):  # 함수(메서드)인 경우 예외 핸들러 적용
                    return functools.partial(self.wrap_method, attr)
                return attr  # 속성인 경우 그대로 반환
            except Exception as e:
                print(f"[Exception in accessing attribute '{item}']: {e}")
                raise

        @staticmethod
        def wrap_method(func, *args, **kwargs):
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
            except ValueError as e:
                return Response(
                    data={"error": "ValueError", "error_message": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
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

    return WrappedClass
