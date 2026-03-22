"""Authentication and authorization helpers."""

from __future__ import annotations

from app.models.errors import DigenError


class AuthService:
    """Handles authenticated provider context.

    Real deployments should bind user-specific credentials or session references here.
    Never return raw tokens or cookies from this service.
    """

    def require_token(self, token: str | None) -> str:
        if not token:
            raise DigenError('AUTH_REQUIRED', 'Authenticated provider access is required.', False)
        return token
