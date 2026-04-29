


"""
Pytest script for testing SQLAlchemy database functions and models.
Assumes a SQLite in-memory database for isolation.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, User, Project, Subscription, Plan, Vendor
from app.database import Base as AppBase
from app.database import engine as app_engine
from app import models
from datetime import datetime

@pytest.fixture(scope="function")
def db_session():
    # Use in-memory SQLite for tests
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_create_user(db_session):
    user = models.User(
        username="testuser",
        email="test@example.com",
        phone="1234567890",
        hash_password="hashedpw",
        first_name="Test",
        last_name="User",
        stripe_customer_id="cus_test",
    )
    db_session.add(user)
    db_session.commit()
    assert user.id is not None
    fetched = db_session.query(models.User).filter_by(username="testuser").first()
    assert fetched.email == "test@example.com"


def test_create_project(db_session):
    user = models.User(
        username="owner",
        email="owner@example.com",
        phone="1234567890",
        hash_password="pw",
        first_name="Owner",
        last_name="User",
        stripe_customer_id="cus_owner",
    )
    db_session.add(user)
    db_session.commit()
    project = models.Project(
        name="Test Project",
        vendor=None,
        is_live=False
    )
    db_session.add(project)
    db_session.commit()
    assert project.id is not None
    fetched = db_session.query(models.Project).filter_by(name="Test Project").first()
    assert fetched.is_live is False


def test_create_plan_and_subscription(db_session):
    plan = models.Plan(
        name="Basic",
        price_in_cents=1000,
        duration=models.Duration.MONTHLY,
        description="Basic plan",
        stripe_plan_id="plan_123",
        currency="USD"
    )
    db_session.add(plan)
    db_session.commit()
    user = models.User(
        username="subuser",
        email="sub@example.com",
        phone="1234567890",
        hash_password="pw",
        first_name="Sub",
        last_name="User",
        stripe_customer_id="cus_sub",
    )
    db_session.add(user)
    db_session.commit()
    sub = models.Subscription(
        plan_id=plan.id,
        status=models.SubscriptionStatus.ACTIVE,
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow(),
        canceled_at=datetime.utcnow(),
        trial_start=datetime.utcnow(),
        trial_end=datetime.utcnow(),
        meta={},
        user_id=user.id
    )
    db_session.add(sub)
    db_session.commit()
    assert sub.id is not None
    fetched = db_session.query(models.Subscription).filter_by(user_id=user.id).first()
    assert fetched.plan_id == plan.id
