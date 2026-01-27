import datetime
from unittest.mock import Mock

from flask_login import login_user
import pytest
from pytest import fixture
from model.dto.user import UserDTO
from model.entity.user import User
from model.repository.user_repository import UserRepository
from service.auth_service import AuthService
from tests.conftest import test_app
from tests.tests_service.test_proposal_service import mock_auth_service

@fixture
def mock_user_repo() -> UserRepository:
    """Create mock UserRepository."""
    return Mock(spec=UserRepository)

def test_hash_and_verify_roundtrip():
    svc = AuthService()
    plain = 'Secur3P@ss!'
    hashed = svc.hash_password(plain)
    assert isinstance(hashed, str) and len(hashed) > 0
    verified, new_hash = svc.verify_password(plain, hashed)
    assert verified is True
    # new_hash may be None depending on passlib behavior
    assert (new_hash is None) or isinstance(new_hash, str)

def test_verify_wrong_password():
    svc = AuthService()
    plain = 'Secur3P@ss!'
    wrong = 'WrongP@ss!'
    hashed = svc.hash_password(plain)
    verified, new_hash = svc.verify_password(wrong, hashed)
    assert verified is False
    assert new_hash is None

def test_register_user_dto_success(test_app):   
    svc = AuthService()
    plain = "Secur3P@ss!"
    mock_user_repo.find_by_email = Mock(return_value=None)
    mock_user_repo.find_by_id = Mock(return_value=None)
    user = User(
        id=0,
        email="test@example.com",
        hash_password="hashed",
        role="user"
    )   
    user_dto: UserDTO = UserDTO.model_validate(user)
    # register_user interacts with the repository which uses the
    # Flask SQLAlchemy session — run it inside an app context provided
    # by the `test_app` fixture.
    with test_app.app_context():
        registered_dto: UserDTO = svc.register_user_dto(user_dto, plain)
    
    assert registered_dto is not None
    assert registered_dto.id > 0
    assert registered_dto.email == user_dto.email
    assert registered_dto.role == user_dto.role


def test_change_password_dto_success(test_app):
    svc = AuthService()
    old = "Secur3P@ss!"
    new = "N3wP@ssw0rd!"

    # Create and register a real user inside app context so repository
    # operations work against the test DB.
    user = User(id=0, email="change_password@example.com", hash_password="", role="user")
    user_dto: UserDTO = UserDTO.model_validate(user)

    with test_app.app_context():
        registered: UserDTO = svc.register_user_dto(user_dto, old)

        # Change the password and verify it was updated
        changed: UserDTO = svc.change_password_dto(registered, new)
        assert changed is not None
        assert changed.id == registered.id
        assert changed.email == registered.email
        assert changed.role == registered.role

        verified, _ = svc.verify_password(new, svc.user_repo.find_by_id(changed.id).hash_password)
        assert verified is True
