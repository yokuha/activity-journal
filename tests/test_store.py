from iicu_activity_journal import store


def test_json_roundtrip_and_reproducible(tmp_path):
    path = tmp_path / 'sub' / 'a.json.gz'
    assert store.write_json_gz(path, {'b': 1, 'a': 'ä'}) is True
    first = path.read_bytes()
    assert store.read_json_gz(path) == {'a': 'ä', 'b': 1}
    assert store.write_json_gz(path, {'a': 'ä', 'b': 1}) is False
    assert path.read_bytes() == first


def test_logbook_section_created_and_extended(tmp_path):
    readme = tmp_path / 'README.md'
    readme.write_text('# title\n')
    store.append_logbook(readme, 'one')
    store.append_logbook(readme, 'two')
    text = readme.read_text()
    assert text.count('# logbook') == 1
    assert text.index('one') < text.index('two')
