from service.auth_service import AuthService


def test_hash_and_verify_roundtrip():
    svc = AuthService()
    plain = 'Secur3P@ss!'
    hashed = svc.hash_password(plain)
    assert isinstance(hashed, str) and len(hashed) > 0
    verified, new_hash = svc.verify_password(plain, hashed)
    assert verified is True
    # new_hash may be None depending on passlib behavior
    assert (new_hash is None) or isinstance(new_hash, str)
