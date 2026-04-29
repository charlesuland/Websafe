import pytest
from datetime import timedelta
from types import SimpleNamespace
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.auth import refresh_tokens, create_jwt_token, utcnow_naive
from app.database import Base
from app.dependencies import REFRESH_TOKEN_EXPIRES_DAYS, REFRESH_COOKIE_NAME, CSRF_COOKIE_NAME


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def make_request(refresh_token: str, csrf_token: str):
    return SimpleNamespace(
        method="POST",
        cookies={
            REFRESH_COOKIE_NAME: refresh_token,
            CSRF_COOKIE_NAME: csrf_token,
        },
        headers={
            "X-CSRF-Token": csrf_token,
            "user-agent": "pytest",
        },
        client=SimpleNamespace(host="127.0.0.1"),
    )


class ResponseStub:
    def __init__(self):
        self.cookies = {}

    def set_cookie(self, key, value, **kwargs):
        self.cookies[key] = {"value": value, **kwargs}

    def delete_cookie(self, key, **kwargs):
        self.cookies.pop(key, None)


@pytest.mark.asyncio
async def test_refresh_tokens_accepts_sqlite_naive_datetime_sessions(db_session):
    user = models.User(
        username="refreshuser",
        email="refresh@example.com",
        phone="1234567890",
        hash_password="pw",
        first_name="Refresh",
        last_name="User",
        stripe_customer_id="cus_refresh",
    )
    db_session.add(user)
    db_session.commit()

    jti = "refresh-jti"
    refresh_token = create_jwt_token(
        user_id=user.id,
        token_type="refresh",
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRES_DAYS),
        jti=jti,
    )
    csrf_token = "csrf-token"

    db_session.add(
        models.RefreshSession(
            user_id=user.id,
            jti=jti,
            expires_at=utcnow_naive() + timedelta(days=REFRESH_TOKEN_EXPIRES_DAYS),
            user_agent="pytest",
            ip_address="127.0.0.1",
        )
    )
    db_session.commit()

    request = make_request(refresh_token, csrf_token)
    response = ResponseStub()

    result = await refresh_tokens(request=request, response=response, db=db_session)

    assert result["status"] == "refreshed"
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies
    assert "csrf_token" in response.cookies
