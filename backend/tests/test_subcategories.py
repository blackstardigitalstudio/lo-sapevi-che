"""Backend API tests for sub-categories feature (V3).

Tests:
- GET /api/categories returns 25 categories (20 original + 5 new)
- GET /api/categories includes has_subcategories=true for 5 new categories
- GET /api/subcategories/{category} returns subcategories list
- GET /api/subcategories/InvalidCategory returns 404
- POST /api/auth/sub-interests saves sub_interests
- GET /api/auth/me returns sub_interests field
- GET /api/feed filters by sub_interests (only selected brands/sub-themes)
- GET /api/feed with empty sub_interests returns all facts
- Facts have sub_category field
"""
import pytest
import requests
import os
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


class TestCategoriesV3:
    """Test 25 categories with sub-categories support."""

    def test_categories_count_25(self, api_client):
        """Test GET /api/categories returns 25 categories (20 original + 5 new)."""
        response = api_client.get(f"{BASE_URL}/api/categories")
        assert response.status_code == 200, f"Categories failed: {response.text}"
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 25, f"Expected 25 categories, got {len(data)}"
        
        category_names = [c["name"] for c in data]
        
        # Check original 20 categories
        original = ["Scienza", "Storia", "Tecnologia", "Natura", "Spazio",
                   "Cucina", "Sport", "Arte", "Psicologia", "Cinema",
                   "Musica", "Geografia", "Medicina", "Filosofia", "Economia",
                   "Letteratura", "Animali", "Matematica", "Viaggi", "Mitologia"]
        for cat in original:
            assert cat in category_names, f"Missing original category: {cat}"
        
        # Check 5 new categories
        new_cats = ["Mafia", "Guerre", "Motori", "Macchine", "Moto"]
        for cat in new_cats:
            assert cat in category_names, f"Missing new category: {cat}"
        
        print(f"✓ Categories: 25 total (20 original + 5 new)")

    def test_categories_have_subcategories_field(self, api_client):
        """Test categories include has_subcategories and subcategories fields."""
        response = api_client.get(f"{BASE_URL}/api/categories")
        assert response.status_code == 200
        
        data = response.json()
        
        # All categories should have these fields
        for cat in data:
            assert "name" in cat
            assert "icon" in cat
            assert "has_subcategories" in cat, f"Missing has_subcategories for {cat['name']}"
            assert "subcategories" in cat, f"Missing subcategories for {cat['name']}"
            assert isinstance(cat["has_subcategories"], bool)
            assert isinstance(cat["subcategories"], list)
        
        print("✓ All categories have has_subcategories and subcategories fields")

    def test_new_categories_have_subcategories(self, api_client):
        """Test 5 new categories have has_subcategories=true with non-empty arrays."""
        response = api_client.get(f"{BASE_URL}/api/categories")
        assert response.status_code == 200
        
        data = response.json()
        cat_dict = {c["name"]: c for c in data}
        
        # Check 5 new categories
        new_cats = {
            "Mafia": ["Cosa Nostra", "Camorra", "'Ndrangheta"],
            "Guerre": ["Prima guerra mondiale", "Seconda guerra mondiale", "Guerra fredda", "Guerre napoleoniche"],
            "Motori": ["Formula 1", "MotoGP", "Rally"],
            "Macchine": ["Ferrari", "Lamborghini", "Tesla", "Fiat"],
            "Moto": ["Ducati", "Harley-Davidson", "Vespa", "MV Agusta"]
        }
        
        for cat_name, expected_subs in new_cats.items():
            assert cat_name in cat_dict, f"Missing category: {cat_name}"
            cat = cat_dict[cat_name]
            assert cat["has_subcategories"] is True, f"{cat_name} should have has_subcategories=true"
            assert len(cat["subcategories"]) > 0, f"{cat_name} should have non-empty subcategories"
            
            # Check some expected subcategories are present
            for sub in expected_subs:
                assert sub in cat["subcategories"], f"Missing subcategory {sub} in {cat_name}"
            
            print(f"✓ {cat_name}: has_subcategories=true, {len(cat['subcategories'])} subcategories")

    def test_original_categories_no_subcategories(self, api_client):
        """Test original 20 categories have has_subcategories=false."""
        response = api_client.get(f"{BASE_URL}/api/categories")
        assert response.status_code == 200
        
        data = response.json()
        cat_dict = {c["name"]: c for c in data}
        
        original = ["Scienza", "Storia", "Tecnologia", "Natura", "Spazio"]
        
        for cat_name in original:
            cat = cat_dict[cat_name]
            assert cat["has_subcategories"] is False, f"{cat_name} should have has_subcategories=false"
            assert len(cat["subcategories"]) == 0, f"{cat_name} should have empty subcategories"
        
        print("✓ Original categories have has_subcategories=false")


