import base64
import hashlib
import hmac
import json
import logging
import secrets
import time
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.user import User

logger = logging.getLogger("opspilot.services.auth")
settings = get_settings()

SECRET_KEY = getattr(settings, "secret_key", "opspilot-secret-jwt-key-2026-sre-platform")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    return f"{salt}${key.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    try:
        salt, key_hex = hashed.split("$")
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
        return hmac.compare_digest(key.hex(), key_hex)
    except Exception:
        return False


def create_token(user_id: str, username: str, role: str, expires_in_seconds: int = 86400) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": user_id,
        "username": username,
        "role": role,
        "exp": int(time.time()) + expires_in_seconds,
        "iat": int(time.time()),
    }
    
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode("utf-8")).rstrip(b"=").decode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8")).rstrip(b"=").decode("utf-8")
    
    signature_base = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(SECRET_KEY.encode("utf-8"), signature_base, hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).rstrip(b"=").decode("utf-8")
    
    return f"{header_b64}.{payload_b64}.{sig_b64}"


def decode_token(token: str) -> dict[str, Any] | None:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, sig_b64 = parts
        
        signature_base = f"{header_b64}.{payload_b64}".encode("utf-8")
        expected_sig = hmac.new(SECRET_KEY.encode("utf-8"), signature_base, hashlib.sha256).digest()
        
        # Pad base64 signature
        padding = "=" * (4 - len(sig_b64) % 4)
        actual_sig = base64.urlsafe_b64decode(sig_b64 + padding)
        
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
        
        payload_padding = "=" * (4 - len(payload_b64) % 4)
        payload_json = base64.urlsafe_b64decode(payload_b64 + payload_padding).decode("utf-8")
        payload = json.loads(payload_json)
        
        if payload.get("exp", 0) < int(time.time()):
            return None
            
        return payload
    except Exception:
        return None


async def authenticate_user(session: AsyncSession, username: str, password: str) -> User | None:
    # Ensure default users exist
    await seed_default_users(session)
    
    stmt = select(User).where(User.username == username)
    res = await session.execute(stmt)
    user = res.scalars().first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def seed_default_users(session: AsyncSession) -> None:
    defaults = [
        {"id": "usr-sre-001", "username": "sre_user", "email": "sre@opspilot.internal", "password": "sre_password", "role": "SRE"},
        {"id": "usr-lead-001", "username": "lead_user", "email": "lead@opspilot.internal", "password": "lead_password", "role": "Lead"},
        {"id": "usr-viewer-001", "username": "viewer_user", "email": "viewer@opspilot.internal", "password": "viewer_password", "role": "Viewer"},
    ]
    
    for item in defaults:
        res = await session.execute(select(User).where(User.username == item["username"]))
        existing = res.scalars().first()
        if not existing:
            u = User(
                id=item["id"],
                username=item["username"],
                email=item["email"],
                hashed_password=hash_password(item["password"]),
                role=item["role"],
                is_active=True,
                created_at=utcnow(),
            )
            session.add(u)
    await session.commit()
