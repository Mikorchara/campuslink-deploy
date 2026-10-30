from concurrent.futures import ThreadPoolExecutor
import os
import threading

import pytest
from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import Session

from src.database.base import Base
from src.models.user import User
from tests.conftest import register_and_login
from tests.test_products import create_product


def other_user(client, name='buyer'):
    return {'Authorization': 'Bearer ' + register_and_login(client, name, name + '@example.com')}


def post(client, owner):
    response = client.post('/api/forum/posts', headers=owner, json={'title': '校园经验', 'content': '一起交流', 'category': '学习'})
    assert response.status_code == 201
    return response.json()['data']


def inbox(client, headers, params=''):
    response = client.get('/api/notifications' + params, headers=headers)
    assert response.status_code == 200
    return response.json()['data']


@pytest.mark.parametrize('kind', ['product', 'post'])
def test_likes_are_persistent_idempotent_and_distinct_from_favorites(client, auth_header, kind):
    buyer = other_user(client)
    item = create_product(client, auth_header) if kind == 'product' else post(client, auth_header)
    base = f"/api/products/{item['id']}" if kind == 'product' else f"/api/forum/posts/{item['id']}"
    endpoint = base + '/like'
    assert client.get(endpoint).json()['data'] == {'count': 0, 'liked': False}
    assert client.put(endpoint).status_code == 401
    for _ in range(2):
        assert client.put(endpoint, headers=buyer).json()['data'] == {'count': 1, 'liked': True}
    assert client.get(endpoint).json()['data'] == {'count': 1, 'liked': False}
    assert client.get(endpoint, headers=buyer).json()['data']['liked'] is True
    assert client.get('/api/favorites', headers=buyer).json()['data'] == []
    assert inbox(client, auth_header)['unread_count'] == 1
    assert inbox(client, buyer)['total'] == 0
    for _ in range(2):
        assert client.delete(endpoint, headers=buyer).json()['data'] == {'count': 0, 'liked': False}
    client.put(endpoint, headers=buyer)
    assert inbox(client, auth_header)['total'] == 1  # unlike/re-like does not spam author
    client.put(endpoint, headers=auth_header)
    assert client.get(endpoint).json()['data']['count'] == 2
    assert inbox(client, auth_header)['total'] == 1  # no self-notification
    assert client.delete(base, headers=auth_header).status_code == 200
    assert client.get(endpoint).status_code == 404
    assert inbox(client, auth_header)['items'][0]['link'] is None


def test_comment_notification_ownership_read_state_and_new_messages(client, auth_header):
    buyer = other_user(client)
    stranger = other_user(client, 'stranger')
    item = post(client, auth_header)
    endpoint = f"/api/forum/posts/{item['id']}/comments"
    first = client.post(endpoint, headers=buyer, json={'content': 'private comment text'})
    assert first.status_code == 201
    data = inbox(client, auth_header)
    message = data['items'][0]
    assert message['kind'] == 'post_comment' and message['link'] == f"/forum/{item['id']}"
    assert 'private comment text' not in message['message']
    assert client.get('/api/notifications').status_code == 401
    assert inbox(client, stranger)['total'] == 0
    assert client.patch(f"/api/notifications/{message['id']}/read", headers=stranger).status_code == 404
    client.post(endpoint, headers=buyer, json={'content': 'new comment'})
    # A message arriving after the user loaded the list must stay unread.
    client.patch('/api/notifications/read-all', headers=auth_header, json={'up_to_id': message['id']})
    unread = inbox(client, auth_header, '?unread_only=true')
    assert unread['total'] == unread['unread_count'] == 1
    second = unread['items'][0]
    assert client.get('/api/notifications/unread-count', headers=auth_header).json()['data']['count'] == 1
    for _ in range(2):
        assert client.patch(f"/api/notifications/{second['id']}/read", headers=auth_header).status_code == 200
    assert inbox(client, auth_header)['unread_count'] == 0
    client.post(endpoint, headers=auth_header, json={'content': 'author response'})
    assert inbox(client, auth_header)['total'] == 2
    client.delete(f"/api/forum/comments/{first.json()['data']['id']}", headers=buyer)
    assert inbox(client, auth_header)['total'] == 2


