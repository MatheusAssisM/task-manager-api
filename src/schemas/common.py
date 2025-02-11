from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str


class MessageResponse(BaseModel):
    message: str


class ValidationErrorDetail(BaseModel):
    loc: list[str]
    msg: str
    type: str


class ValidationErrorResponse(BaseModel):
    error: str = "Validation error"
    details: list[ValidationErrorDetail]


class UnauthorizedResponse(BaseModel):
    error: str = "Unauthorized"


class NotFoundResponse(BaseModel):
    error: str = "Not found"


class ForbiddenResponse(BaseModel):
    error: str = "Forbidden"
