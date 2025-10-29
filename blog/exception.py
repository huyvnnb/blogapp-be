class ApiError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ResourceExist(ApiError):
    def __init__(self, message, status_code=409):
        super().__init__(message, status_code)


class NotFound(ApiError):
    def __init__(self, message, status_code=404):
        super().__init__(message, status_code)


class BadRequest(ApiError):
    def __init__(self, message: str = "Bad request."):
        super().__init__(message, status_code=400)


class Unauthorized(ApiError):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=401)


class Forbidden(ApiError):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, status_code=403)


class ServerError(ApiError):
    def __init__(self, message: str = "Server error"):
        super().__init__(message, status_code=500)

