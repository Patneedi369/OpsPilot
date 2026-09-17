import logging
from typing import Callable

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession 

from app.persistence.session import get_db
from app.services.audit_service import log_audit
from app.services.auth_service import decode_token

logger = logging.getLogger("opspilot.dependencies.auth")


class AuthenticatedUser:
    def __init__(self, id: str, username: str, role: str, email: str = ""):
        self.id = id
        self.username = username
        self.role = role
        self.email = email


async def get_current_user(
    request: Request,
    authorization: str | None = Header(None),
    x_user_role: str | None = Header(None),
    x_user_id: str | None = Header(None),
    x_user_name: str | None = Header(None),
    session: AsyncSession = Depends(get_db),
) -> AuthenticatedUser:
    # 1. Check Bearer token
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "").strip()
        payload = decode_token(token)
        if payload:
            return AuthenticatedUser(
                id=payload.get("sub", "usr-sre-001"),
                username=payload.get("username", "sre_user"),
                role=payload.get("role", "SRE"),
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication token.",
            )

    # 2. Check X-User-Role test header fallback
    if x_user_role:
        role = x_user_role.strip()
        user_id = x_user_id or f"usr-{role.lower()}-001"
        username = x_user_name or f"{role.lower()}_user"
        return AuthenticatedUser(id=user_id, username=username, role=role)

    # 3. Default fallback for backwards compatibility with Phases 1-11
    return AuthenticatedUser(id="usr-sre-001", username="sre_user", role="SRE")


def require_role(allowed_roles: list[str]) -> Callable:
    async def dependency(
        user: AuthenticatedUser = Depends(get_current_user),
        session: AsyncSession = Depends(get_db),
    ) -> AuthenticatedUser:
        if user.role not in allowed_roles:
            logger.warning(
                "RBAC permission denied",
                extra={"user": user.username, "role": user.role, "allowed_roles": allowed_roles},
            )
            # Log audit record for permission failure
            await log_audit(
                session=session,
                user_id=user.id,
                username=user.username,
                user_role=user.role,
                action="rbac.permission_denied",
                resource_type="endpoint",
                resource_id="rbac_check",
                outcome="failure",
                metadata={"allowed_roles": allowed_roles, "denied_role": user.role},
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: role '{user.role}' is not authorized. Requires one of {allowed_roles}.",
            )
        return user

    return dependency
