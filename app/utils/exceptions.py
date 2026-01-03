class PexaException(Exception):

    def __init__(self, message: str) -> None:
        self.message: str = message
        super().__init__(self.message)


class EntityNotFoundException(PexaException):
    """Exception to raise instead of HTTPException 404"""

    pass


class OperationNotPermitedException(PexaException):
    """Exception to raise instead of HTTPException 403"""
    pass


class BadRequestException(PexaException):
    """Exception to raise instead of HTTPException 400"""

    pass

class AuthenticationMissingException(PexaException):
    """Exception to raise instead of HTTPException 401"""

    pass
