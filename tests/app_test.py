import pytest
import json
from unittest.mock import patch, MagicMock
from app import app, inventory


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def reset_inventory():
    """Reset inventory to initial state before each test"""
    inventory.clear()
    inventory.extend([
        {
            "id": 1,
            "product_name": "Organic Almond Milk",
            "brands": "Silk",
            "barcode": "025293600577",
            "quantity": 10,
            "price": 3.99,
            "category": "Beverages"
        },
        {
            "id": 2,
            "product_name": "Whole Grain Bread",
            "brands": "Bread",
            "barcode": "013093502006",
            "quantity": 5,
            "price": 5.49,
            "category": "Bakery"
        }
    ])


def test_home_endpoint(client):
    """Test the home endpoint returns API information"""
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data


def test_get_all_inventory(client):
    """Test retrieving all inventory items"""
    response = client.get('/inventory')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2


def test_get_inventory_item(client):
    """Test retrieving a specific item by ID"""
    response = client.get('/inventory/1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['product_name'] == 'Organic Almond Milk'


def test_add_inventory_item(client):
    """Test adding a new inventory item"""
    new_item = {
        "product_name": "Test Product",
        "quantity": 25,
        "price": 9.99
    }
    response = client.post(
        '/inventory',
        data=json.dumps(new_item),
        content_type='application/json'
    )
    assert response.status_code == 201


def test_update_inventory_item(client):
    """Test updating an existing inventory item"""
    update_data = {"quantity": 50, "price": 4.99}
    response = client.patch(
        '/inventory/1',
        data=json.dumps(update_data),
        content_type='application/json'
    )
    assert response.status_code == 200


def test_delete_inventory_item(client):
    """Test deleting an inventory item"""
    response = client.delete('/inventory/1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    
    # Verify the item was deleted by trying to get it
    response = client.get('/inventory/1')
    assert response.status_code == 404


@patch('app.requests.get')
def test_openfoodfacts_endpoint(mock_get, client):
    """Test OpenFoodFacts endpoint"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'status': 1,
        'product': {
            'product_name': 'Test Product',
            'brands': 'Test Brand',
            'categories': 'Test Category'
        }
    }
    mock_get.return_value = mock_response
    
    response = client.get('/openfoodfacts/123456789')
    assert response.status_code == 200