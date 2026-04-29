"""
Pytest script to test the core functions in routers/projects.py directly.
Mocks dependencies like get_db and get_current_user.
"""
import pytest
from unittest.mock import MagicMock
from app.routers import projects
from app.models import Project, Vendor, DraftProjectPage, User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from fastapi import HTTPException

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

@pytest.fixture
def test_user(db_session):
    user = User(
        username="testuser",
        email="test@example.com",
        phone="1234567890",
        hash_password="pw",
        first_name="Test",
        last_name="User",
        stripe_customer_id="cus_test",
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def test_vendor(db_session, test_user):
    vendor = Vendor(
        business_name="TestVendor",
        email="vendor@example.com",
        owner=test_user.id,
        phone="1234567890",
        stripe_connect_id="scid",
        payouts_enabled=True,
        requirements_due_for_payment=""
    )
    db_session.add(vendor)
    db_session.commit()
    return vendor

def mock_get_db(db):
    def _get_db():
        yield db
    return _get_db

def mock_get_current_user(user):
    def _get_user():
        return user
    return _get_user


@pytest.mark.asyncio
async def test_create_and_get_project(db_session, test_user, test_vendor, monkeypatch):
    # Patch dependencies
    monkeypatch.setattr(projects, "get_db", mock_get_db(db_session))
    monkeypatch.setattr(projects, "get_current_user", mock_get_current_user(test_user))

    # Create project
    project_in = projects.ProjectIn(name="My Project")
    result = await projects.create_project(project_in, db=db_session, user=test_user)
    assert result["name"] == "My Project"

    # Get projects
    projects_list = await projects.get_projects(db=db_session, user=test_user)
    assert any(p["name"] == "My Project" for p in projects_list)


@pytest.mark.asyncio
async def test_delete_project(db_session, test_user, test_vendor, monkeypatch):
    monkeypatch.setattr(projects, "get_db", mock_get_db(db_session))
    monkeypatch.setattr(projects, "get_current_user", mock_get_current_user(test_user))

    # Create project
    project = Project(name="ToDelete", vendor=test_vendor.id, is_live=False)
    db_session.add(project)
    db_session.commit()
    pid = project.id

    # Add a draft page
    draft = DraftProjectPage(project=pid, name="Home", layout=[])
    db_session.add(draft)
    db_session.commit()

    # Delete project
    result = await projects.delete_project(pid, db=db_session, user=test_user)
    assert result["status"] == "deleted"
    assert db_session.get(Project, pid) is None
