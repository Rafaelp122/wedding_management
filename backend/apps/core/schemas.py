from ninja import Schema


class ErrorResponse(Schema):
    detail: str
    code: str | None = None
