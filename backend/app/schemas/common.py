from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field


PayloadT = TypeVar("PayloadT")


class ApiErrorDetail(BaseModel):
    code: str
    message: str
    details: dict[str, Any] | list[Any] | None = None


class ApiErrorResponse(BaseModel):
    success: bool = False
    message: str
    detail: str
    error: ApiErrorDetail


class ApiResponse(BaseModel, Generic[PayloadT]):
    success: bool = True
    message: str = "ok"
    data: PayloadT
    meta: dict[str, Any] | None = Field(default=None)


def build_api_response(
    data: PayloadT,
    *,
    message: str = "ok",
    meta: dict[str, Any] | None = None,
) -> ApiResponse[PayloadT]:
    return ApiResponse[PayloadT](message=message, data=data, meta=meta)
