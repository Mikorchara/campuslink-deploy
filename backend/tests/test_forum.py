import pytest
from sqlalchemy import create_engine

from tests.conftest import register_and_login
from src.models.user import User
from tools.db_admin import snapshot


PAYLOAD = {"title": "图书馆自习攻略", "content": "第一段经验\n\n第二段经验", "category": "学习"}


def test_forum_crud_permissions_and_comment_cascade(client, auth_header):
    post = client.post('/api/forum/posts', json=PAYLOAD, headers=auth_header)
    assert post.status_code == 201
    post = post.json()['data']
    url = f'/api/forum/posts/{post["id"]}'
    assert post['author']['name'] == 'seller'
    assert 'email' not in post['author'] and 'password_hash' not in post['author']
    other = {'Authorization': 'Bearer ' + register_and_login(client, 'reader', 'reader@example.com')}
    assert client.put(url, json=PAYLOAD, headers=other).status_code == 403
    assert client.delete(url, headers=other).status_code == 403
    assert client.get('/api/forum/posts/mine', headers=other).json()['data']['total'] == 0
    assert client.get('/api/forum/posts/mine', headers=auth_header).json()['data']['total'] == 1
    changed = dict(PAYLOAD, title='修改后的自习攻略')
    assert client.put(url, json=changed, headers=auth_header).json()['data']['title'] == changed['title']
    comment = client.post(url + '/comments', json={'content': '  实用经验  '}, headers=other)
    assert comment.status_code == 201
    comment = comment.json()['data']
    comment_url = f'/api/forum/comments/{comment["id"]}'
    assert comment['content'] == '实用经验'
    assert client.get(url).json()['data']['comment_count'] == 1
    assert client.get('/api/forum/posts').json()['data']['items'][0]['comment_count'] == 1
    assert client.delete(comment_url, headers=auth_header).status_code == 403
    assert client.put(comment_url, json={'content': '越权'}, headers=auth_header).status_code == 403
    assert client.put(comment_url, json={'content': '修订评论'}, headers=other).json()['data']['content'] == '修订评论'
    assert client.get(url + '/comments').json()['data']['items'][0]['content'] == '修订评论'
    assert client.delete(comment_url, headers=other).status_code == 200
    assert client.get(url).json()['data']['comment_count'] == 0
    second = client.post(url + '/comments', json={'content': '跟帖'}, headers=other).json()['data']
    assert client.delete(url, headers=auth_header).status_code == 200
    assert client.get(url).status_code == 404
    assert client.get(url + '/comments').status_code == 404
    assert client.post(url + '/comments', json={'content': '已删除'}, headers=other).status_code == 404
    assert client.delete(f'/api/forum/comments/{second["id"]}', headers=other).status_code == 404


def test_forum_pagination_filter_and_literal_search(client, auth_header):
    for i in range(5):
        payload = dict(PAYLOAD, title=f'攻略{i}', content=f'经验_{i}%', category='学习' if i % 2 == 0 else '生活')
        assert client.post('/api/forum/posts', json=payload, headers=auth_header).status_code == 201
    first = client.get('/api/forum/posts?page=1&page_size=2').json()['data']
    second = client.get('/api/forum/posts?page=2&page_size=2').json()['data']
    assert first['total'] == second['total'] == 5
    assert len(first['items']) == len(second['items']) == 2
    assert not ({p['id'] for p in first['items']} & {p['id'] for p in second['items']})
    assert client.get('/api/forum/posts?category=学习').json()['data']['total'] == 3
    assert client.get('/api/forum/posts', params={'keyword': '经验_2%'}).json()['data']['total'] == 1
    assert client.get('/api/forum/posts?keyword=没有此帖').json()['data']['items'] == []
    url = f'/api/forum/posts/{first["items"][0]["id"]}/comments'
    for i in range(3):
        client.post(url, json={'content': str(i)}, headers=auth_header)
    assert client.get(url + '?page_size=2').json()['data']['total'] == 3
    assert [c['content'] for c in client.get(url + '?page=2&page_size=2').json()['data']['items']] == ['2']


@pytest.mark.parametrize('patch', [
    {'title': '   '}, {'content': '\n  '}, {'category': '任意分类'}, {'title': 'a' * 121},
    {'content': 'x' * 10001}, {'author_id': 100}, {'image_url': 'javascript:alert(1)'},
    {'image_url': 'https://example.com/tracking.png'},
])
def test_forum_validates_writes(client, auth_header, patch):
    assert client.post('/api/forum/posts', json=PAYLOAD | patch, headers=auth_header).status_code == 422
    assert client.get('/api/forum/posts').json()['data']['total'] == 0


def test_forum_authentication_and_invalid_comments(client, auth_header):
    assert client.post('/api/forum/posts', json=PAYLOAD).status_code == 401
    assert client.get('/api/forum/posts/mine').status_code == 401
    post = client.post('/api/forum/posts', json=PAYLOAD, headers=auth_header).json()['data']
    url = f'/api/forum/posts/{post["id"]}'
    assert client.put(url, json=PAYLOAD).status_code == 401
    assert client.delete(url).status_code == 401
    assert client.post(url + '/comments', json={'content': '评论'}).status_code == 401
    for content in [' ', 'x' * 1001]:
        assert client.post(url + '/comments', json={'content': content}, headers=auth_header).status_code == 422
    assert client.get(url).json()['data']['comment_count'] == 0
    assert client.get('/api/forum/posts?page=0').status_code == 422
    assert client.get('/api/forum/posts?page_size=101').status_code == 422


def test_database_fingerprints_support_pre_forum_backups(tmp_path):
    target = create_engine(f'sqlite:///{tmp_path / "legacy.db"}')
    User.__table__.create(target)
    with target.connect() as connection:
        assert set(snapshot(connection)) == {'users'}
        expanded = snapshot(connection, missing_as_empty=True)
        assert expanded['forum_posts']['rows'] == expanded['forum_comments']['rows'] == 0
    target.dispose()


def test_migrate_legacy_sqlite_without_forum_tables(client, tmp_path, monkeypatch):
    from src.database.base import Base
    from src.database.session import get_db
    from src.main import app
    from tools import db_admin
    from sqlalchemy import select
    session = next(app.dependency_overrides[get_db]())
    target = session.get_bind()
    if target.dialect.name != 'postgresql':
        session.close()
        pytest.skip('PostgreSQL migration check')
    session.close()
    source = tmp_path / 'old.sqlite3'
    original = create_engine(f'sqlite:///{source}')
    Base.metadata.create_all(original, tables=[table for table in Base.metadata.sorted_tables if not table.name.startswith('forum_')])
    with original.begin() as connection:
        connection.execute(User.__table__.insert().values(id=1, username='legacy', email='legacy@example.com', password_hash='test-only-placeholder'))
    original.dispose()
    original_hash = db_admin.digest(source)
    monkeypatch.setattr(db_admin, 'engine', lambda: target)
    db_admin.sqlite_migrate(source, tmp_path / 'backups')
    assert db_admin.digest(source) == original_hash
    with target.connect() as connection:
        assert connection.scalar(select(User.username)) == 'legacy'
        data = snapshot(connection)
        assert data['forum_posts']['rows'] == data['forum_comments']['rows'] == 0
