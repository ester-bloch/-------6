from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class AppError(Exception):
    code: str
    message: str
    details: Optional[dict[str, Any]] = None
    cause: Optional[BaseException] = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.details:
            payload["details"] = self.details
        return payload


class ProviderError(AppError):
    pass


class ValidationError(AppError):
    pass


class RateLimitError(AppError):
    pass
