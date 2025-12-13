import requests
import json
from typing import Optional

API_base_url = "http://localhost:8000"

def heading(text):
    print(text)
    print('=' * 70)

def print_single_item(item):
    print(f'\nID: {item["id"]}')
    print(f'Name: {item["product_name"]}')
    print(f'Brand: {item["brands"]}')
    print(f'Barcode: {item["barcode"]}')
    print(f'Quantity: {item["quantity"]}')
    print(f'Price: {item["price"]}')
    print(f'Cateogry: {item["category"]}')

def print_all_items(items):
    """Display all inventory items in a formatted table"""
    
    if not items:
        print('\n❌ No items found in inventory')
        return
    
    print(f"\n{'ID':<5} {'Name':<30} {'Brand':<20} {'Qty':<8} {'Price':<10}")
    print('-' * 80)
    
    for item in items:
        name = item['product_name'][:28] + '..' if len(item['product_name']) > 30 else item['product_name']
        brand = item['brands'][:18] + '..' if len(item['brands']) > 20 else item['brands']
        
        print(f"{item['id']:<5} {name:<30} {brand:<20} {item['quantity']:<8} ${item['price']:<9.2f}")
    
    print(f"Total items: {len(items)}")


def error_response(response):
    if response.status_code == 200:
        print('Item not found')
    elif response.status_code == 400:
        print('Bad Request')
    else:
        print(response.status_code)


def get_inventory():
    try:
        response = requests.get(f'{API_base_url}/inventory')

        if response.status_code == 200:
            items = response.json()
            heading('Inventory')
            print_all_items(items)
        else:
            error_response(response)
    except Exception as e:
        print(f'Error: {e}')

def get_item_by_id():
    try:
        item_id = input('Enter item ID: ').strip()

        if not item_id.isdigit():
            print('Please enter a valid number')
            return
        
        response = requests.get(f'{API_base_url}/inventory/{item_id}')

        if response.status_code == 200:
            item = response.json()
            print(item)
        else:
            error_response(response)
        
    except Exception as e:
        print(f'Error: {e}')

def add_new_item():
    try:
        name = input('Product Name: ').strip()
        if not name:
            print('Please enter a product name')
            return
        
        brands = input('Brand (optional): ').strip()
        barcode = input('Barcode (optional): ').strip()

        quantity = input('Quantity: ').strip()
        if not quantity.isdigit():
            print('Please use a valid number')
            return
        
        price = input('Price: $').strip()
        try:
            price = float(price)
        except ValueError:
            print('Please enter only numbers')
            return
        
        category = input('Category (optional): ')

        item_data = {
            'product_name': name,
            'quantity': int(quantity),
            'price': price
        }

        if brands:
            item_data['brands'] = brands
        if barcode:
            item_data['barcode'] = barcode
        if category:
            item_data['category'] = category

        response = requests.post(
            f'{API_base_url}/inventory',
            json=item_data,
            headers={'Content-Type': 'application/json'}            
        )

        if response.status_code == 201:
            print('Item Added Successfully')
        else:
            error_response(response)

    except Exception as e:
        print(f'Error: {e}')

def update_item():
    try:
        item_id = input('Enter item ID to update: ').strip()
        if not item_id.isdigit():
            print('Please use a number')
            return
        response = requests.get(f"{API_base_url}/inventory/{item_id}")

        if response.status_code != 200:
            error_response(response)
            return
        
        current_item = response.json()
        print('Item details')
        print(current_item)

        update_data = {}

        product_name = input('Enter updated product name: ').strip()
        if product_name:
            update_data["product_name"] = product_name

        brands = input('Enter updated brand: ').strip()
        if brands:
            update_data['brands'] = brands
        
        quantity = input('Enter updated quantity: ').strip()
        if quantity and quantity.isdigit():
            update_data['quantity'] = int(quantity)

        price = input('Enter updated price: $').strip()
        if price:
            try:
                update_data['price'] = float(price)
            except ValueError:
                print('Invalid price, keeping original price')

        category = input('Enter updated category: ').strip()
        if category:
            update_data['category'] = category

        if not update_data:
            print('No logged updates')
            return
        
        response = requests.patch(
            f'{API_base_url}/inventory/{item_id}',
            json=update_data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            updated_item = response.json()
            print('Updated successfully!')
            print(updated_item)
        else:
            error_response(response)

    except Exception as e:
        print(f'Error: {e}')

def delete_item():
    try:
        item_id = input('Enter item ID to delete: ').strip()

        if not item_id.isdigit():
            print('Please enter a nummber')
            return
        
        response = requests.delete(f'{API_base_url}/inventory/{item_id}')

        if response.status_code == 200:
            print('Item deleted.')
        else:
            error_response(response)

    except Exception as e:
        print(f'Error: {e}')

def search_openfoodfacts():
    try:
        barcode = input('Enter product barcode: ').strip()

        if not barcode:
            print('Barcode required')
            return

        print('Searching barcode...')

        response = requests.get(f'https://world.openfoodfacts.net/api/v2/product/{barcode}')
        if response.status_code == 200:
            product = response.json()
            print(f'Product: {product.get("product_name")}')
            print(f'Brand: {product.get("brands")}')
            print(f'Barcode: {product.get("barcode")}')
            print(f'Category: {product.get("category")}')

        add_to_inventory = input('Add item to inventory? (y/n) ').strip().lower()
        if add_to_inventory in ['yes', 'y']:
            quantity = input('Enter item quantity: ').strip()
            price = input('Enter price: $').strip()

            if quantity.isdigit() and price:
                item_data = {
                    'product_name': product.get('product_name'),
                    'brands': product.get('brands'),
                    'barcode': product.get('barcode'),
                    'quantity': int(quantity),
                    'price': float(price),
                    'category': product.get('category')
                }

                add_response = requests.post(
                    f'{API_base_url}/inventory',
                    json=item_data,
                    headers={'Content-Type': 'application/json'}
                )

                if add_response.status_code == 200:
                    print('Added to inventory')
                else:
                    print('Failed to add item to inventory')
                
        else:
            error_response(response)

    except Exception as e:
        print('Error: {e}')



def display_menu():
    """Display the main menu"""
    print("\n" + "="*70)
    print("  🍎 FOOD INVENTORY MANAGEMENT SYSTEM")
    print("="*70)
    print("\n  1. View all inventory items")
    print("  2. View specific item")
    print("  3. Add new item")
    print("  4. Update item")
    print("  5. Delete item")
    print("  6. Search OpenFoodFacts database")
    print("  7. Exit")
    print("\n" + "-"*70)


def main():
    print("  Welcome to Food Inventory Management System!")
    print("="*70)
    
    while True:
        display_menu()
        
        choice = input("  Enter your choice (1-7): ").strip()
        
        if choice == '1':
            get_inventory()
        
        elif choice == '2':
            get_item_by_id()
        
        elif choice == '3':
            add_new_item()
        
        elif choice == '4':
            update_item()
        
        elif choice == '5':
            delete_item()
        
        elif choice == '6':
            search_openfoodfacts()
        
        elif choice == '7':
            print('Exiting inventory management system')
            break
        
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")
        
        input("Press Enter to continue...")


if __name__ == "__main__":
    main()

