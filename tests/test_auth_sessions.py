#!/usr/bin/env python3
"""
Test script to verify authentication and user-specific sessions.
"""

import os
import sys
import requests
import json
import time

# Add the parent directory to the path so we can import the intake_agent module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_auth_and_sessions():
    """Test authentication and user-specific session management."""
    base_url = "http://localhost:8000"  # Adjust if your API runs on a different port
    
    print("\n=== Testing Authentication and User-Specific Sessions ===\n")
    
    # Test 1: Login as two different users
    print("Test 1: Logging in as two different users")
    
    # Login as user1
    response1 = requests.post(
        f"{base_url}/token",
        data={"username": "admin", "password": "admin"}
    )
    
    if response1.status_code != 200:
        print(f"Error logging in as admin: {response1.status_code}")
        print(response1.text)
        return
        
    admin_token = response1.json().get("access_token")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print(f"✓ Successfully logged in as admin")
    
    # Login as user2
    response2 = requests.post(
        f"{base_url}/token",
        data={"username": "user", "password": "user"}
    )
    
    if response2.status_code != 200:
        print(f"Error logging in as user: {response2.status_code}")
        print(response2.text)
        return
        
    user_token = response2.json().get("access_token")
    user_headers = {"Authorization": f"Bearer {user_token}"}
    print(f"✓ Successfully logged in as user")
    
    # Test 2: Create a session for each user
    print("\nTest 2: Creating a session for each user")
    
    # Create admin session
    admin_response = requests.post(
        f"{base_url}/intake/query",
        headers=admin_headers,
        json={"input_text": "I'm admin creating a new conversation"}
    )
    
    if admin_response.status_code != 200:
        print(f"Error creating admin session: {admin_response.status_code}")
        print(admin_response.text)
        return
        
    admin_session_id = admin_response.json().get("session_id")
    print(f"✓ Created admin session with ID: {admin_session_id}")
    
    # Create user session
    user_response = requests.post(
        f"{base_url}/intake/query",
        headers=user_headers,
        json={"input_text": "I'm user creating a new conversation"}
    )
    
    if user_response.status_code != 200:
        print(f"Error creating user session: {user_response.status_code}")
        print(user_response.text)
        return
        
    user_session_id = user_response.json().get("session_id")
    print(f"✓ Created user session with ID: {user_session_id}")
    
    # Test 3: Continue the conversation for each user
    print("\nTest 3: Continuing the conversation for each user")
    
    # Continue admin session
    admin_continue = requests.post(
        f"{base_url}/intake/query",
        headers=admin_headers,
        json={
            "input_text": "This is a follow-up from admin",
            "session_id": admin_session_id
        }
    )
    
    if admin_continue.status_code != 200:
        print(f"Error continuing admin session: {admin_continue.status_code}")
        print(admin_continue.text)
    else:
        admin_messages = admin_continue.json().get("messages", [])
        print(f"✓ Admin conversation continued with {len(admin_messages)} messages")
    
    # Continue user session
    user_continue = requests.post(
        f"{base_url}/intake/query",
        headers=user_headers,
        json={
            "input_text": "This is a follow-up from user",
            "session_id": user_session_id
        }
    )
    
    if user_continue.status_code != 200:
        print(f"Error continuing user session: {user_continue.status_code}")
        print(user_continue.text)
    else:
        user_messages = user_continue.json().get("messages", [])
        print(f"✓ User conversation continued with {len(user_messages)} messages")
    
    # Test 4: Try to access another user's session
    print("\nTest 4: Trying to access another user's session")
    
    # User tries to access admin's session
    user_access_admin = requests.get(
        f"{base_url}/intake/sessions/{admin_session_id}",
        headers=user_headers
    )
    
    if user_access_admin.status_code == 404:
        print(f"✓ User correctly cannot access admin's session (404)")
    else:
        print(f"⚠️ User incorrectly accessed admin's session: {user_access_admin.status_code}")
        print(user_access_admin.text)
    
    # Admin tries to access user's session
    admin_access_user = requests.get(
        f"{base_url}/intake/sessions/{user_session_id}",
        headers=admin_headers
    )
    
    if admin_access_user.status_code == 404:
        print(f"✓ Admin correctly cannot access user's session (404)")
    else:
        print(f"⚠️ Admin incorrectly accessed user's session: {admin_access_user.status_code}")
        print(admin_access_user.text)
    
    # Test 5: List sessions for each user
    print("\nTest 5: Listing sessions for each user")
    
    # List admin sessions
    admin_sessions = requests.get(
        f"{base_url}/intake/sessions",
        headers=admin_headers
    )
    
    if admin_sessions.status_code != 200:
        print(f"Error listing admin sessions: {admin_sessions.status_code}")
        print(admin_sessions.text)
    else:
        sessions = admin_sessions.json().get("sessions", [])
        print(f"✓ Admin has {len(sessions)} sessions")
        for session in sessions:
            print(f"  - {session.get('session_id')}: {session.get('title')}")
    
    # List user sessions
    user_sessions = requests.get(
        f"{base_url}/intake/sessions",
        headers=user_headers
    )
    
    if user_sessions.status_code != 200:
        print(f"Error listing user sessions: {user_sessions.status_code}")
        print(user_sessions.text)
    else:
        sessions = user_sessions.json().get("sessions", [])
        print(f"✓ User has {len(sessions)} sessions")
        for session in sessions:
            print(f"  - {session.get('session_id')}: {session.get('title')}")
    
    # Test 6: Delete sessions
    print("\nTest 6: Deleting sessions")
    
    # Delete admin session
    admin_delete = requests.delete(
        f"{base_url}/intake/sessions/{admin_session_id}",
        headers=admin_headers
    )
    
    if admin_delete.status_code != 200:
        print(f"Error deleting admin session: {admin_delete.status_code}")
        print(admin_delete.text)
    else:
        print(f"✓ Admin session deleted successfully")
    
    # Delete user session
    user_delete = requests.delete(
        f"{base_url}/intake/sessions/{user_session_id}",
        headers=user_headers
    )
    
    if user_delete.status_code != 200:
        print(f"Error deleting user session: {user_delete.status_code}")
        print(user_delete.text)
    else:
        print(f"✓ User session deleted successfully")
    
    print("\n=== Authentication and User-Specific Sessions Test Complete ===")

if __name__ == "__main__":
    test_auth_and_sessions() 