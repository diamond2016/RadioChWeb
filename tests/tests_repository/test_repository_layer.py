import pytest

from model.repository.user_repository import UserRepository
from model.repository.stream_type_repository import StreamTypeRepository
from model.repository.radio_source_repository import RadioSourceRepository
from model.repository.proposal_repository import ProposalRepository
from model.repository.stream_analysis_repository import StreamAnalysisRepository

from model.entity.radio_source import RadioSource
from model.entity.proposal import Proposal
from model.entity.stream_analysis import StreamAnalysis


def test_user_repository_crud(test_db):
    user_repo = UserRepository(test_db)

    user = user_repo.create('repo@example.com', 'hash123', role='user')
    assert user.id is not None

    fetched = user_repo.find_by_id(user.id)
    assert fetched is not None and fetched.email == 'repo@example.com'

    fetched_by_email = user_repo.find_by_email('repo@example.com')
    assert fetched_by_email.id == user.id

    # update password
    user_repo.update_password(user, 'newhash')
    assert user.hash_password == 'newhash'

    # change role
    user_repo.set_role(user, 'admin')
    assert user.role == 'admin'


def test_stream_type_repository_create_and_find(test_db):
    st_repo = StreamTypeRepository(test_db)

    st = st_repo.create_if_not_exists('HTTP', 'MP3', 'Icecast', 'HTTP MP3 Icecast')
    assert st.id is not None

    found_id = st_repo.find_by_combination('HTTP', 'MP3', 'Icecast')
    assert found_id == st.id

    key_map = st_repo.get_type_key_to_id_map()
    assert 'HTTP-MP3-Icecast' in key_map


def test_radio_source_repository_crud_and_eager(test_db):
    # prepare dependencies
    user_repo = UserRepository(test_db)
    st_repo = StreamTypeRepository(test_db)
    radio_repo = RadioSourceRepository(test_db)

    user = user_repo.create('radio@example.com', 'h', role='user')
    st = st_repo.create_if_not_exists('HTTP', 'MP3', 'Icecast', 'HTTP MP3 Icecast')

    radio = RadioSource(stream_url='http://radio.example/stream', name='RadioX', stream_type_id=st.id, is_secure=False, website_url='http://example.com', country='IT', description='desc', created_by=user.id)
    saved = radio_repo.save(radio)
    assert saved.id is not None

    fetched = radio_repo.find_by_id(saved.id)
    assert fetched is not None
    assert fetched.stream_url == saved.stream_url
    # eager-loaded relations
    assert fetched.stream_type is not None and fetched.stream_type.id == st.id
    assert fetched.user is not None and fetched.user.id == user.id


def test_proposal_repository_eager_load(test_db):
    user_repo = UserRepository(test_db)
    st_repo = StreamTypeRepository(test_db)
    prop_repo = ProposalRepository(test_db)

    user = user_repo.create('prop@example.com', 'h', role='user')
    st = st_repo.create_if_not_exists('HTTP', 'MP3', 'Icecast', 'HTTP MP3 Icecast')

    proposal = Proposal(stream_url='http://prop.example/stream', name='Prop1', stream_type_id=st.id, is_secure=False, created_by=user.id)
    saved = prop_repo.save(proposal)
    assert saved.id is not None

    fetched = prop_repo.find_by_id(saved.id)
    assert fetched is not None
    assert fetched.stream_type is not None and fetched.stream_type.id == st.id
    assert fetched.user is not None and fetched.user.id == user.id


def test_stream_analysis_repository_crud(test_db):
    user_repo = UserRepository(test_db)
    st_repo = StreamTypeRepository(test_db)
    analysis_repo = StreamAnalysisRepository(test_db)

    user = user_repo.create('analyst@example.com', 'h', role='user')
    st = st_repo.create_if_not_exists('HTTP', 'MP3', 'Icecast', 'HTTP MP3 Icecast')

    analysis = StreamAnalysis(stream_url='http://an.example/stream', stream_type_id=st.id, is_valid=True, is_secure=False, created_by=user.id)
    saved = analysis_repo.save(analysis)
    assert saved.id is not None

    fetched = analysis_repo.find_by_id(saved.id)
    assert fetched is not None
    assert fetched.stream_type is not None and fetched.stream_type.id == st.id
    assert fetched.user is not None and fetched.user.id == user.id

    by_user = analysis_repo.get_analyses_by_user(user.id)
    assert any(a.id == saved.id for a in by_user)
