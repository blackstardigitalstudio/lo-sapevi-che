"""Backend API tests for Lo Sapevi che.

Tests:
- Health check
- Auth (register, login, me, update interests)
- Categories
- Feed (personalized)
- Reactions (like, dislike)
- Bookmarks
- Fact detail
- AI generation
"""
import pytest
import requests
import os
import time
import uuid
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

class TestHealth:
    """Health and basic connectivity tests."""

    def test_health_endpoint(self, api_client):
        """Test /api/health returns ok and counts."""
        response = api_client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "facts" in data
        assert "users" in data
        assert data["facts"] > 0, "No facts seeded"
        print(f"✓ Health check passed: {data['facts']} facts, {data['users']} users")

    def test_root_endpoint(self, api_client):
        """Test /api/ returns app info."""
        response = api_client.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "app" in data
        assert data["status"] == "ok"
        print(f"✓ Root endpoint: {data['app']}")


class TestAuth:
    """Authentication flow tests."""

    def test_register_new_user(self, api_client):
        """Test POST /api/auth/register creates user and returns token."""
        unique_email = f"TEST_user_{uuid.uuid4().hex[:8]}@test.com"
        payload = {
            "email": unique_email,
            "password": "test123",
            "name": "Test User New",
            "interests": ["Scienza", "Spazio"]
        }
        response = api_client.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response.status_code == 200, f"Register failed: {response.text}"
        
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == unique_email.lower()
        assert data["user"]["name"] == payload["name"]
        assert set(data["user"]["interests"]) == set(payload["interests"])
        assert "interest_weights" in data["user"]
        assert data["user"]["interest_weights"]["Scienza"] == 1.0
        assert data["user"]["interest_weights"]["Cucina"] == 0.3
        print(f"✓ Register successful: {data['user']['email']}")

    def test_register_duplicate_email(self, api_client):
        """Test registering with existing email returns 400."""
        response = api_client.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": "test@test.com",
                "password": "test123",
                "name": "Duplicate",
                "interests": []
            }
        )
        assert response.status_code == 400
        assert "già registrata" in response.text.lower()
        print("✓ Duplicate email rejected")

    def test_login_success(self, api_client):
        """Test POST /api/auth/login with valid credentials."""
        response = api_client.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "test@test.com", "password": "test123"}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == "test@test.com"
        print(f"✓ Login successful: {data['user']['name']}")

    def test_login_invalid_credentials(self, api_client):
        """Test login with wrong password returns 401."""
        response = api_client.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "test@test.com", "password": "wrongpass"}
        )
        assert response.status_code == 401
        assert "non valide" in response.text.lower()
        print("✓ Invalid credentials rejected")

    def test_me_endpoint(self, api_client, test_user_token):
        """Test GET /api/auth/me returns current user with stats."""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = api_client.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert response.status_code == 200, f"Me endpoint failed: {response.text}"
        
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "name" in data
        assert "interests" in data
        assert "interest_weights" in data
        assert "stats" in data
        assert "liked" in data["stats"]
        assert "disliked" in data["stats"]
        assert "bookmarked" in data["stats"]
        assert "seen" in data["stats"]
        print(f"✓ Me endpoint: {data['name']}, stats: {data['stats']}")

    def test_me_without_token(self, api_client):
        """Test /api/auth/me without token returns 401."""
        response = api_client.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401
        print("✓ Unauthorized access rejected")

    def test_update_interests(self, api_client, test_user_token):
        """Test POST /api/auth/interests updates user interests and weights."""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        new_interests = ["Tecnologia", "Arte", "Musica"]
        response = api_client.post(
            f"{BASE_URL}/api/auth/interests",
            json={"interests": new_interests},
            headers=headers
        )
        assert response.status_code == 200, f"Update interests failed: {response.text}"
        
        data = response.json()
        assert set(data["interests"]) == set(new_interests)
        assert data["interest_weights"]["Tecnologia"] >= 1.0
        assert data["interest_weights"]["Arte"] >= 1.0
        print(f"✓ Interests updated: {data['interests']}")


