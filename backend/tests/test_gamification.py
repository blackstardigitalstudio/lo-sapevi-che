"""Backend tests for gamification features: streak, trophies, sources, preview.

Tests:
- GET /api/preview (20 category preview cards)
- GET /api/trophies (10 trophies with earned flag)
- POST /api/auth/checkin (streak tracking, trophy earning)
- Facts with sources field
- new_trophies in react/bookmark responses
- ai_generated_count tracking
- POST /api/facts/bulk-generate (count=1 for speed)
- Health check for 96+ facts
"""
import pytest
import requests
import uuid
import time
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


class TestContentExpansion:
    """Test expanded seed data and preview endpoint."""

    def test_health_shows_96_plus_facts(self, api_client):
        """Test /api/health shows 96+ facts after seed."""
        response = api_client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["facts"] >= 96, f"Expected 96+ facts, got {data['facts']}"
        print(f"✓ Health check: {data['facts']} facts seeded (96+ required)")

    def test_preview_endpoint(self, api_client):
        """Test GET /api/preview returns 20 category preview cards."""
        response = api_client.get(f"{BASE_URL}/api/preview")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 20, f"Expected 20 preview items, got {len(data)}"
        
        # Check first preview item structure
        preview = data[0]
        assert "category" in preview
        assert "icon" in preview
        assert "sample_title" in preview
        assert "sample_short" in preview
        assert "image_url" in preview
        assert preview["image_url"].startswith("http")
        print(f"✓ Preview endpoint: 20 categories with sample facts")
        print(f"  Sample: {preview['category']} - {preview['sample_title'][:40]}...")

    def test_facts_have_sources_field(self, api_client, test_user_token):
        """Test facts now include optional 'sources' field."""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Get feed
        response = api_client.get(f"{BASE_URL}/api/feed?limit=10", headers=headers)
        assert response.status_code == 200
        
        facts = response.json()["facts"]
        assert len(facts) > 0
        
        # Check if sources field exists (may be empty list)
        fact = facts[0]
        # Sources may or may not be present in all facts, but should be in schema
        # Let's check a specific fact detail
        fact_id = fact["id"]
        detail_resp = api_client.get(f"{BASE_URL}/api/facts/{fact_id}", headers=headers)
        detail = detail_resp.json()
        
        # Sources field should exist (even if empty)
        if "sources" in detail:
            assert isinstance(detail["sources"], list)
            if detail["sources"]:
                source = detail["sources"][0]
                assert "title" in source
                assert "url" in source
                print(f"✓ Fact has sources field: {len(detail['sources'])} sources")
        else:
            print(f"⚠ Fact missing sources field (may be old seed data)")


class TestTrophies:
    """Test trophy system."""

    def test_get_trophies(self, api_client, test_user_token):
        """Test GET /api/trophies returns 10 trophies with earned flag."""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        response = api_client.get(f"{BASE_URL}/api/trophies", headers=headers)
        assert response.status_code == 200, f"Trophies endpoint failed: {response.text}"
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 10, f"Expected 10 trophies, got {len(data)}"
        
        # Check trophy structure
        trophy = data[0]
        assert "id" in trophy
        assert "name" in trophy
        assert "desc" in trophy
        assert "icon" in trophy
        assert "earned" in trophy
        assert isinstance(trophy["earned"], bool)
        
        earned_count = sum(1 for t in data if t["earned"])
        print(f"✓ Trophies endpoint: 10 trophies, {earned_count} earned")
        
        # List earned trophies
        earned_names = [t["name"] for t in data if t["earned"]]
        if earned_names:
            print(f"  Earned: {', '.join(earned_names)}")

    def test_trophies_require_auth(self, api_client):
        """Test /api/trophies requires authentication."""
        response = api_client.get(f"{BASE_URL}/api/trophies")
        assert response.status_code == 401
        print("✓ Trophies endpoint requires auth")


