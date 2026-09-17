from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.persistence.session import get_db
from app.dependencies.auth import AuthenticatedUser, get_current_user
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.services.audit_service import log_audit
from app.services.auth_service import authenticate_user, create_token

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_db),
) -> TokenResponse:
    user = await authenticate_user(session, payload.username, payload.password)
    if not user:
        await log_audit(
            session=session,
            user_id="anonymous",
            username=payload.username,
            user_role="Unknown",
            action="auth.login_failure",
            resource_type="user",
            resource_id=payload.username,
            outcome="failure",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    token = create_token(user.id, user.username, user.role)
    await log_audit(
        session=session,
        user_id=user.id,
        username=user.username,
        user_role=user.role,
        action="auth.login_success",
        resource_type="user",
        resource_id=user.id,
        outcome="success",
    )
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        username=user.username,
        role=user.role,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: AuthenticatedUser = Depends(get_current_user)) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        email=getattr(user, "email", f"{user.username}@opspilot.internal"),
        role=user.role,
        is_active=True,
        created_at=user.__dict__.get("created_at") or "2026-09-10T00:00:00Z",
    )
