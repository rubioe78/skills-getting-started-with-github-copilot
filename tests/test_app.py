import copy

from fastapi.testclient import TestClient
import pytest

import src.app as app_module

client = TestClient(app_module.app)

@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original))


def test_get_activities():
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert "Chess Club" in activities
    assert activities["Chess Club"]["description"].startswith("Learn strategies")


def test_signup_for_activity():
    # Arrange
    email = "newstudent@mergington.edu"
    url = "/activities/Chess%20Club/signup"
    params = {"email": email}

    # Act
    response = client.post(url, params=params)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in app_module.activities["Chess Club"]["participants"]


def test_signup_duplicate_fails():
    # Arrange
    url = "/activities/Chess%20Club/signup"
    params = {"email": "michael@mergington.edu"}

    # Act
    response = client.post(url, params=params)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_unknown_activity_fails():
    # Arrange
    url = "/activities/Nonexistent%20Club/signup"
    params = {"email": "student@mergington.edu"}

    # Act
    response = client.post(url, params=params)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant():
    # Arrange
    email = "michael@mergington.edu"
    url = "/activities/Chess%20Club/participants"
    params = {"email": email}

    # Act
    response = client.delete(url, params=params)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Chess Club"}
    assert email not in app_module.activities["Chess Club"]["participants"]


def test_unregister_missing_participant_fails():
    # Arrange
    url = "/activities/Chess%20Club/participants"
    params = {"email": "missing@mergington.edu"}

    # Act
    response = client.delete(url, params=params)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in activity"