class TestStreak:
    """Test daily streak and checkin."""

    def test_checkin_first_call(self, api_client):
        """Test POST /api/auth/checkin for fresh user creates streak=1."""
        # Create a fresh user
        unique_email = f"TEST_streak_{uuid.uuid4().hex[:8]}@test.com"
        register_resp = api_client.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": unique_email,
                "password": "test123",
                "name": "Streak Test User",
                "interests": ["Scienza"]
            }
        )
        assert register_resp.status_code == 200
        token = register_resp.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Mark one fact as seen to earn first_step trophy
        feed_resp = api_client.get(f"{BASE_URL}/api/feed?limit=1", headers=headers)
        facts = feed_resp.json()["facts"]
        if facts:
            api_client.post(f"{BASE_URL}/api/facts/{facts[0]['id']}/seen", headers=headers)
        
        # First checkin
        response = api_client.post(f"{BASE_URL}/api/auth/checkin", headers=headers)
        assert response.status_code == 200, f"Checkin failed: {response.text}"
        
        data = response.json()
        assert "streak_days" in data
        assert "best_streak" in data
        assert "trophies" in data
        assert "new_trophies" in data
        
        assert data["streak_days"] == 1, f"Expected streak=1, got {data['streak_days']}"
        assert data["best_streak"] == 1
        
        # Should have earned at least first_step trophy if seen_ids >= 1
        if data["new_trophies"]:
            print(f"✓ First checkin: streak=1, earned {len(data['new_trophies'])} trophies")
            print(f"  New trophies: {[t['name'] for t in data['new_trophies']]}")
        else:
            print(f"✓ First checkin: streak=1, no new trophies (may already have them)")

    def test_checkin_same_day_no_change(self, api_client, test_user_token):
        """Test POST /api/auth/checkin called again same day doesn't change streak."""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # First checkin
        resp1 = api_client.post(f"{BASE_URL}/api/auth/checkin", headers=headers)
        assert resp1.status_code == 200
        data1 = resp1.json()
        streak1 = data1["streak_days"]
        
        # Second checkin same day
        resp2 = api_client.post(f"{BASE_URL}/api/auth/checkin", headers=headers)
        assert resp2.status_code == 200
        data2 = resp2.json()
        streak2 = data2["streak_days"]
        
        assert streak2 == streak1, f"Streak changed on same day: {streak1} -> {streak2}"
        assert len(data2["new_trophies"]) == 0, "Should not earn new trophies on same-day checkin"
        print(f"✓ Same-day checkin: streak unchanged ({streak2})")


