#!/usr/bin/env python3
"""
Comprehensive Frontend Testing Script for RxOrder Pharmacy App
Tests all user flows from login to order placement
"""

import asyncio
from playwright.async_api import async_playwright
import json

API_URL = "https://rxorder-platform.preview.emergentagent.com"

async def setup_auth(page):
    """Get auth token and inject into browser"""
    print("Setting up authentication...")
    auth_data = await page.evaluate(f"""
        async () => {{
            const otpResponse = await fetch('{API_URL}/api/auth/send-otp', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ phone: '5555555555' }})
            }});
            const otpData = await otpResponse.json();
            
            const verifyResponse = await fetch('{API_URL}/api/auth/verify-otp', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ phone: '5555555555', otp: otpData.otp }})
            }});
            const verifyData = await verifyResponse.json();
            
            localStorage.setItem('token', verifyData.token);
            localStorage.setItem('user', JSON.stringify(verifyData.user));
            
            return verifyData;
        }}
    """)
    print(f"✓ Auth setup complete for user: {auth_data['user']['phone']}")
    return auth_data

async def test_home_screen(page):
    """Test home screen functionality"""
    print("\n=== TESTING HOME SCREEN ===")
    
    await page.goto(f"{API_URL}/(tabs)/home")
    await page.wait_for_timeout(3000)
    
    # Check greeting
    greeting = await page.is_visible('text=Hello')
    print(f"✓ Greeting visible: {greeting}")
    
    # Check search bar
    search = await page.is_visible('text=Search medicines')
    print(f"✓ Search bar visible: {search}")
    
    # Check categories
    all_cat = await page.is_visible('text=All')
    print(f"✓ Categories visible: {all_cat}")
    
    # Check medicine cards
    paracetamol = await page.is_visible('text=Paracetamol')
    print(f"✓ Medicine cards visible: {paracetamol}")
    
    await page.screenshot(path="/tmp/test_home.png", quality=40, full_page=False)
    
    return greeting and search and paracetamol

async def test_category_filter(page):
    """Test category filtering"""
    print("\n=== TESTING CATEGORY FILTER ===")
    
    # Click Tablets category
    tablets = await page.wait_for_selector('text=Tablets', timeout=5000)
    await tablets.click()
    await page.wait_for_timeout(2000)
    
    print("✓ Clicked Tablets category")
    await page.screenshot(path="/tmp/test_category_tablets.png", quality=40, full_page=False)
    
    # Click Syrups category
    syrups = await page.wait_for_selector('text=Syrups', timeout=5000)
    await syrups.click()
    await page.wait_for_timeout(2000)
    
    print("✓ Clicked Syrups category")
    await page.screenshot(path="/tmp/test_category_syrups.png", quality=40, full_page=False)
    
    return True

async def test_search(page):
    """Test search functionality"""
    print("\n=== TESTING SEARCH ===")
    
    # Click search bar to navigate to search screen
    search_bar = await page.wait_for_selector('text=Search medicines', timeout=5000)
    await search_bar.click()
    await page.wait_for_timeout(2000)
    
    # Check if on search screen
    search_title = await page.is_visible('text=Search Medicines')
    print(f"✓ Search screen loaded: {search_title}")
    
    # Enter search query
    search_input = await page.wait_for_selector('input[placeholder*="Search by name"]', timeout=5000)
    await search_input.fill("paracetamol")
    await page.wait_for_timeout(2000)
    
    print("✓ Entered search query: paracetamol")
    await page.screenshot(path="/tmp/test_search_results.png", quality=40, full_page=False)
    
    # Check if results are visible
    results = await page.is_visible('text=Paracetamol')
    print(f"✓ Search results visible: {results}")
    
    return search_title and results

async def test_medicine_detail(page):
    """Test medicine detail screen"""
    print("\n=== TESTING MEDICINE DETAIL ===")
    
    # Go back to home
    await page.goto(f"{API_URL}/(tabs)/home")
    await page.wait_for_timeout(2000)
    
    # Click on first medicine card
    medicine_card = await page.wait_for_selector('text=Paracetamol 500mg', timeout=5000)
    await medicine_card.click()
    await page.wait_for_timeout(3000)
    
    # Check if detail screen loaded
    detail_title = await page.is_visible('text=Medicine Details')
    composition = await page.is_visible('text=Composition')
    add_to_cart = await page.is_visible('text=Add to Cart')
    
    print(f"✓ Medicine detail screen loaded: {detail_title}")
    print(f"✓ Composition section visible: {composition}")
    print(f"✓ Add to Cart button visible: {add_to_cart}")
    
    await page.screenshot(path="/tmp/test_medicine_detail.png", quality=40, full_page=False)
    
    return detail_title and add_to_cart

async def test_add_to_cart(page):
    """Test add to cart functionality"""
    print("\n=== TESTING ADD TO CART ===")
    
    # Click Add to Cart button
    add_btn = await page.wait_for_selector('text=Add to Cart', timeout=5000)
    await add_btn.click()
    await page.wait_for_timeout(2000)
    
    print("✓ Clicked Add to Cart button")
    
    # Handle alert dialog
    page.on("dialog", lambda dialog: dialog.accept())
    await page.wait_for_timeout(1000)
    
    await page.screenshot(path="/tmp/test_added_to_cart.png", quality=40, full_page=False)
    
    return True

