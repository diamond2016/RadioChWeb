# python
import importlib

from api.services.radio_source_api_service import RadioSourceAPIService


def test_get_stream_type_repo_returns_repository_with_db_session(monkeypatch):
    # Arrange: sentinel session and fake repository class
    sentinel_session = object()

    # Patch the get_db_session used in the radio_source_api_service module
    monkeypatch.setattr(
        "api.services.radio_source_api_service.get_db_session",
        lambda: sentinel_session,
    )

    # Create a fake StreamTypeRepository that captures the session passed in
    class FakeRepo:
        def __init__(self, session):
            self.session = session

    # Patch the module that the method imports from
    mod = importlib.import_module("model.repository.stream_type_repository")
    monkeypatch.setattr(mod, "StreamTypeRepository", FakeRepo)

    # Act
    svc = RadioSourceAPIService()
    repo = svc.get_stream_type_repo()

    # Assert
    assert isinstance(repo, FakeRepo)
    assert repo.session is sentinel_session


def test_get_stream_type_repo_returns_new_instance_each_call(monkeypatch):
    sentinel_session = object()
    monkeypatch.setattr(
        "api.services.radio_source_api_service.get_db_session",
        lambda: sentinel_session,
    )

    class FakeRepo:
        def __init__(self, session):
            self.session = session

    mod = importlib.import_module("model.repository.stream_type_repository")
    monkeypatch.setattr(mod, "StreamTypeRepository", FakeRepo)

    svc = RadioSourceAPIService()
    repo1 = svc.get_stream_type_repo()
    repo2 = svc.get_stream_type_repo()

    assert repo1 is not repo2
    assert repo1.session is sentinel_session
    assert repo2.session is sentinel_session