from typing import List


class ServiceParameterError(BaseException):
    """Argument validation exception thrown by the service

    Args:
        parameter: a list of 2-tuples (param_name, error_msg).

    """

    def __init__(self, parameters: List):
        err_msg = ';'.join([(f"param {p[0]}: {p[1]}") for p in parameters])
        message = f"Parameter validation error: {err_msg}"
        super().__init__(message)


class ServiceInternalError(BaseException):
    """Unexpected service exception
    """

    def __init__(self, message: str):
        super().__init__(f"Service Internal Error: {message}")