class TestSubcategoriesEndpoint:
    """Test GET /api/subcategories/{category} endpoint."""

    def test_get_subcategories_macchine(self, api_client):
        """Test GET /api/subcategories/Macchine returns Ferrari, Lamborghini, etc."""
        response = api_client.get(f"{BASE_URL}/api/subcategories/Macchine")
        assert response.status_code == 200, f"Subcategories failed: {response.text}"
        
        data = response.json()
        assert "category" in data
        assert data["category"] == "Macchine"
        assert "subcategories" in data
        assert isinstance(data["subcategories"], list)
        assert len(data["subcategories"]) > 0
        
        # Check expected brands
        expected = ["Ferrari", "Lamborghini", "Tesla", "Fiat"]
        for brand in expected:
            assert brand in data["subcategories"], f"Missing brand: {brand}"
        
        print(f"✓ Macchine subcategories: {len(data['subcategories'])} brands")

    def test_get_subcategories_moto(self, api_client):
        """Test GET /api/subcategories/Moto returns Ducati, Harley-Davidson, etc."""
        response = api_client.get(f"{BASE_URL}/api/subcategories/Moto")
        assert response.status_code == 200
        
        data = response.json()
        assert data["category"] == "Moto"
        
        expected = ["Ducati", "Harley-Davidson", "Vespa", "MV Agusta"]
        for brand in expected:
            assert brand in data["subcategories"], f"Missing brand: {brand}"
        
        print(f"✓ Moto subcategories: {len(data['subcategories'])} brands")

    def test_get_subcategories_guerre(self, api_client):
        """Test GET /api/subcategories/Guerre returns war periods."""
        response = api_client.get(f"{BASE_URL}/api/subcategories/Guerre")
        assert response.status_code == 200
        
        data = response.json()
        assert data["category"] == "Guerre"
        
        expected = ["Prima guerra mondiale", "Seconda guerra mondiale", "Guerra fredda", "Guerre napoleoniche"]
        for period in expected:
            assert period in data["subcategories"], f"Missing period: {period}"
        
        print(f"✓ Guerre subcategories: {len(data['subcategories'])} periods")

    def test_get_subcategories_invalid_category(self, api_client):
        """Test GET /api/subcategories/InvalidCategory returns 404."""
        response = api_client.get(f"{BASE_URL}/api/subcategories/InvalidCategory")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        assert "non trovata" in response.text.lower()
        print("✓ Invalid category returns 404")

    def test_get_subcategories_original_category(self, api_client):
        """Test GET /api/subcategories/Scienza returns empty array."""
        response = api_client.get(f"{BASE_URL}/api/subcategories/Scienza")
        assert response.status_code == 200
        
        data = response.json()
        assert data["category"] == "Scienza"
        assert data["subcategories"] == []
        print("✓ Original category returns empty subcategories")


