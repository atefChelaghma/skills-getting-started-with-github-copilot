import os
import sys

# Make sure tests can import the application from src/app.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def ensure_removed(activity: str, email: str):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    if email in data.get(activity, {}).get("participants", []):
        client.post(f"/activities/{activity}/unregister", params={"email": email})


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Sanity check: one known activity should exist
    assert "Chess Club" in data


def test_signup_and_unregister():
    activity = "Chess Club"
    email = "test.user@example.com"

    # Ensure clean state
    ensure_removed(activity, email)

    # Sign up
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Verify participant present
    resp = client.get("/activities")
    assert resp.status_code == 200
    participants = resp.json()[activity]["participants"]
    assert email in participants

    # Unregister
    resp = client.post(f"/activities/{activity}/unregister", params={"email": email})
    assert resp.status_code == 200
    assert "Unregistered" in resp.json().get("message", "")

    # Verify participant removed
    resp = client.get("/activities")
    participants = resp.json()[activity]["participants"]
    assert email not in participants
