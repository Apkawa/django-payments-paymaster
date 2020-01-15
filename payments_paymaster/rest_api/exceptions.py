from ..constants import ERROR_CODES


class BaseApiError(Exception):
    message = 'Неизвестная ошибка. Сбой в системе PayMaster. Если ошибка повторяется, обратитесь в техподдержку.'
    code = None

    def __init__(self, code=None, message=None):
        self.code = code or self.code
        self.message = ERROR_CODES.get(self.code, self.message)

    def __str__(self):
        return "({self.code}) {self.message}".format(self=self)


class ApiError(BaseApiError):
    code = -1


class PaymasterNetworkError(ApiError):
    code = -2


class PaymasterPermissionError(ApiError):
    code = -6


class SignError(ApiError):
    code = -7


class PaymentNotFound(ApiError):
    code = -13


class DuplicateNonce(ApiError):
    code = -14


class IncorrectAmountValue(ApiError):
    code = -18


PAYMASTER_ERROR_CODES = {e.code: e for e in
                         [
                             ApiError,
                             PaymasterNetworkError,
                             PaymasterPermissionError,
                             SignError,
                             PaymentNotFound,
                             DuplicateNonce,
                             IncorrectAmountValue
                         ]
                         }
