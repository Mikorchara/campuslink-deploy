import pytest

from tests.conftest import register_and_login


URL = '/api/forum/posts/participated'


def user(client, name):
    return {'Authorization': 'Bearer ' + register_and_login(client, name, name + '@example.com')}


def post(client, author, title):
    response = client.post('/api/forum/posts', headers=author,
        json={'title': title, 'content': '讨论正文', 'category': '学习'})
    assert response.status_code == 201
    return response.json()['data']['id']


def comment(client, author, post_id, content='参与讨论'):
    response = client.post(f'/api/forum/posts/{post_id}/comments', headers=author, json={'content': content})
    assert response.status_code == 201
    return response.json()['data']['id']


def listing(client, viewer, params=None):
    response = client.get(URL, headers=viewer, params=params)
    assert response.status_code == 200
    return response.json()['data']


def test_participation_requires_login_and_is_scoped_to_current_user(client, auth_header):
    assert client.get(URL).status_code == 401
    assert client.get(URL, headers={'Authorization': 'Bearer invalid'}).status_code == 401
    reader, other = user(client, 'reader'), user(client, 'other')
    a = post(client, auth_header, '作者发帖不自动算参与')
    assert listing(client, auth_header)['total'] == 0
    assert listing(client, reader)['items'] == []
    # Likes are independent of participation.
    client.put(f'/api/forum/posts/{a}/like', headers=reader)
    assert listing(client, reader)['total'] == 0
    comment(client, reader, a)
    assert listing(client, reader)['total'] == 1
    assert listing(client, other, {'user_id': 2, 'author_id': 2})['total'] == 0
    assert listing(client, auth_header)['total'] == 0
    comment(client, auth_header, a)
    assert listing(client, auth_header)['total'] == 1  # self-comments count too


def test_participation_deduplicates_and_sorts_by_personal_comment_not_post_or_others(client, auth_header):
    reader = user(client, 'reader')
    a = post(client, auth_header, '旧帖')
    b = post(client, auth_header, '新帖')
    c = post(client, auth_header, '未参与')
    comment(client, reader, a)
    comment(client, reader, b)
    last = comment(client, reader, a)
    comment(client, auth_header, b)  # another person's new reply must not reorder it
    result = listing(client, reader)
    assert [p['id'] for p in result['items']] == [a, b]
    assert result['total'] == 2 and c not in [p['id'] for p in result['items']]
    assert [p['comment_count'] for p in result['items']] == [2, 2]
    assert all(p['last_participated_at'] for p in result['items'])
    assert 'email' not in result['items'][0]['author']
    before = result['items'][0]['last_participated_at']
    assert client.put(f'/api/forum/comments/{last}', headers=reader, json={'content': '修改评论'}).status_code == 200
    assert listing(client, reader)['items'][0]['last_participated_at'] == before


def test_deleting_comments_recalculates_participation_and_deleted_posts_disappear(client, auth_header):
    reader = user(client, 'reader')
    a, b = post(client, auth_header, 'A'), post(client, auth_header, 'B')
    old = comment(client, reader, a)
    comment(client, reader, b)
    recent = comment(client, reader, a)
    assert [p['id'] for p in listing(client, reader)['items']] == [a, b]
    assert client.delete(f'/api/forum/comments/{recent}', headers=reader).status_code == 200
    assert [p['id'] for p in listing(client, reader)['items']] == [b, a]
    assert client.delete(f'/api/forum/comments/{old}', headers=reader).status_code == 200
    assert [p['id'] for p in listing(client, reader)['items']] == [b]
    assert client.delete(f'/api/forum/posts/{b}', headers=auth_header).status_code == 200
    assert listing(client, reader)['total'] == 0


def test_participation_paginates_unique_posts_and_handles_out_of_range(client, auth_header):
    reader = user(client, 'reader')
    ids=[]
    for i in range(5):
        pid=post(client, auth_header, f'帖子{i}')
        ids.append(pid)
        comment(client, reader, pid)
        comment(client, reader, pid)
    pages=[listing(client, reader, {'page': page, 'page_size': 2}) for page in [1,2,3]]
    assert all(data['total'] == 5 for data in pages)
    assert [p['id'] for data in pages for p in data['items']] == ids[::-1]
    assert listing(client, reader, {'page': 99})['items'] == []
    assert listing(client, reader, {'page_size': 100})['total'] == 5


@pytest.mark.parametrize('params', [{'page': 0}, {'page': -1}, {'page_size': 0}, {'page_size': 101}])
def test_participation_rejects_invalid_pagination(client, auth_header, params):
    assert client.get(URL, headers=auth_header, params=params).status_code == 422