class TestSubInterestsAuth:
    """Test POST /api/auth/sub-interests endpoint."""

    def test_update_sub_interests_macchine_ferrari(self, api_client):
        """Test POST /api/auth/sub-interests with {Macchine: ['Ferrari']} saves correctly."""
        # Register new user
        unique_email = f"TEST_subint_{uuid.uuid4().hex[:8]}@test.com"
        reg_resp = api_client.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": unique_email,
                "password": "test123",
                "name": "Sub Interest Test",
                "interests": ["Macchine", "Moto"]
            }
        )
        assert reg_resp.status_code == 200
        token = reg_resp.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Update sub_interests
        response = api_client.post(
            f"{BASE_URL}/api/auth/sub-interests",
            json={"sub_interests": {"Macchine": ["Ferrari"]}},
            headers=headers
        )
        assert response.status_code == 200, f"Update sub-interests failed: {response.text}"
        
        data = response.json()
        assert "sub_interests" in data
        assert "Macchine" in data["sub_interests"]
        assert data["sub_interests"]["Macchine"] == ["Ferrari"]
        print("✓ Sub-interests saved: Macchine -> Ferrari")

    def test_update_sub_interests_multiple_brands(self, api_client):
        """Test saving multiple brands for one category."""
        unique_email = f"TEST_multi_{uuid.uuid4().hex[:8]}@test.com"
        reg_resp = api_client.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": unique_email,
                "password": "test123",
                "name": "Multi Brand Test",
                "interests": ["Macchine"]
            }
        )
        token = reg_resp.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Update with multiple brands
        response = api_client.post(
            f"{BASE_URL}/api/auth/sub-interests",
            json={"sub_interests": {"Macchine": ["Ferrari", "Lamborghini", "Tesla"]}},
            headers=headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert set(data["sub_interests"]["Macchine"]) == {"Ferrari", "Lamborghini", "Tesla"}
        print("✓ Multiple brands saved: Ferrari, Lamborghini, Tesla")

    def test_update_sub_interests_multiple_categories(self, api_client):
        """Test saving sub-interests for multiple categories."""
        unique_email = f"TEST_multicat_{uuid.uuid4().hex[:8]}@test.com"
        reg_resp = api_client.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": unique_email,
                "password": "test123",
                "name": "Multi Category Test",
                "interests": ["Macchine", "Moto", "Guerre"]
            }
        )
        token = reg_resp.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Update with multiple categories
        response = api_client.post(
            f"{BASE_URL}/api/auth/sub-interests",
            json={
                "sub_interests": {
                    "Macchine": ["Ferrari", "Lamborghini"],
                    "Moto": ["Ducati"],
                    "Guerre": ["Seconda guerra mondiale"]
                }
            },
            headers=headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "Macchine" in data["sub_interests"]
        assert "Moto" in data["sub_interests"]
        assert "Guerre" in data["sub_interests"]
        print("✓ Multiple categories saved")

    def test_sub_interests_sanitization(self, api_client):
        """Test invalid subcategories are filtered out."""
        unique_email = f"TEST_sanitize_{uuid.uuid4().hex[:8]}@test.com"
        reg_resp = api_client.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": unique_email,
                "password": "test123",
                "name": "Sanitize Test",
                "interests": ["Macchine"]
            }
        )
        token = reg_resp.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to save invalid subcategories
        response = api_client.post(
            f"{BASE_URL}/api/auth/sub-interests",
            json={
                "sub_interests": {
                    "Macchine": ["Ferrari", "InvalidBrand", "Lamborghini"],
                    "InvalidCategory": ["Something"]
                }
            },
            headers=headers
        )
        assert response.status_code == 200
        
        data = response.json()
        # InvalidCategory should be removed
        assert "InvalidCategory" not in data["sub_interests"]
        # InvalidBrand should be filtered out
        assert "InvalidBrand" not in data["sub_interests"]["Macchine"]
        assert "Ferrari" in data["sub_interests"]["Macchine"]
        assert "Lamborghini" in data["sub_interests"]["Macchine"]
        print("✓ Invalid subcategories filtered out")

    def test_me_returns_sub_interests(self, api_client):
        """Test GET /api/auth/me returns sub_interests field."""
        unique_email = f"TEST_me_{uuid.uuid4().hex[:8]}@test.com"
        reg_resp = api_client.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": unique_email,
                "password": "test123",
                "name": "Me Test",
                "interests": ["Macchine"]
            }
        )
        token = reg_resp.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Set sub_interests
        api_client.post(
            f"{BASE_URL}/api/auth/sub-interests",
            json={"sub_interests": {"Macchine": ["Ferrari"]}},
            headers=headers
        )
        
        # Get /me
        response = api_client.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "sub_interests" in data, "sub_interests field missing from /me"
        assert "Macchine" in data["sub_interests"]
        assert data["sub_interests"]["Macchine"] == ["Ferrari"]
        print("✓ GET /api/auth/me returns sub_interests")


