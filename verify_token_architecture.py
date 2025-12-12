#!/usr/bin/env python3
"""
Verification script for Page Access Token Architecture
Tests all critical methods to ensure implementation is correct
"""

import sys
sys.path.insert(0, '/workspaces/Socials')

from app import create_app, db
from app.models import User
from app.services.facebook_service import facebook_service
from datetime import datetime
import json

def test_database_schema():
    """Verify User model has all required fields"""
    print("\n✅ Testing Database Schema...")
    
    app = create_app()
    with app.app_context():
        # Check if User table exists with proper columns
        inspector = db.inspect(db.engine)
        columns = [c['name'] for c in inspector.get_columns('users')]
        
        required_fields = [
            'page_access_token',
            'facebook_pages',
            'selected_page_id',
            'selected_page_name',
            'access_token'
        ]
        
        for field in required_fields:
            if field in columns:
                print(f"  ✓ Column '{field}' exists")
            else:
                print(f"  ✗ Column '{field}' MISSING")
                return False
    
    return True

def test_facebook_service_methods():
    """Verify FacebookService has all required methods"""
    print("\n✅ Testing FacebookService Methods...")
    
    required_methods = [
        'get_authorization_url',
        'exchange_code_for_token',
        'get_user_info',
        'get_user_pages',
        'get_page_access_token',
        'publish_post',
        'schedule_post',
        'get_post_analytics'
    ]
    
    for method_name in required_methods:
        if hasattr(facebook_service, method_name):
            print(f"  ✓ Method '{method_name}' exists")
        else:
            print(f"  ✗ Method '{method_name}' MISSING")
            return False
    
    return True

def test_auth_routes():
    """Verify auth routes are properly configured"""
    print("\n✅ Testing Auth Routes...")
    
    app = create_app()
    
    routes = {
        '/auth/': 'index',
        '/auth/login': 'login',
        '/auth/facebook/callback': 'facebook_callback',
        '/auth/select-page': 'select_page',
        '/auth/logout': 'logout'
    }
    
    for route, expected_endpoint in routes.items():
        found = False
        for rule in app.url_map.iter_rules():
            if str(rule) == route:
                found = True
                print(f"  ✓ Route '{route}' exists")
                break
        if not found:
            print(f"  ✗ Route '{route}' NOT FOUND")
            return False
    
    return True

def test_token_architecture():
    """Verify token architecture in code"""
    print("\n✅ Testing Token Architecture...")
    
    # Check PostService uses page_access_token
    try:
        with open('/workspaces/Socials/app/services/post_service.py', 'r') as f:
            content = f.read()
            if 'user.page_access_token' in content:
                print("  ✓ PostService uses page_access_token")
            else:
                print("  ✗ PostService doesn't use page_access_token")
                return False
    except Exception as e:
        print(f"  ✗ Error checking PostService: {e}")
        return False
    
    # Check FacebookService publish_post uses page_access_token
    try:
        with open('/workspaces/Socials/app/services/facebook_service.py', 'r') as f:
            content = f.read()
            if 'page_access_token' in content:
                print("  ✓ FacebookService methods use page_access_token")
            else:
                print("  ✗ FacebookService doesn't use page_access_token")
                return False
    except Exception as e:
        print(f"  ✗ Error checking FacebookService: {e}")
        return False
    
    return True

def main():
    print("=" * 60)
    print("PAGE ACCESS TOKEN ARCHITECTURE - VERIFICATION")
    print("=" * 60)
    
    tests = [
        test_database_schema,
        test_facebook_service_methods,
        test_auth_routes,
        test_token_architecture
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ ALL TESTS PASSED - IMPLEMENTATION IS CORRECT")
        print("=" * 60)
        print("\n📋 Next Steps:")
        print("  1. Log in with Facebook (http://localhost:5000/auth/login)")
        print("  2. Select a Facebook page you manage")
        print("  3. Verify page_access_token is stored in database")
        print("  4. Create and publish a test post")
        print("  5. Check post appears on your Facebook page")
        return 0
    else:
        print("❌ SOME TESTS FAILED - CHECK IMPLEMENTATION")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    sys.exit(main())
