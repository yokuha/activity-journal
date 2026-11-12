import pytest

from iicu_activity_journal import credentials as cr


@pytest.fixture(autouse=True)
def clean_env(monkeypatch, tmp_path):
    monkeypatch.delenv(cr.ENV_API_KEY, raising=False)
    monkeypatch.delenv(cr.ENV_ATHLETE_ID, raising=False)
    monkeypatch.setenv('IICU_AUTHINFO_FILE', str(tmp_path / 'missing.gpg'))


def test_environment_wins(monkeypatch, tmp_path):
    (tmp_path / '.env').write_text('INTERVALS_ICU_API_KEY=file\nINTERVALS_ICU_ATHLETE_ID=i9\n')
    monkeypatch.setenv(cr.ENV_API_KEY, 'env')
    creds = cr.load_credentials(env_dir=tmp_path)
    assert (creds.api_key, creds.athlete_id) == ('env', 'i9')


def test_env_file_parsing(tmp_path):
    env = tmp_path / 'my.env'
    env.write_text('# c\nexport INTERVALS_ICU_API_KEY="k y"\nINTERVALS_ICU_ATHLETE_ID=\'i1\'\n')
    creds = cr.load_credentials(env_file=env)
    assert (creds.api_key, creds.athlete_id) == ('k y', 'i1')


def test_missing_credentials_raise(tmp_path):
    with pytest.raises(cr.CredentialsError):
        cr.load_credentials(env_dir=tmp_path)


def test_missing_explicit_env_file_raises(tmp_path):
    with pytest.raises(cr.CredentialsError):
        cr.load_credentials(env_file=tmp_path / 'nope.env')


def test_authinfo_parsing():
    text = 'machine other login a password b\nmachine intervals.icu login i5 password sek # c\n'
    assert cr.parse_authinfo(text) == ('i5', 'sek')
    assert cr.parse_authinfo('machine other login a password b') is None


def test_repr_hides_key():
    assert 'secret' not in repr(cr.Credentials('i1', 'secret'))