@pytest.mark.parametrize('status', ['ACCEPTED', 'REJECTED', 'CANCELLED', 'COMPLETED'])
def test_trade_notifications_go_to_other_party_and_failed_updates_do_not_notify(client, auth_header, status):
    buyer = other_user(client)
    item = create_product(client, auth_header)
    endpoint = f"/api/products/{item['id']}/transactions"
    transaction = client.post(endpoint, headers=buyer, json={'note': 'private contact note'}).json()['data']
    assert client.post(endpoint, headers=buyer, json={}).status_code == 409
    messages = inbox(client, auth_header)
    assert messages['total'] == 1 and messages['items'][0]['kind'] == 'booking'
    assert 'private contact' not in messages['items'][0]['message']
    path = f"/api/transactions/{transaction['id']}"
    assert client.patch(path, headers=buyer, json={'status': 'ACCEPTED'}).status_code == 403
    assert inbox(client, buyer)['total'] == 0
    if status == 'COMPLETED':
        assert client.patch(path, headers=auth_header, json={'status': 'ACCEPTED'}).status_code == 200
    actor = buyer if status == 'CANCELLED' else auth_header
    assert client.patch(path, headers=actor, json={'status': status}).status_code == 200
    recipient = auth_header if status == 'CANCELLED' else buyer
    data = inbox(client, recipient)
    assert data['items'][0]['kind'] == 'transaction_status'
    assert data['items'][0]['link'] == f"/transactions?transaction={transaction['id']}"
    before = data['total']
    assert client.patch(path, headers=actor, json={'status': status}).status_code == 409
    assert inbox(client, recipient)['total'] == before


def test_failed_reservation_accept_does_not_commit_notification(client, auth_header):
    buyer = other_user(client)
    second = other_user(client, 'second')
    product = create_product(client, auth_header)
    endpoint = f"/api/products/{product['id']}/transactions"
    a = client.post(endpoint, headers=buyer, json={}).json()['data']['id']
    b = client.post(endpoint, headers=second, json={}).json()['data']['id']
    assert client.patch(f'/api/transactions/{a}', headers=auth_header, json={'status': 'ACCEPTED'}).status_code == 200
    assert client.patch(f'/api/transactions/{b}', headers=auth_header, json={'status': 'ACCEPTED'}).status_code == 409
    assert inbox(client, second)['total'] == 0


def test_additive_upgrade_preserves_existing_user_and_is_repeatable(tmp_path):
    engine = create_engine('sqlite:///' + str(tmp_path / 'old.db'))
    added = {'product_likes', 'post_likes', 'notifications'}
    Base.metadata.create_all(engine, tables=[table for table in Base.metadata.sorted_tables if table.name not in added])
    with Session(engine) as db:
        db.add(User(username='existing', email='existing@example.com', password_hash='original-hash'))
        db.commit()
    assert not added.intersection(inspect(engine).get_table_names())
    Base.metadata.create_all(engine)
    Base.metadata.create_all(engine)
    assert added.issubset(inspect(engine).get_table_names())
    with Session(engine) as db:
        existing = db.scalar(select(User))
        assert existing.username == 'existing' and existing.password_hash == 'original-hash'
    engine.dispose()


@pytest.mark.skipif(not os.environ.get('CAMPUSLINK_TEST_DATABASE_URL'), reason='PostgreSQL concurrency check')
def test_concurrent_likes_have_one_row_and_one_notification(client, auth_header):
    buyer = other_user(client)
    item = create_product(client, auth_header)
    barrier = threading.Barrier(2)
    def like(_):
        barrier.wait(timeout=5)
        return client.put(f"/api/products/{item['id']}/like", headers=buyer).status_code
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert list(pool.map(like, range(2))) == [200, 200]
    assert client.get(f"/api/products/{item['id']}/like").json()['data']['count'] == 1
    assert inbox(client, auth_header)['total'] == 1