class TestCategories:
    """Category listing tests."""

    def test_get_categories(self, api_client):
        """Test GET /api/categories returns 20 Italian niches."""
        response = api_client.get(f"{BASE_URL}/api/categories")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 20, f"Expected 20 categories, got {len(data)}"
        
        for cat in data:
            assert "name" in cat
            assert "icon" in cat
        
        category_names = [c["name"] for c in data]
        assert "Scienza" in category_names
        assert "Storia" in category_names
        assert "Spazio" in category_names
        print(f"✓ Categories: {len(data)} niches loaded")


class TestFeed:
    """Feed and personalization tests."""

    def test_get_feed(self, api_client, test_user_token):
        """Test GET /api/feed returns personalized facts."""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = api_client.get(f"{BASE_URL}/api/feed?limit=5", headers=headers)
        assert response.status_code == 200, f"Feed failed: {response.text}"
        
        data = response.json()
        assert "facts" in data
        assert isinstance(data["facts"], list)
        assert len(data["facts"]) > 0, "Feed is empty"
        
        fact = data["facts"][0]
        assert "id" in fact
        assert "title" in fact
        assert "short_fact" in fact
        assert "deep_dive" in fact
        assert "category" in fact
        assert "image_url" in fact
        assert "source" in fact
        print(f"✓ Feed loaded: {len(data['facts'])} facts")

    def test_feed_without_auth(self, api_client):
        """Test feed requires authentication."""
        response = api_client.get(f"{BASE_URL}/api/feed")
        assert response.status_code == 401
        print("✓ Feed requires auth")


class TestReactions:
    """Like/dislike reaction tests."""

    def test_like_fact(self, api_client, test_user_token):
        """Test POST /api/facts/{id}/react with action=like."""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Get a fact from feed
        feed_resp = api_client.get(f"{BASE_URL}/api/feed?limit=1", headers=headers)
        assert feed_resp.status_code == 200
        facts = feed_resp.json()["facts"]
        if not facts:
            pytest.skip("No facts available")
        
        fact_id = facts[0]["id"]
        category = facts[0]["category"]
        
        # Like the fact
        response = api_client.post(
            f"{BASE_URL}/api/facts/{fact_id}/react",
            json={"action": "like"},
            headers=headers
        )
        assert response.status_code == 200, f"Like failed: {response.text}"
        
        data = response.json()
        assert data["ok"] is True
        assert "new_weight" in data
        assert data["new_weight"] > 0
        print(f"✓ Like successful: {category} weight = {data['new_weight']}")
        
        # Verify user stats updated
        me_resp = api_client.get(f"{BASE_URL}/api/auth/me", headers=headers)
        me_data = me_resp.json()
        assert me_data["stats"]["liked"] > 0
        print(f"✓ User stats updated: {me_data['stats']['liked']} liked")

    def test_dislike_fact(self, api_client, test_user_token):
        """Test POST /api/facts/{id}/react with action=dislike."""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Get a fact
        feed_resp = api_client.get(f"{BASE_URL}/api/feed?limit=1", headers=headers)
        facts = feed_resp.json()["facts"]
        if not facts:
            pytest.skip("No facts available")
        
        fact_id = facts[0]["id"]
        category = facts[0]["category"]
        
        # Dislike the fact
        response = api_client.post(
            f"{BASE_URL}/api/facts/{fact_id}/react",
            json={"action": "dislike"},
            headers=headers
        )
        assert response.status_code == 200, f"Dislike failed: {response.text}"
        
        data = response.json()
        assert data["ok"] is True
        assert "new_weight" in data
        print(f"✓ Dislike successful: {category} weight = {data['new_weight']}")

    def test_react_invalid_action(self, api_client, test_user_token):
        """Test react with invalid action returns 400."""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        feed_resp = api_client.get(f"{BASE_URL}/api/feed?limit=1", headers=headers)
        facts = feed_resp.json()["facts"]
        if not facts:
            pytest.skip("No facts available")
        
        fact_id = facts[0]["id"]
        response = api_client.post(
            f"{BASE_URL}/api/facts/{fact_id}/react",
            json={"action": "invalid"},
            headers=headers
        )
        assert response.status_code == 400
        print("✓ Invalid action rejected")


