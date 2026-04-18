"""Shared pytest fixtures for Lo Sapevi che backend tests."""
import pytest
import requests
import os
from pathlib import Path

# Read EXPO_PUBLIC_BACKEND_URL from frontend .env
env_file = Path("/app/frontend/.env")
BASE_URL = None
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if line.startswith("EXPO_PUBLIC_BACKEND_URL="):
            BASE_URL = line.split("=", 1)[1].strip().strip('"')
            break

if not BASE_URL:
    raise ValueError("EXPO_PUBLIC_BACKEND_URL not found in /app/frontend/.env")

@pytest.fixture
def api_client():
    """Shared requests session."""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session

@pytest.fixture
def test_user_token(api_client):
    """Get or create test user and return token."""
    # Try login first
    try:
        resp = api_client.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "test@test.com", "password": "test123"}
        )
        if resp.status_code == 200:
            return resp.json()["token"]
    except:
        pass
    
    # Register new test user
    resp = api_client.post(
        f"{BASE_URL}/api/auth/register",
        json={
            "email": "test@test.com",
            "password": "test123",
            "name": "Test User",
            "interests": ["Scienza", "Spazio", "Storia"]
        }
    )
    if resp.status_code == 200:
        return resp.json()["token"]
    elif resp.status_code == 400 and "già registrata" in resp.text:
        # Already exists, try login again
        resp = api_client.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "test@test.com", "password": "test123"}
        )
        return resp.json()["token"]
    raise Exception(f"Failed to get test user token: {resp.status_code} {resp.text}")
