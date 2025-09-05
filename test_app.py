# test_app.py

import pytest
from datetime import datetime
from app import app, db
from models import Registration, Winner
from scheduler import select_winner
from freezegun import freeze_time

@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_register_success(client):
    """Test successful user registration."""
    response = client.post('/register', json={
        "name": "John Doe",
        "email": "john.doe@example.com"
    })
    assert response.status_code == 201
    assert response.json['message'] == "Registration successful"

def test_register_input_validation(client):
    """Test registration input validation for missing/invalid fields."""
    
    # Missing fields
    response = client.post('/register', json={
        "email": "test@example.com"
    })
    assert response.status_code == 400
    
    response = client.post('/register', json={
        "name": "John Doe"
    })
    assert response.status_code == 400
    
    # Empty fields
    response = client.post('/register', json={
        "name": "",
        "email": "test@example.com"
    })
    assert response.status_code == 400
    
    response = client.post('/register', json={
        "name": "John Doe",
        "email": ""
    })
    assert response.status_code == 400
    
    # Empty request
    response = client.post('/register', json={})
    assert response.status_code == 400
    
    # Invalid json
    response = client.post('/register', data='{"name": "John", invalid}', content_type='application/json')
    assert response.status_code == 400

def test_register_duplicate_email(client):
    """Test to prevent duplicate email registration within the same month."""
    client.post('/register', json={
        "name": "Jane Doe",
        "email": "jane.doe@example.com"
    })
    
    response = client.post('/register', json={
        "name": "Jane Doe",
        "email": "jane.doe@example.com"
    })
    
    assert response.status_code == 400
    assert response.json['error'] == "Email already registered this month"

def test_email_normalization(client):
    """Test to prevent duplicate email registration within the same month."""
    client.post('/register', json={
        "name": "Jane Doe",
        "email": "jane.doe@example.com"
    })
    
    response = client.post('/register', json={
        "name": "Jane Doe",
        "email": "jaNE.doe@EXAMple.com"
    })
    
    assert response.status_code == 400
    assert response.json['error'] == "Email already registered this month"

def test_winner_selection(client):
    """Test the winner selection logic."""
    client.post('/register', json={"name": "Alice", "email": "alice@example.com"})
    client.post('/register', json={"name": "Bob", "email": "bob@example.com"})

    select_winner()

    with app.app_context():
        winner_count = Winner.query.count()
        assert winner_count == 1

def test_no_participants_winner_selection(client, capsys):
    """Test winner selection with no participants."""
    select_winner()
    captured = capsys.readouterr()
    assert "No valid participants found" in captured.out

@freeze_time("2025-09-05 16:00:00") # set mock time to september
def test_winner_selection_with_only_outdated_participants(client):
    """
    Test that winner selection logic correctly isolates participants
    from the current, mocked month.
    """
    with app.app_context():
        aug_user = Registration(name="August User", email="august@example.com")
        aug_user.timestamp = datetime.strptime("2025-08-15 10:00:00", "%Y-%m-%d %H:%M:%S")

        db.session.add_all([aug_user])
        db.session.commit()

    select_winner()

    with app.app_context():
        assert Winner.query.count() == 0 

