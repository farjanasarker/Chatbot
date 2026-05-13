#!/usr/bin/env python3
"""
Test script for the chatbot API
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_chatbot():
    print("Testing chatbot API...")

    # Create a session-enabled client
    client = requests.Session()

    # First, signup a test user
    try:
        signup_data = {"username": "testuser", "password": "testpass"}
        response = client.post(f"{BASE_URL}/api/signup", json=signup_data)
        print(f"Signup response: {response.status_code} - {response.text}")
        if response.status_code != 200:
            print("Signup failed, trying login...")
            # Try login instead
            login_data = {"username": "testuser", "password": "testpass"}
            response = client.post(f"{BASE_URL}/api/login", json=login_data)
            print(f"Login response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error with auth: {e}")
        return

    # Create a session
    try:
        response = client.post(f"{BASE_URL}/api/sessions", json={})
        if response.status_code == 200:
            data = response.json()
            session_id = data["session_id"]
            print(f"Created session: {session_id}")
        else:
            print(f"Failed to create session: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"Error creating session: {e}")
        return

    # Now send a chat message
    try:
        chat_data = {"message": "Hello, how are you?"}
        response = client.post(f"{BASE_URL}/api/sessions/{session_id}/chat", json=chat_data)
        if response.status_code == 200:
            data = response.json()
            reply = data["reply"]
            print(f"Chatbot reply: {reply}")
            print("✅ Local LLM integration successful!")
        else:
            print(f"Failed to chat: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error chatting: {e}")

if __name__ == "__main__":
    test_chatbot()