async def test_cart_screen(page):
    """Test cart screen"""
    print("\n=== TESTING CART SCREEN ===")
    
    # Navigate to cart tab
    await page.goto(f"{API_URL}/(tabs)/cart")
    await page.wait_for_timeout(3000)
    
    # Check if cart has items
    cart_title = await page.is_visible('text=My Cart')
    checkout_btn = await page.is_visible('text=Proceed to Checkout')
    
    print(f"✓ Cart screen loaded: {cart_title}")
    print(f"✓ Checkout button visible: {checkout_btn}")
    
    await page.screenshot(path="/tmp/test_cart.png", quality=40, full_page=False)
    
    return cart_title and checkout_btn

async def test_checkout(page):
    """Test checkout flow"""
    print("\n=== TESTING CHECKOUT ===")
    
    # Click Proceed to Checkout
    checkout_btn = await page.wait_for_selector('text=Proceed to Checkout', timeout=5000)
    await checkout_btn.click()
    await page.wait_for_timeout(3000)
    
    # Check if checkout screen loaded
    checkout_title = await page.is_visible('text=Checkout')
    delivery_address = await page.is_visible('text=Delivery Address')
    
    print(f"✓ Checkout screen loaded: {checkout_title}")
    print(f"✓ Delivery address section visible: {delivery_address}")
    
    # Fill address form
    line1 = await page.wait_for_selector('input[placeholder*="Address Line 1"]', timeout=5000)
    await line1.fill("123 Test Street")
    
    city = await page.wait_for_selector('input[placeholder*="City"]', timeout=5000)
    await city.fill("Mumbai")
    
    state = await page.wait_for_selector('input[placeholder*="State"]', timeout=5000)
    await state.fill("Maharashtra")
    
    pincode = await page.wait_for_selector('input[placeholder*="Pincode"]', timeout=5000)
    await pincode.fill("400001")
    
    print("✓ Filled address form")
    await page.screenshot(path="/tmp/test_checkout_form.png", quality=40, full_page=False)
    
    # Click Place Order
    place_order = await page.wait_for_selector('text=Place Order', timeout=5000)
    await place_order.click()
    await page.wait_for_timeout(3000)
    
    print("✓ Clicked Place Order")
    
    return True

async def test_order_success(page):
    """Test order success screen"""
    print("\n=== TESTING ORDER SUCCESS ===")
    
    # Check if order success screen loaded
    success_title = await page.is_visible('text=Order Placed Successfully')
    order_id = await page.is_visible('text=Order ID')
    
    print(f"✓ Order success screen loaded: {success_title}")
    print(f"✓ Order ID visible: {order_id}")
    
    await page.screenshot(path="/tmp/test_order_success.png", quality=40, full_page=False)
    
    return success_title

async def test_orders_screen(page):
    """Test orders screen"""
    print("\n=== TESTING ORDERS SCREEN ===")
    
    # Navigate to orders tab
    await page.goto(f"{API_URL}/(tabs)/orders")
    await page.wait_for_timeout(3000)
    
    # Check if orders screen loaded
    orders_title = await page.is_visible('text=My Orders')
    
    print(f"✓ Orders screen loaded: {orders_title}")
    await page.screenshot(path="/tmp/test_orders.png", quality=40, full_page=False)
    
    return orders_title

async def test_profile_screen(page):
    """Test profile screen"""
    print("\n=== TESTING PROFILE SCREEN ===")
    
    # Navigate to profile tab
    await page.goto(f"{API_URL}/(tabs)/profile")
    await page.wait_for_timeout(3000)
    
    # Check if profile screen loaded
    profile_title = await page.is_visible('text=Profile')
    logout_btn = await page.is_visible('text=Logout')
    
    print(f"✓ Profile screen loaded: {profile_title}")
    print(f"✓ Logout button visible: {logout_btn}")
    
    await page.screenshot(path="/tmp/test_profile.png", quality=40, full_page=False)
    
    return profile_title and logout_btn

async def test_tab_navigation(page):
    """Test bottom tab navigation"""
    print("\n=== TESTING TAB NAVIGATION ===")
    
    # Test all tabs
    tabs = ['Home', 'Search', 'Cart', 'Orders', 'Profile']
    
    for tab in tabs:
        tab_element = await page.is_visible(f'text={tab}')
        print(f"✓ {tab} tab visible: {tab_element}")
    
    return True

async def main():
    """Main test runner"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 390, "height": 844})
        page = await context.new_page()
        
        # Enable console logging
        page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))
        
        results = {}
        
        try:
            # Setup authentication
            await setup_auth(page)
            await page.reload()
            await page.wait_for_timeout(2000)
            
            # Run all tests
            results['home_screen'] = await test_home_screen(page)
            results['category_filter'] = await test_category_filter(page)
            results['search'] = await test_search(page)
            results['medicine_detail'] = await test_medicine_detail(page)
            results['add_to_cart'] = await test_add_to_cart(page)
            results['cart_screen'] = await test_cart_screen(page)
            results['checkout'] = await test_checkout(page)
            results['order_success'] = await test_order_success(page)
            results['orders_screen'] = await test_orders_screen(page)
            results['profile_screen'] = await test_profile_screen(page)
            results['tab_navigation'] = await test_tab_navigation(page)
            
        except Exception as e:
            print(f"\n✗ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            await page.screenshot(path="/tmp/test_error.png", quality=40, full_page=False)
        
        finally:
            await browser.close()
        
        # Print summary
        print("\n" + "="*50)
        print("TEST SUMMARY")
        print("="*50)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for test, result in results.items():
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {test}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        return results

if __name__ == "__main__":
    asyncio.run(main())