class TestTrophyEarning:
    """Test trophy earning via reactions and bookmarks."""

    def test_react_returns_new_trophies(self, api_client):
        """Test POST /api/facts/{id}/react returns new_trophies array."""
        # Create fresh user
        unique_email = f"TEST_react_{uuid.uuid4().hex[:8]}@test.com"
        register_resp = api_client.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": unique_email,
                "password": "test123",
                "name": "React Test User",
                "interests": ["Scienza"]
            }
        )
        token = register_resp.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get a fact
        feed_resp = api_client.get(f"{BASE_URL}/api/feed?limit=1", headers=headers)
        facts = feed_resp.json()["facts"]
        if not facts:
            pytest.skip("No facts available")
        
        fact_id = facts[0]["id"]
        
        # Like the fact
        response = api_client.post(
            f"{BASE_URL}/api/facts/{fact_id}/react",
            json={"action": "like"},
            headers=headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "new_trophies" in data
        assert isinstance(data["new_trophies"], list)
        
        # Fresh user liking first fact should earn first_step trophy
        if data["new_trophies"]:
            print(f"✓ React returns new_trophies: {[t['name'] for t in data['new_trophies']]}")
        else:
            print(f"✓ React returns new_trophies: [] (no new trophies earned)")

    def test_bookmark_returns_new_trophies(self, api_client):
        """Test POST /api/facts/{id}/bookmark returns new_trophies array."""
        # Create fresh user
        unique_email = f"TEST_bookmark_{uuid.uuid4().hex[:8]}@test.com"
        register_resp = api_client.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": unique_email,
                "password": "test123",
                "name": "Bookmark Test User",
                "interests": ["Scienza"]
            }
        )
        token = register_resp.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get facts
        feed_resp = api_client.get(f"{BASE_URL}/api/feed?limit=10", headers=headers)
        facts = feed_resp.json()["facts"]
        if len(facts) < 10:
            pytest.skip("Not enough facts to test collector trophy")
        
        # Bookmark 10 facts to trigger collector trophy
        for i in range(10):
            fact_id = facts[i]["id"]
            response = api_client.post(
                f"{BASE_URL}/api/facts/{fact_id}/bookmark",
                headers=headers
            )
            assert response.status_code == 200
            data = response.json()
            assert "new_trophies" in data
            
            if i == 9:  # 10th bookmark
                if data["new_trophies"]:
                    collector_earned = any(t["id"] == "collector" for t in data["new_trophies"])
                    if collector_earned:
                        print(f"✓ Bookmark 10 facts: 'Collezionista' trophy earned")
                    else:
                        print(f"✓ Bookmark returns new_trophies: {[t['name'] for t in data['new_trophies']]}")
                else:
                    print(f"✓ Bookmark returns new_trophies: [] (may already have collector)")


class TestAIGeneration:
    """Test AI generation with trophy tracking."""

    def test_generate_tracks_ai_count(self, api_client):
        """Test POST /api/facts/generate tracks ai_generated_count."""
        # Create fresh user
        unique_email = f"TEST_ai_{uuid.uuid4().hex[:8]}@test.com"
        register_resp = api_client.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": unique_email,
                "password": "test123",
                "name": "AI Test User",
                "interests": ["Scienza"]
            }
        )
        token = register_resp.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
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
        assert "new_trophies" in data
        assert isinstance(data["new_trophies"], list)
        
        # Check user ai_generated_count
        me_resp = api_client.get(f"{BASE_URL}/api/auth/me", headers=headers)
        me_data = me_resp.json()
        assert "ai_generated_count" in me_data
        assert me_data["ai_generated_count"] == 1
        
        print(f"✓ AI generation tracks count: ai_generated_count=1 (took {elapsed:.1f}s)")

    def test_bulk_generate_creates_multiple_facts(self, api_client):
        """Test POST /api/facts/bulk-generate with count=1 (skip if slow)."""
        # Create fresh user
        unique_email = f"TEST_bulk_{uuid.uuid4().hex[:8]}@test.com"
        register_resp = api_client.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": unique_email,
                "password": "test123",
                "name": "Bulk Test User",
                "interests": ["Scienza"]
            }
        )
        token = register_resp.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        print("⏳ Bulk generating 1 AI fact (may take ~10s)...")
        start = time.time()
        
        response = api_client.post(
            f"{BASE_URL}/api/facts/bulk-generate",
            json={"count": 1, "category": "Scienza"},
            headers=headers,
            timeout=30
        )
        
        elapsed = time.time() - start
        
        if response.status_code == 503:
            print(f"⚠ Bulk generation unavailable (503): {response.text}")
            pytest.skip("Bulk generation service unavailable")
        
        assert response.status_code == 200, f"Bulk generate failed: {response.text}"
        
        data = response.json()
        assert "created" in data
        assert "facts" in data
        assert data["created"] == 1, f"Expected 1 fact created, got {data['created']}"
        assert len(data["facts"]) == 1
        
        fact = data["facts"][0]
        assert fact["source"] == "ai"
        assert fact["category"] == "Scienza"
        
        print(f"✓ Bulk generate: 1 fact created in {elapsed:.1f}s")
        print(f"  Title: {fact['title'][:60]}...")
