"""
FastAPI tests for the Mergington High School Activities API.
Uses the AAA (Arrange-Act-Assert) testing pattern.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


# Original activities data for resetting state between tests
ORIGINAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
}


@pytest.fixture
def client():
    """Provide a test client and reset activities state before each test."""
    # Arrange: Reset to original state
    activities.clear()
    activities.update({
        activity: {**data, "participants": data["participants"].copy()}
        for activity, data in ORIGINAL_ACTIVITIES.items()
    })
    yield TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_returns_all_activities(self, client):
        """Test that the activities endpoint returns all available activities."""
        # Arrange: activities are pre-loaded by fixture

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_activity_includes_participant_list(self, client):
        """Test that each activity includes current participants."""
        # Arrange: activities are pre-loaded by fixture

        # Act
        response = client.get("/activities")

        # Assert
        data = response.json()
        chess_club = data["Chess Club"]
        assert "participants" in chess_club
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]

    def test_activity_includes_metadata(self, client):
        """Test that each activity includes required metadata fields."""
        # Arrange: activities are pre-loaded by fixture

        # Act
        response = client.get("/activities")

        # Assert
        data = response.json()
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_participant_succeeds(self, client):
        """Test that a new participant can successfully sign up for an activity."""
        # Arrange
        email = "new_student@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup actually adds the participant to the activity's participant list."""
        # Arrange
        email = "new_student@mergington.edu"
        activity = "Chess Club"

        # Act
        client.post(f"/activities/{activity}/signup", params={"email": email})
        response = client.get("/activities")

        # Assert
        data = response.json()
        assert email in data[activity]["participants"]

    def test_signup_duplicate_returns_400(self, client):
        """Test that signing up a student who is already registered returns a 400 error."""
        # Arrange
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signing up for a non-existent activity returns a 404 error."""
        # Arrange
        email = "student@mergington.edu"
        activity = "Nonexistent Club"

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint."""

    def test_unregister_existing_participant_succeeds(self, client):
        """Test that an existing participant can successfully unregister from an activity."""
        # Arrange
        email = "michael@mergington.edu"  # Currently in Chess Club
        activity = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]

    def test_unregister_removes_participant_from_activity(self, client):
        """Test that unregister actually removes the participant from the activity."""
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"

        # Act
        client.post(f"/activities/{activity}/unregister", params={"email": email})
        response = client.get("/activities")

        # Assert
        data = response.json()
        assert email not in data[activity]["participants"]

    def test_unregister_nonregistered_participant_returns_400(self, client):
        """Test that unregistering a non-registered participant returns a 400 error."""
        # Arrange
        email = "not_registered@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"].lower()

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Test that unregistering from a non-existent activity returns a 404 error."""
        # Arrange
        email = "student@mergington.edu"
        activity = "Nonexistent Club"

        # Act
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
