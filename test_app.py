import pytest
from datetime import datetime
from app import create_app, db
from models import Registration, Winner
from scheduler import select_winner
from freezegun import freeze_time

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


from models import Registration, Winner, Log
from scheduler import select_winner

def test_get_registrations(client, app):
    """
    Tests the /registrations endpoint.
    """
    with app.app_context():
        reg = Registration(name="Test User", email="test@example.com")
        db.session.add(reg)
        db.session.commit()

    response = client.get('/registrations')

    assert response.status_code == 200
    assert response.json[0]['email'] == "test@example.com"

def test_get_winners(client, app):
    """
    Tests the /winners endpoint.
    """
    with app.app_context():
        reg = Registration(name="Winner User", email="winner@example.com")
        db.session.add(reg)
        db.session.commit()
        select_winner(app)

    response = client.get('/winners')

    assert response.status_code == 200
    assert response.json[0]['email'] == "winner@example.com"

def test_get_logs(client, app):
    """
    Tests the /logs endpoint.
    """
    client.post('/register', json={"name": "Log User", "email": "log@example.com"})

    response = client.get('/logs')

    assert response.status_code == 200
    assert 'action' in response.json[0]

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

def test_winner_selection(client, app):
    """Test the winner selection logic."""
    client.post('/register', json={"name": "Alice", "email": "alice@example.com"})
    client.post('/register', json={"name": "Bob", "email": "bob@example.com"})

    with app.app_context():
        select_winner(app)
        winner_count = Winner.query.count()
        assert winner_count == 1

def test_no_participants_winner_selection(client, capsys, app):
    """Test winner selection with no participants."""
    with app.app_context():
        select_winner(app)
        captured = capsys.readouterr()
        assert "No valid participants found" in captured.out

@freeze_time("2025-09-05 16:00:00") # set mock time to september
def test_winner_selection_with_only_outdated_participants(client, app):
    """
    Test that winner selection logic correctly isolates participants
    from the current, mocked month.
    """
    with app.app_context():
        aug_user = Registration(name="August User", email="august@example.com")
        aug_user.timestamp = datetime.strptime("2025-08-15 10:00:00", "%Y-%m-%d %H:%M:%S")

        db.session.add_all([aug_user])
        db.session.commit()

        select_winner(app)

    with app.app_context():
        assert Winner.query.count() == 0 

def test_register_invalid_email_format(client):
    """Test registration fails with an invalid email format."""
    response = client.post('/register', json={
        "name": "Test User",
        "email": "not-a-valid-email"
    })
    assert response.status_code == 400
