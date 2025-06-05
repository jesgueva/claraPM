#!/usr/bin/env python3
"""
Test script to verify that session IDs and conversation state are maintained across multiple queries.
"""

import os
import sys
import requests
import json
import time

# Add the parent directory to the path so we can import the intake_agent module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_session_continuity():
    """Test that session IDs and conversation state are maintained across multiple queries."""
    base_url = "http://localhost:8000"  # Adjust if your API runs on a different port
    
    print("\n=== Testing Session Continuity ===\n")
    
    # Test 1: New session (no session_id provided)
    print("Test 1: Starting a new conversation (no session_id provided)")
    response1 = requests.post(
        f"{base_url}/query",
        json={"input_text": "Hello, I'm starting a new conversation."}
    )
    
    if response1.status_code == 200:
        result1 = response1.json()
        session_id = result1.get("session_id")
        messages = result1.get("messages", [])
        print(f"Response: {result1.get('response')}")
        print(f"Session ID: {session_id}")
        print(f"Messages count: {len(messages)}")
        
        # Verify we have at least 2 messages (user + assistant)
        if len(messages) >= 2:
            print("✓ Messages correctly stored in the first response")
        else:
            print(f"⚠️ Expected at least 2 messages, got {len(messages)}")
    else:
        print(f"Error: {response1.status_code}")
        print(response1.text)
        return
    
    # Test 2: Continue with the same session
    print("\nTest 2: Continuing the conversation (using the same session_id)")
    response2 = requests.post(
        f"{base_url}/query",
        json={
            "input_text": "This is a follow-up question in the same conversation.",
            "session_id": session_id
        }
    )
    
    if response2.status_code == 200:
        result2 = response2.json()
        continued_session_id = result2.get("session_id")
        messages = result2.get("messages", [])
        print(f"Response: {result2.get('response')}")
        print(f"Session ID: {continued_session_id}")
        print(f"Messages count: {len(messages)}")
        
        if continued_session_id == session_id:
            print("✓ Session ID was maintained across queries")
        else:
            print(f"⚠️ Error: Session ID changed from {session_id} to {continued_session_id}")
        
        # Verify we have at least 4 messages now (2 user + 2 assistant)
        if len(messages) >= 4:
            print("✓ Conversation history was preserved")
            # Verify the first message is still there
            if messages[0].get("content") == "Hello, I'm starting a new conversation.":
                print("✓ Initial message was preserved in conversation history")
            else:
                print("⚠️ Initial message was not preserved in conversation history")
        else:
            print(f"⚠️ Expected at least 4 messages, got {len(messages)}")
    else:
        print(f"Error: {response2.status_code}")
        print(response2.text)
        return
    
    # Test 3: Retrieve session using GET endpoint
    print("\nTest 3: Retrieving session using GET endpoint")
    response3 = requests.get(f"{base_url}/sessions/{session_id}")
    
    if response3.status_code == 200:
        result3 = response3.json()
        retrieved_messages = result3.get("messages", [])
        print(f"Retrieved messages count: {len(retrieved_messages)}")
        
        if len(retrieved_messages) == len(messages):
            print("✓ Successfully retrieved the full conversation history")
        else:
            print(f"⚠️ Retrieved message count ({len(retrieved_messages)}) doesn't match expected ({len(messages)})")
    else:
        print(f"Error: {response3.status_code}")
        print(response3.text)
    
    # Test 4: Force a new conversation
    print("\nTest 4: Forcing a new conversation (with new_conversation=True)")
    response4 = requests.post(
        f"{base_url}/query",
        json={
            "input_text": "I want to start a new conversation.",
            "session_id": session_id,
            "new_conversation": True
        }
    )
    
    if response4.status_code == 200:
        result4 = response4.json()
        new_session_id = result4.get("session_id")
        new_messages = result4.get("messages", [])
        print(f"Response: {result4.get('response')}")
        print(f"New Session ID: {new_session_id}")
        print(f"Messages count: {len(new_messages)}")
        
        if new_session_id != session_id:
            print("✓ New session ID was generated when requested")
        else:
            print("⚠️ Session ID was not changed despite new_conversation=True")
        
        # Verify we have exactly 2 messages (new conversation)
        if len(new_messages) == 2:
            print("✓ New conversation started with clean history")
        else:
            print(f"⚠️ Expected 2 messages in new conversation, got {len(new_messages)}")
    else:
        print(f"Error: {response4.status_code}")
        print(response4.text)
    
    # Test 5: Delete a session
    print("\nTest 5: Deleting a session")
    response5 = requests.delete(f"{base_url}/sessions/{session_id}")
    
    if response5.status_code == 200:
        result5 = response5.json()
        print(f"Delete response: {result5}")
        
        # Verify the session is really gone
        response6 = requests.get(f"{base_url}/sessions/{session_id}")
        if response6.status_code == 200 and "error" in response6.json():
            print("✓ Session was successfully deleted")
        else:
            print("⚠️ Session was not deleted properly")
    else:
        print(f"Error: {response5.status_code}")
        print(response5.text)
    
    print("\n=== Session Continuity Test Complete ===")

if __name__ == "__main__":
    test_session_continuity() 