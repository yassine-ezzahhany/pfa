"""
Test script for JWT Authentication
Run this to test the complete authentication flow
"""

import requests
import json
from time import sleep

BASE_URL = "http://localhost:8000"

def print_response(title, response):
    print(f"\n{'='*60}")
    print(f"📍 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print("Response:", json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print("Response:", response.text)

def test_authentication():
    """Complete authentication workflow test"""
    
    # Test data
    test_user = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "TestPass123!"
    }

    print("\n" + "="*60)
    print("🔐 JWT AUTHENTICATION TEST")
    print("="*60)

    # 1. Test Registration
    print("\n1️⃣  Testing Registration...")
    try:
        register_response = requests.post(
            f"{BASE_URL}/register",
            json=test_user
        )
        print_response("Registration Response", register_response)
        
        if register_response.status_code != 200:
            print("⚠️  Registration may have failed or user already exists")
    except Exception as e:
        print(f"❌ Registration Error: {e}")
        return

    sleep(1)

    # 2. Test Login (Valid Credentials)
    print("\n2️⃣  Testing Login with Valid Credentials...")
    try:
        login_response = requests.post(
            f"{BASE_URL}/login",
            json={
                "email": test_user["email"],
                "password": test_user["password"]
            }
        )
        print_response("Login Response (Valid)", login_response)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get("access_token")
            print(f"✅ Token obtained: {access_token[:50]}...")
        else:
            print("❌ Login failed")
            return
    except Exception as e:
        print(f"❌ Login Error: {e}")
        return

    sleep(1)

    # 3. Test Login (Invalid Password)
    print("\n3️⃣  Testing Login with Invalid Password...")
    try:
        invalid_login_response = requests.post(
            f"{BASE_URL}/login",
            json={
                "email": test_user["email"],
                "password": "InvalidPass123!"
            }
        )
        print_response("Login Response (Invalid)", invalid_login_response)
        
        if invalid_login_response.status_code == 401:
            print("✅ Correctly rejected invalid password")
    except Exception as e:
        print(f"❌ Error: {e}")

    sleep(1)

    # 4. Test Protected Route with Valid Token
    print("\n4️⃣  Testing Protected Route with Valid Token...")
    try:
        protected_response = requests.get(
            f"{BASE_URL}/protected",
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )
        print_response("Protected Route (Valid Token)", protected_response)
        
        if protected_response.status_code == 200:
            print("✅ Successfully accessed protected route")
    except Exception as e:
        print(f"❌ Error: {e}")

    sleep(1)

    # 5. Test Protected Route without Token
    print("\n5️⃣  Testing Protected Route without Token...")
    try:
        no_token_response = requests.get(f"{BASE_URL}/protected")
        print_response("Protected Route (No Token)", no_token_response)
        
        if no_token_response.status_code in [401, 403]:
            print("✅ Correctly blocked access without token")
    except Exception as e:
        print(f"❌ Error: {e}")

    sleep(1)

    # 6. Test Protected Route with Invalid Token
    print("\n6️⃣  Testing Protected Route with Invalid Token...")
    try:
        invalid_token_response = requests.get(
            f"{BASE_URL}/protected",
            headers={
                "Authorization": "Bearer invalid_token_12345"
            }
        )
        print_response("Protected Route (Invalid Token)", invalid_token_response)
        
        if invalid_token_response.status_code == 401:
            print("✅ Correctly rejected invalid token")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 7. Test Info Route
    print("\n7️⃣  Testing Info Route...")
    try:
        info_response = requests.get(f"{BASE_URL}/")
        print_response("Root Info Route", info_response)
        
        if info_response.status_code == 200:
            print("✅ Info route accessible")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "="*60)
    print("✅ JWT Authentication Test Complete!")
    print("="*60 + "\n")

if __name__ == "__main__":
    print("Starting JWT Authentication Tests...")
    print("Make sure the FastAPI server is running on http://localhost:8000")
    print("Start the server with: uvicorn main:app --reload")
    
    input("\nPress Enter to begin tests...")
    
    test_authentication()