class TestBookmarks:
    """Bookmark functionality tests."""

    def test_bookmark_toggle(self, api_client, test_user_token):
        """Test POST /api/facts/{id}/bookmark toggles bookmark."""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Get a fact
        feed_resp = api_client.get(f"{BASE_URL}/api/feed?limit=1", headers=headers)
        facts = feed_resp.json()["facts"]
        if not facts:
            pytest.skip("No facts available")
        
        fact_id = facts[0]["id"]
        
        # Bookmark it
        response = api_client.post(
            f"{BASE_URL}/api/facts/{fact_id}/bookmark",
            headers=headers
        )
        assert response.status_code == 200, f"Bookmark failed: {response.text}"
        
        data = response.json()
        assert data["ok"] is True
        assert "bookmarked" in data
        is_bookmarked = data["bookmarked"]
        print(f"✓ Bookmark toggled: {is_bookmarked}")
        
        # Toggle again
        response2 = api_client.post(
            f"{BASE_URL}/api/facts/{fact_id}/bookmark",
            headers=headers
        )
        data2 = response2.json()
        assert data2["bookmarked"] != is_bookmarked
        print(f"✓ Bookmark toggled again: {data2['bookmarked']}")

    def test_get_bookmarks(self, api_client, test_user_token):
        """Test GET /api/facts/bookmarks returns saved facts."""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = api_client.get(f"{BASE_URL}/api/facts/bookmarks", headers=headers)
        assert response.status_code == 200, f"Get bookmarks failed: {response.text}"
        
        data = response.json()
        assert "facts" in data
        assert isinstance(data["facts"], list)
        print(f"✓ Bookmarks retrieved: {len(data['facts'])} saved")


class TestFactDetail:
    """Individual fact detail tests."""

    def test_get_fact_by_id(self, api_client, test_user_token):
        """Test GET /api/facts/{id} returns fact with is_liked and is_bookmarked."""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Get a fact ID from feed
        feed_resp = api_client.get(f"{BASE_URL}/api/feed?limit=1", headers=headers)
        facts = feed_resp.json()["facts"]
        if not facts:
            pytest.skip("No facts available")
        
        fact_id = facts[0]["id"]
        
        # Get fact detail
        response = api_client.get(f"{BASE_URL}/api/facts/{fact_id}", headers=headers)
        assert response.status_code == 200, f"Get fact failed: {response.text}"
        
        data = response.json()
        assert data["id"] == fact_id
        assert "title" in data
        assert "short_fact" in data
        assert "deep_dive" in data
        assert "category" in data
        assert "is_liked" in data
        assert "is_bookmarked" in data
        assert isinstance(data["is_liked"], bool)
        assert isinstance(data["is_bookmarked"], bool)
        print(f"✓ Fact detail: {data['title'][:50]}...")

    def test_get_nonexistent_fact(self, api_client, test_user_token):
        """Test getting non-existent fact returns 404."""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = api_client.get(
            f"{BASE_URL}/api/facts/nonexistent-id-12345",
            headers=headers
        )
        assert response.status_code == 404
        print("✓ Non-existent fact returns 404")


class TestAIGeneration:
    """AI fact generation tests (may be slow)."""

    def test_generate_fact(self, api_client, test_user_token):
        """Test POST /api/facts/generate creates AI fact (slow ~10s)."""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        print("⏳ Generating AI fact (may take ~10s)...")
        start = time.time()
        
        response = api_client.post(
            f"{BASE_URL}/api/facts/generate",
            json={"category": "Scienza"},
            headers=headers,
            timeout=30
        )
        
        elapsed = time.time() - start
        
        if response.status_code == 503:
            print(f"⚠ AI generation unavailable (503): {response.text}")
            pytest.skip("AI generation service unavailable")
        
        assert response.status_code == 200, f"Generate failed: {response.text}"
        
        data = response.json()
        assert "id" in data
        assert "title" in data
        assert "short_fact" in data
        assert "deep_dive" in data
        assert data["category"] == "Scienza"
        assert data["source"] == "ai"
        print(f"✓ AI fact generated in {elapsed:.1f}s: {data['title'][:60]}...")
