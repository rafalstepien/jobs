class APIError(Exception):
    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


class RetryableAPIError(APIError): ...


class JobOfferStructureError(Exception): ...


class JustJoinITOfferStructureError(Exception): ...
