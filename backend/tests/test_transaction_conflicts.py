from tests.conftest import register_and_login
from tests.test_products import create_product
from concurrent.futures import ThreadPoolExecutor
import os
import threading
import pytest


def two_requests(client, auth_header):
    product = create_product(client, auth_header)
    requests = []
    for index in range(2):
        token = register_and_login(client, f"buyer{index}", f"buyer{index}@example.com")
        header = {"Authorization": f"Bearer {token}"}
        item = client.post(f"/api/products/{product['id']}/transactions", headers=header, json={})
        assert item.status_code == 201
        requests.append((item.json()["data"]["id"], header))
    return product, requests


def test_cannot_accept_two_buyers_for_one_product(client, auth_header):
    product, requests = two_requests(client, auth_header)
    first = client.patch(f"/api/transactions/{requests[0][0]}", headers=auth_header, json={"status": "ACCEPTED"})
    assert first.status_code == 200
    other = client.patch(f"/api/transactions/{requests[1][0]}", headers=auth_header, json={"status": "ACCEPTED"})
    assert other.status_code == 409
    assert client.get(f"/api/products/{product['id']}").json()["data"]["status"] == "RESERVED"
    assert client.patch(f"/api/products/{product['id']}/status", headers=auth_header,
                        json={"status": "AVAILABLE"}).status_code == 409
    assert client.put(f"/api/products/{product['id']}", headers=auth_header,
                      json={"status": "SOLD"}).status_code == 409


def test_cancelling_pending_request_does_not_reopen_another_buyers_reservation(client, auth_header):
    product, requests = two_requests(client, auth_header)
    assert client.patch(f"/api/transactions/{requests[0][0]}", headers=auth_header, json={"status": "ACCEPTED"}).status_code == 200
    assert client.patch(f"/api/transactions/{requests[1][0]}", headers=requests[1][1], json={"status": "CANCELLED"}).status_code == 200
    assert client.get(f"/api/products/{product['id']}").json()["data"]["status"] == "RESERVED"
    completed = client.patch(f"/api/transactions/{requests[0][0]}", headers=auth_header, json={"status": "COMPLETED"})
    assert completed.status_code == 200
    assert client.get(f"/api/products/{product['id']}").json()["data"]["status"] == "SOLD"
    assert client.patch(f"/api/transactions/{requests[0][0]}", headers=auth_header, json={"status": "CANCELLED"}).status_code == 409


@pytest.mark.skipif(not os.environ.get('CAMPUSLINK_TEST_DATABASE_URL'), reason='PostgreSQL concurrency check')
def test_concurrent_accepts_reserve_for_exactly_one_buyer(client, auth_header):
    product, requests = two_requests(client, auth_header)
    barrier = threading.Barrier(2)

    def accept(request):
        barrier.wait(timeout=5)
        return client.patch(f"/api/transactions/{request[0]}", headers=auth_header,
                            json={"status": "ACCEPTED"}).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(accept, requests))
    assert sorted(results) == [200, 409]
    transactions = client.get('/api/transactions', headers=auth_header).json()['data']
    assert sum(item['status'] == 'ACCEPTED' for item in transactions) == 1
    assert client.get(f"/api/products/{product['id']}").json()['data']['status'] == 'RESERVED'
