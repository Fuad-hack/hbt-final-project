"""
Integration test for frontend-backend
"""
import urllib.request
import json

BASE_URL = "http://localhost:5000"

def test_register():
    """Test registration"""
    print("1. Testing Register...")
    data = json.dumps({
        'name': 'Integration Test',
        'email': 'integration@test.com',
        'password': 'testpass123'
    }).encode()
    
    req = urllib.request.Request(
        f'{BASE_URL}/api/auth/register',
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        response = urllib.request.urlopen(req, timeout=10)
        result = json.loads(response.read().decode())
        print(f"   Status: {response.status}")
        print(f"   Token: {'Yes' if result.get('access_token') else 'No'}")
        return result.get('access_token')
    except Exception as e:
        print(f"   Error: {e}")
        return None

def test_login():
    """Test login with existing admin"""
    print("2. Testing Login (admin)...")
    data = json.dumps({
        'username': 'admin',
        'password': 'admin123'
    }).encode()
    
    req = urllib.request.Request(
        f'{BASE_URL}/api/auth/login',
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        response = urllib.request.urlopen(req, timeout=10)
        result = json.loads(response.read().decode())
        print(f"   Status: {response.status}")
        print(f"   Token: {'Yes' if result.get('access_token') else 'No'}")
        return result.get('access_token')
    except Exception as e:
        print(f"   Error: {e}")
        return None

def test_dashboard(token):
    """Test dashboard stats"""
    print("3. Testing Dashboard Stats...")
    req = urllib.request.Request(
        f'{BASE_URL}/api/dashboard/stats',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    try:
        response = urllib.request.urlopen(req, timeout=10)
        result = json.loads(response.read().decode())
        print(f"   Status: {response.status}")
        print(f"   Stats: {result}")
        return True
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_users(token):
    """Test users list"""
    print("4. Testing Users List...")
    req = urllib.request.Request(
        f'{BASE_URL}/api/users',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    try:
        response = urllib.request.urlopen(req, timeout=10)
        result = json.loads(response.read().decode())
        print(f"   Status: {response.status}")
        print(f"   Users count: {len(result.get('users', []))}")
        return True
    except Exception as e:
        print(f"   Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("FRONTEND-BACKEND INTEGRATION TEST")
    print("=" * 50)
    
    # Test 1: Register
    token1 = test_register()
    
    # Test 2: Login
    token2 = test_login()
    
    if token2:
        # Test 3: Dashboard
        test_dashboard(token2)
        
        # Test 4: Users
        test_users(token2)
    
    print("=" * 50)
    print("✅ Integration test completed!")
    print("=" * 50)
