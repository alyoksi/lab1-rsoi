from typing import Optional

from pydantic import BaseModel, ConfigDict


class PersonRequest(BaseModel):
    name: str
    age: Optional[int] = None
    address: Optional[str] = None
    work: Optional[str] = None


class PersonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    age: Optional[int] = None
    address: Optional[str] = None
    work: Optional[str] = None


class ErrorResponse(BaseModel):
    message: str


class ValidationErrorResponse(BaseModel):
    message: str
    errors: Optional[dict] = None
