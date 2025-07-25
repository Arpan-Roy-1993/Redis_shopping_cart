# tests/test_shoppingcart.py
import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shoppingcart import app, r

class TestConfig:
    TESTING = True
    DEBUG = False

@pytest.fixture
def client():
    app.config.from_object(TestConfig)
    with app.test_client() as client:
        with app.app_context():
            r.flushdb()  # Clear Redis before each test
            yield client

def test_home_redirect(client):
    response = client.get('/')
    assert response.status_code == 302
    assert '/cart/user123' in response.location

def test_add_item_to_cart(client):
    response = client.post('/cart/user123', data={'sku': 'item1', 'quantity': 2})
    assert response.status_code == 200
    cart = r.hgetall('cart:user123')
    assert b'item1' in cart
    assert int(cart[b'item1']) == 2

def test_remove_item_from_cart(client):
    r.hset('cart:user123', 'item2', 5)
    response = client.post('/cart/user123/remove', data={'sku_to_remove': 'item2', 'quantity_to_remove': 3})
    assert response.status_code == 302
    cart = r.hgetall('cart:user123')
    assert int(cart[b'item2']) == 2

def test_remove_item_completely(client):
    r.hset('cart:user123', 'item3', 1)
    response = client.post('/cart/user123/remove', data={'sku_to_remove': 'item3', 'quantity_to_remove': 1})
    assert response.status_code == 302
    cart = r.hgetall('cart:user123')
    assert b'item3' not in cart

def test_redis_connection():
    pong = r.ping()
    assert pong is True