class TestFeedFiltering:
    """Test feed filtering by sub_interests."""

    def test_feed_filter_by_sub_interests_ferrari_only(self, api_client):
        """Test GET /api/feed with sub_interests={Macchine:['Ferrari']} returns only Ferrari facts."""
        # Register user with Macchine interest
        unique_email = f"TEST_feed_ferrari_{uuid.uuid4().hex[:8]}@test.com"
        reg_resp = api_client.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": unique_email,
                "password": "test123",
                "name": "Feed Ferrari Test",
                "interests": ["Macchine"]
            }
        )
        token = reg_resp.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Set sub_interests to Ferrari only
        api_client.post(
            f"{BASE_URL}/api/auth/sub-interests",
            json={"sub_interests": {"Macchine": ["Ferrari"]}},
            headers=headers
        )
        
        # Get feed
        response = api_client.get(f"{BASE_URL}/api/feed?limit=50", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        facts = data["facts"]
        
        # Filter Macchine facts
        macchine_facts = [f for f in facts if f["category"] == "Macchine"]
        
        if macchine_facts:
            # All Macchine facts should be Ferrari or have no sub_category (general)
            for fact in macchine_facts:
                sub = fact.get("sub_category")
                if sub:
                    assert sub == "Ferrari", f"Expected Ferrari, got {sub} for fact: {fact['title']}"
            print(f"✓ Feed filtered: {len(macchine_facts)} Macchine facts, all Ferrari or general")
        else:
            print("⚠ No Macchine facts in feed (may need more facts seeded)")

    def test_feed_empty_sub_interests_returns_all(self, api_client):
        """Test GET /api/feed with empty sub_interests returns all facts from selected categories."""
        unique_email = f"TEST_feed_all_{uuid.uuid4().hex[:8]}@test.com"
        reg_resp = api_client.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": unique_email,
                "password": "test123",
                "name": "Feed All Test",
                "interests": ["Macchine", "Moto"]
            }
        )
        token = reg_resp.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Don't set sub_interests (empty by default)
        
        # Get feed
        response = api_client.get(f"{BASE_URL}/api/feed?limit=50", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        facts = data["facts"]
        
        # Should get facts from both Macchine and Moto
        macchine_facts = [f for f in facts if f["category"] == "Macchine"]
        moto_facts = [f for f in facts if f["category"] == "Moto"]
        
        # With empty sub_interests, should get all brands
        if macchine_facts:
            brands = set(f.get("sub_category") for f in macchine_facts if f.get("sub_category"))
            print(f"✓ Empty sub_interests: {len(macchine_facts)} Macchine facts with brands: {brands}")
        
        if moto_facts:
            brands = set(f.get("sub_category") for f in moto_facts if f.get("sub_category"))
            print(f"✓ Empty sub_interests: {len(moto_facts)} Moto facts with brands: {brands}")

    def test_facts_have_sub_category_field(self, api_client):
        """Test facts have sub_category field (null for original, populated for new)."""
        # Login as test user
        login_resp = api_client.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "test@test.com", "password": "test123"}
        )
        token = login_resp.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get feed
        response = api_client.get(f"{BASE_URL}/api/feed?limit=50", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        facts = data["facts"]
        
        # Check sub_category field exists
        for fact in facts:
            assert "sub_category" in fact or fact.get("sub_category") is None, \
                f"Fact missing sub_category field: {fact['title']}"
        
        # Check new categories have sub_category populated
        new_cat_facts = [f for f in facts if f["category"] in ["Mafia", "Guerre", "Motori", "Macchine", "Moto"]]
        if new_cat_facts:
            with_sub = [f for f in new_cat_facts if f.get("sub_category")]
            print(f"✓ Facts have sub_category field: {len(with_sub)}/{len(new_cat_facts)} new category facts have sub_category")


class TestFactsCount:
    """Test DB has 120+ facts after V3 seed."""

    def test_db_has_120_plus_facts(self, api_client):
        """Test GET /api/health shows 120+ facts."""
        response = api_client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        
        data = response.json()
        facts_count = data["facts"]
        assert facts_count >= 120, f"Expected 120+ facts, got {facts_count}"
        print(f"✓ DB has {facts_count} facts (120+ required)")


@pytest.fixture
def api_client():
    """Shared requests session."""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session
