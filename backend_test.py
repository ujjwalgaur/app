#!/usr/bin/env python3
"""
RxOrder Pharmacy App - Backend API Testing
Tests all backend endpoints comprehensively
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional

# API Configuration
API_BASE_URL = "https://rxorder-platform.preview.emergentagent.com/api"

# Test credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
TEST_PHONE = "9876543210"

# Global variables for test data
auth_token = None
admin_token = None
test_user_id = None
test_medicine_id = None
test_order_id = None
test_prescription_id = None

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_pass(self, test_name: str):
        self.passed += 1
        print(f"✅ {test_name}")
    
    def add_fail(self, test_name: str, error: str):
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
        print(f"❌ {test_name}: {error}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success Rate: {(self.passed/total*100):.1f}%" if total > 0 else "0%")
        
        if self.errors:
            print(f"\n{'='*60}")
            print(f"FAILED TESTS:")
            print(f"{'='*60}")
            for error in self.errors:
                print(f"❌ {error}")

result = TestResult()

def make_request(method: str, endpoint: str, data: Dict = None, headers: Dict = None, auth_token: str = None) -> tuple:
    """Make HTTP request and return (success, response_data, status_code)"""
    url = f"{API_BASE_URL}{endpoint}"
    
    # Default headers
    default_headers = {"Content-Type": "application/json"}
    if headers:
        default_headers.update(headers)
    
    # Add auth token if provided
    if auth_token:
        default_headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=default_headers, timeout=30)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=default_headers, timeout=30)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=default_headers, timeout=30)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=default_headers, timeout=30)
        else:
            return False, {"error": f"Unsupported method: {method}"}, 0
        
        try:
            response_data = response.json()
        except:
            response_data = {"text": response.text}
        
        return response.status_code < 400, response_data, response.status_code
    
    except requests.exceptions.RequestException as e:
        return False, {"error": str(e)}, 0

def test_seed_database():
    """Test database seeding"""
    print("\n🌱 Testing Database Seeding...")
    
    success, data, status = make_request("POST", "/seed")
    if success and status == 200:
        result.add_pass("Database seeding")
        return True
    else:
        result.add_fail("Database seeding", f"Status: {status}, Error: {data}")
        return False

def test_authentication_flow():
    """Test complete authentication flow"""
    global auth_token, test_user_id
    
    print("\n🔐 Testing Authentication Flow...")
    
    # Test 1: Send OTP
    otp_data = {"phone": TEST_PHONE}
    success, data, status = make_request("POST", "/auth/send-otp", otp_data)
    
    if not success or status != 200:
        result.add_fail("Send OTP", f"Status: {status}, Error: {data}")
        return False
    
    result.add_pass("Send OTP")
    
    # Extract OTP from response (mock implementation returns OTP)
    otp = data.get("otp")
    if not otp:
        result.add_fail("Extract OTP", "OTP not found in response")
        return False
    
    result.add_pass("Extract OTP from response")
    
    # Test 2: Verify OTP
    verify_data = {"phone": TEST_PHONE, "otp": otp}
    success, data, status = make_request("POST", "/auth/verify-otp", verify_data)
    
    if not success or status != 200:
        result.add_fail("Verify OTP", f"Status: {status}, Error: {data}")
        return False
    
    auth_token = data.get("token")
    user_data = data.get("user")
    
    if not auth_token:
        result.add_fail("Get JWT token", "Token not found in response")
        return False
    
    if not user_data or not user_data.get("id"):
        result.add_fail("Get user data", "User data not found in response")
        return False
    
    test_user_id = user_data.get("id")
    result.add_pass("Verify OTP and get JWT token")
    
    # Test 3: Get current user
    success, data, status = make_request("GET", "/auth/me", auth_token=auth_token)
    
    if not success or status != 200:
        result.add_fail("Get current user", f"Status: {status}, Error: {data}")
        return False
    
    if data.get("phone") != TEST_PHONE:
        result.add_fail("Verify user data", f"Phone mismatch: {data.get('phone')} != {TEST_PHONE}")
        return False
    
    result.add_pass("Get current user info")
    
    # Test 4: Update profile
    profile_data = {"name": "Test User", "email": "test@example.com"}
    success, data, status = make_request("PUT", "/auth/profile", profile_data, auth_token=auth_token)
    
    if not success or status != 200:
        result.add_fail("Update profile", f"Status: {status}, Error: {data}")
        return False
    
    result.add_pass("Update user profile")
    
    return True

def test_medicine_catalog():
    """Test medicine catalog endpoints"""
    global test_medicine_id
    
    print("\n💊 Testing Medicine Catalog...")
    
    # Test 1: Get all medicines
    success, data, status = make_request("GET", "/medicines")
    
    if not success or status != 200:
        result.add_fail("Get all medicines", f"Status: {status}, Error: {data}")
        return False
    
    if not isinstance(data, list) or len(data) == 0:
        result.add_fail("Verify medicines list", "No medicines found")
        return False
    
    # Store first medicine ID for later tests
    test_medicine_id = data[0].get("id")
    result.add_pass("Get all medicines")
    
    # Test 2: Search medicines
    success, data, status = make_request("GET", "/medicines?search=paracetamol")
    
    if not success or status != 200:
        result.add_fail("Search medicines", f"Status: {status}, Error: {data}")
        return False
    
    # Check if search results contain paracetamol
    found_paracetamol = any("paracetamol" in med.get("name", "").lower() for med in data)
    if not found_paracetamol:
        result.add_fail("Verify search results", "Paracetamol not found in search results")
        return False
    
    result.add_pass("Search medicines by name")
    
    # Test 3: Filter by category
    success, data, status = make_request("GET", "/medicines?category=Tablets")
    
    if not success or status != 200:
        result.add_fail("Filter by category", f"Status: {status}, Error: {data}")
        return False
    
    # Check if all results are tablets
    all_tablets = all(med.get("category") == "Tablets" for med in data)
    if not all_tablets:
        result.add_fail("Verify category filter", "Non-tablet medicines found in tablets filter")
        return False
    
    result.add_pass("Filter medicines by category")
    
    # Test 4: Get categories
    success, data, status = make_request("GET", "/categories")
    
    if not success or status != 200:
        result.add_fail("Get categories", f"Status: {status}, Error: {data}")
        return False
    
    categories = data.get("categories", [])
    if not categories or len(categories) == 0:
        result.add_fail("Verify categories", "No categories found")
        return False
    
    result.add_pass("Get medicine categories")
    
    # Test 5: Get medicine details
    if test_medicine_id:
        success, data, status = make_request("GET", f"/medicines/{test_medicine_id}")
        
        if not success or status != 200:
            result.add_fail("Get medicine details", f"Status: {status}, Error: {data}")
            return False
        
        if data.get("id") != test_medicine_id:
            result.add_fail("Verify medicine details", "Medicine ID mismatch")
            return False
        
        result.add_pass("Get medicine details")
    
    return True

def test_cart_operations():
    """Test cart management"""
    print("\n🛒 Testing Cart Operations...")
    
    if not auth_token or not test_medicine_id:
        result.add_fail("Cart operations setup", "Missing auth token or medicine ID")
        return False
    
    # Test 1: Get empty cart
    success, data, status = make_request("GET", "/cart", auth_token=auth_token)
    
    if not success or status != 200:
        result.add_fail("Get empty cart", f"Status: {status}, Error: {data}")
        return False
    
    if data.get("total", 0) != 0:
        result.add_fail("Verify empty cart", f"Cart total should be 0, got {data.get('total')}")
        return False
    
    result.add_pass("Get empty cart")
    
    # Test 2: Add item to cart
    add_data = {"medicine_id": test_medicine_id, "quantity": 2}
    success, data, status = make_request("POST", "/cart/add", add_data, auth_token=auth_token)
    
    if not success or status != 200:
        result.add_fail("Add to cart", f"Status: {status}, Error: {data}")
        return False
    
    result.add_pass("Add item to cart")
    
    # Test 3: Verify cart has items
    success, data, status = make_request("GET", "/cart", auth_token=auth_token)
    
    if not success or status != 200:
        result.add_fail("Get cart after adding", f"Status: {status}, Error: {data}")
        return False
    
    items = data.get("items", [])
    if len(items) == 0:
        result.add_fail("Verify cart items", "No items found in cart after adding")
        return False
    
    if items[0].get("quantity") != 2:
        result.add_fail("Verify item quantity", f"Expected quantity 2, got {items[0].get('quantity')}")
        return False
    
    result.add_pass("Verify cart items after adding")
    
    # Test 4: Update cart item quantity
    success, data, status = make_request("PUT", f"/cart/update/{test_medicine_id}?quantity=3", auth_token=auth_token)
    
    if not success or status != 200:
        result.add_fail("Update cart quantity", f"Status: {status}, Error: {data}")
        return False
    
    result.add_pass("Update cart item quantity")
    
    # Test 5: Verify updated quantity
    success, data, status = make_request("GET", "/cart", auth_token=auth_token)
    
    if success and status == 200:
        items = data.get("items", [])
        if items and items[0].get("quantity") == 3:
            result.add_pass("Verify updated quantity")
        else:
            result.add_fail("Verify updated quantity", f"Expected quantity 3, got {items[0].get('quantity') if items else 'no items'}")
    else:
        result.add_fail("Get cart after update", f"Status: {status}, Error: {data}")
    
    return True

def test_order_flow():
    """Test order creation and management"""
    global test_order_id
    
    print("\n📦 Testing Order Flow...")
    
    if not auth_token:
        result.add_fail("Order flow setup", "Missing auth token")
        return False
    
    # Ensure cart has items first
    if test_medicine_id:
        add_data = {"medicine_id": test_medicine_id, "quantity": 1}
        make_request("POST", "/cart/add", add_data, auth_token=auth_token)
    
    # Test 1: Create order
    order_data = {
        "delivery_address": {
            "line1": "123 Test Street",
            "line2": "Apt 4B",
            "city": "Mumbai",
            "state": "Maharashtra",
            "pincode": "400001",
            "phone": "9876543210"
        },
        "payment_method": "COD"
    }
    
    success, data, status = make_request("POST", "/orders", order_data, auth_token=auth_token)
    
    if not success or status != 200:
        result.add_fail("Create order", f"Status: {status}, Error: {data}")
        return False
    
    test_order_id = data.get("id")
    if not test_order_id:
        result.add_fail("Get order ID", "Order ID not found in response")
        return False
    
    result.add_pass("Create order from cart")
    
    # Test 2: Verify cart is cleared
    success, data, status = make_request("GET", "/cart", auth_token=auth_token)
    
    if success and status == 200:
        items = data.get("items", [])
        if len(items) == 0:
            result.add_pass("Verify cart cleared after order")
        else:
            result.add_fail("Verify cart cleared", f"Cart still has {len(items)} items")
    else:
        result.add_fail("Get cart after order", f"Status: {status}, Error: {data}")
    
    # Test 3: Get user orders
    success, data, status = make_request("GET", "/orders", auth_token=auth_token)
    
    if not success or status != 200:
        result.add_fail("Get user orders", f"Status: {status}, Error: {data}")
        return False
    
    if not isinstance(data, list) or len(data) == 0:
        result.add_fail("Verify orders list", "No orders found")
        return False
    
    result.add_pass("Get user orders")
    
    # Test 4: Get specific order
    if test_order_id:
        success, data, status = make_request("GET", f"/orders/{test_order_id}", auth_token=auth_token)
        
        if not success or status != 200:
            result.add_fail("Get order details", f"Status: {status}, Error: {data}")
            return False
        
        if data.get("id") != test_order_id:
            result.add_fail("Verify order details", "Order ID mismatch")
            return False
        
        result.add_pass("Get order details")
    
    return True

def test_prescription_upload():
    """Test prescription upload"""
    global test_prescription_id
    
    print("\n📋 Testing Prescription Upload...")
    
    if not auth_token:
        result.add_fail("Prescription upload setup", "Missing auth token")
        return False
    
    # Test 1: Upload prescription
    prescription_data = {
        "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
        "notes": "Test prescription upload"
    }
    
    success, data, status = make_request("POST", "/prescriptions", prescription_data, auth_token=auth_token)
    
    if not success or status != 200:
        result.add_fail("Upload prescription", f"Status: {status}, Error: {data}")
        return False
    
    test_prescription_id = data.get("id")
    if not test_prescription_id:
        result.add_fail("Get prescription ID", "Prescription ID not found in response")
        return False
    
    result.add_pass("Upload prescription")
    
    # Test 2: Get user prescriptions
    success, data, status = make_request("GET", "/prescriptions", auth_token=auth_token)
    
    if not success or status != 200:
        result.add_fail("Get user prescriptions", f"Status: {status}, Error: {data}")
        return False
    
    if not isinstance(data, list):
        result.add_fail("Verify prescriptions list", "Invalid prescriptions response")
        return False
    
    result.add_pass("Get user prescriptions")
    
    return True

def test_admin_endpoints():
    """Test admin functionality"""
    global admin_token
    
    print("\n👨‍💼 Testing Admin Endpoints...")
    
    # Test 1: Admin login
    admin_data = {"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
    success, data, status = make_request("POST", "/admin/login", admin_data)
    
    if not success or status != 200:
        result.add_fail("Admin login", f"Status: {status}, Error: {data}")
        return False
    
    admin_token = data.get("token")
    if not admin_token:
        result.add_fail("Get admin token", "Admin token not found in response")
        return False
    
    result.add_pass("Admin login")
    
    # Test 2: Get dashboard stats
    success, data, status = make_request("GET", "/admin/dashboard", auth_token=admin_token)
    
    if not success or status != 200:
        result.add_fail("Get dashboard stats", f"Status: {status}, Error: {data}")
        return False
    
    required_fields = ["total_orders", "total_revenue", "pending_orders", "total_users", "low_stock_medicines", "pending_prescriptions"]
    for field in required_fields:
        if field not in data:
            result.add_fail("Verify dashboard fields", f"Missing field: {field}")
            return False
    
    result.add_pass("Get dashboard statistics")
    
    # Test 3: Get all orders (admin)
    success, data, status = make_request("GET", "/admin/orders", auth_token=admin_token)
    
    if not success or status != 200:
        result.add_fail("Get all orders (admin)", f"Status: {status}, Error: {data}")
        return False
    
    if not isinstance(data, list):
        result.add_fail("Verify admin orders list", "Invalid orders response")
        return False
    
    result.add_pass("Get all orders (admin)")
    
    # Test 4: Create medicine (admin)
    medicine_data = {
        "name": "Test Medicine",
        "salt_composition": "Test Composition",
        "category": "Tablets",
        "price": 100.0,
        "discount": 10,
        "stock_quantity": 50,
        "description": "Test medicine description",
        "usage": "Test usage instructions",
        "manufacturer": "Test Pharma",
        "requires_prescription": False
    }
    
    success, data, status = make_request("POST", "/admin/medicines", medicine_data, auth_token=admin_token)
    
    if not success or status != 200:
        result.add_fail("Create medicine (admin)", f"Status: {status}, Error: {data}")
        return False
    
    new_medicine_id = data.get("id")
    if not new_medicine_id:
        result.add_fail("Get new medicine ID", "Medicine ID not found in response")
        return False
    
    result.add_pass("Create medicine (admin)")
    
    # Test 5: Update medicine (admin)
    update_data = {"price": 120.0, "discount": 15}
    success, data, status = make_request("PUT", f"/admin/medicines/{new_medicine_id}", update_data, auth_token=admin_token)
    
    if not success or status != 200:
        result.add_fail("Update medicine (admin)", f"Status: {status}, Error: {data}")
        return False
    
    result.add_pass("Update medicine (admin)")
    
    # Test 6: Get all prescriptions (admin)
    success, data, status = make_request("GET", "/admin/prescriptions", auth_token=admin_token)
    
    if not success or status != 200:
        result.add_fail("Get all prescriptions (admin)", f"Status: {status}, Error: {data}")
        return False
    
    if not isinstance(data, list):
        result.add_fail("Verify admin prescriptions list", "Invalid prescriptions response")
        return False
    
    result.add_pass("Get all prescriptions (admin)")
    
    # Test 7: Update order status (admin)
    if test_order_id:
        status_data = {"status": "confirmed"}
        success, data, status = make_request("PUT", f"/admin/orders/{test_order_id}/status", status_data, auth_token=admin_token)
        
        if not success or status != 200:
            result.add_fail("Update order status (admin)", f"Status: {status}, Error: {data}")
            return False
        
        result.add_pass("Update order status (admin)")
    
    return True

def test_cart_clear():
    """Test cart clearing functionality"""
    print("\n🗑️ Testing Cart Clear...")
    
    if not auth_token:
        result.add_fail("Cart clear setup", "Missing auth token")
        return False
    
    # Add item to cart first
    if test_medicine_id:
        add_data = {"medicine_id": test_medicine_id, "quantity": 1}
        make_request("POST", "/cart/add", add_data, auth_token=auth_token)
    
    # Clear cart
    success, data, status = make_request("DELETE", "/cart/clear", auth_token=auth_token)
    
    if not success or status != 200:
        result.add_fail("Clear cart", f"Status: {status}, Error: {data}")
        return False
    
    result.add_pass("Clear cart")
    
    # Verify cart is empty
    success, data, status = make_request("GET", "/cart", auth_token=auth_token)
    
    if success and status == 200:
        items = data.get("items", [])
        if len(items) == 0:
            result.add_pass("Verify cart cleared")
        else:
            result.add_fail("Verify cart cleared", f"Cart still has {len(items)} items")
    else:
        result.add_fail("Get cart after clear", f"Status: {status}, Error: {data}")
    
    return True

def main():
    """Run all tests"""
    print("🚀 Starting RxOrder Pharmacy Backend API Tests")
    print(f"API Base URL: {API_BASE_URL}")
    print("="*60)
    
    # Test sequence
    tests = [
        ("Database Seeding", test_seed_database),
        ("Authentication Flow", test_authentication_flow),
        ("Medicine Catalog", test_medicine_catalog),
        ("Cart Operations", test_cart_operations),
        ("Order Flow", test_order_flow),
        ("Prescription Upload", test_prescription_upload),
        ("Admin Endpoints", test_admin_endpoints),
        ("Cart Clear", test_cart_clear),
    ]
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*60}")
            print(f"Running: {test_name}")
            print(f"{'='*60}")
            test_func()
        except Exception as e:
            result.add_fail(f"{test_name} (Exception)", str(e))
            print(f"❌ {test_name} failed with exception: {e}")
    
    # Print final summary
    result.summary()
    
    # Return exit code
    return 0 if result.failed == 0 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)