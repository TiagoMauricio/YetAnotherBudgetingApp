class PexaException(Exception):

    def __init__(self, message: str) -> None:
        self.message: str = message
        super().__init__(self.message)


class EntityNotFoundException(PexaException):
    pass


class OperationNotPermitedException(PexaException):
    pass


class BadRequestException(PexaException):
    """Exception to raise instead of HTTPException 400"""

    pass
