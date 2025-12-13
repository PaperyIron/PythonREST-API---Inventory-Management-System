import pytest
from unittest.mock import patch, MagicMock
from io import StringIO
from cli import (
    print_all_items,
    error_response,
    get_inventory,
    get_item_by_id,
    add_new_item,
    update_item,
    delete_item,
    search_openfoodfacts
)


def test_print_all_items():
    """Test printing inventory items"""
    items = [
        {"id": 1, "product_name": "Product 1", "brands": "Brand A", "quantity": 10, "price": 5.99}
    ]
    with patch('sys.stdout', new=StringIO()) as fake_out:
        print_all_items(items)
        output = fake_out.getvalue()
        assert 'Product 1' in output


def test_error_response():
    """Test error handling"""
    mock_response = MagicMock()
    mock_response.status_code = 404
    with patch('sys.stdout', new=StringIO()) as fake_out:
        error_response(mock_response)
        output = fake_out.getvalue()
        assert '404' in output


@patch('cli.requests.get')
@patch('cli.print_all_items')
def test_get_inventory(mock_print, mock_get):
    """Test getting all inventory"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"id": 1, "product_name": "Test"}]
    mock_get.return_value = mock_response
    
    get_inventory()
    mock_print.assert_called_once()


@patch('cli.requests.get')
@patch('builtins.input', return_value='1')
def test_get_item_by_id(mock_input, mock_get):
    """Test getting item by ID"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 1, "product_name": "Test"}
    mock_get.return_value = mock_response
    
    with patch('sys.stdout', new=StringIO()):
        get_item_by_id()
    
    mock_get.assert_called_once_with('http://localhost:8000/inventory/1')


@patch('cli.requests.post')
@patch('builtins.input')
def test_add_new_item(mock_input, mock_post):
    """Test adding a new item"""
    mock_input.side_effect = ['Product', 'Brand', '123', '10', '9.99', 'Food']
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_post.return_value = mock_response
    
    with patch('sys.stdout', new=StringIO()):
        add_new_item()
    
    mock_post.assert_called_once()


@patch('cli.requests.get')
@patch('cli.requests.patch')
@patch('builtins.input')
def test_update_item(mock_input, mock_patch, mock_get):
    """Test updating an item"""
    mock_input.side_effect = ['1', 'New Name', '', '20', '', '']
    
    mock_get_response = MagicMock()
    mock_get_response.status_code = 200
    mock_get_response.json.return_value = {"id": 1, "product_name": "Old"}
    mock_get.return_value = mock_get_response
    
    mock_patch_response = MagicMock()
    mock_patch_response.status_code = 200
    mock_patch_response.json.return_value = {"id": 1}
    mock_patch.return_value = mock_patch_response
    
    with patch('sys.stdout', new=StringIO()):
        update_item()
    
    mock_patch.assert_called_once()


@patch('cli.requests.delete')
@patch('builtins.input', return_value='1')
def test_delete_item(mock_input, mock_delete):
    """Test deleting an item"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_delete.return_value = mock_response
    
    with patch('sys.stdout', new=StringIO()):
        delete_item()
    
    mock_delete.assert_called_once_with('http://localhost:8000/inventory/1')


@patch('cli.requests.get')
@patch('cli.requests.post')
@patch('builtins.input')
def test_search_openfoodfacts(mock_input, mock_post, mock_get):
    """Test searching OpenFoodFacts"""
    mock_input.side_effect = ['123456789', 'y', '10', '5.99']
    
    mock_off_response = MagicMock()
    mock_off_response.status_code = 200
    mock_off_response.json.return_value = {
        'product_name': 'Test Product',
        'brands': 'Test Brand'
    }
    mock_get.return_value = mock_off_response
    
    mock_post_response = MagicMock()
    mock_post_response.status_code = 200
    mock_post.return_value = mock_post_response
    
    with patch('sys.stdout', new=StringIO()):
        search_openfoodfacts()
    
    assert mock_get.call_count == 1