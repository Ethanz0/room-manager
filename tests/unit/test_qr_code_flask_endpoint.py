import pytest
from flask import Flask
from unittest.mock import MagicMock, patch
import sys

sys.path.insert(0, 'src')

@pytest.fixture
def client():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test_secret'
    config = {}
    
    from pi_roles.agent_pi.routes.endpoints.login import login_endpoints
    login_endpoints(app, config)
    
    with app.test_client() as client:
        yield client

def test_qrcode_login_endpoint_success(client, mocker):
    """
    Additional Feature Test
    Test /qrcode-login endpoint with valid credentials
    Should return positive message and status code
    Should update session with user info
    """
    mock_socket = MagicMock()
    mock_socket.send_request.return_value = {
        "status": "success",
        "data": {
            "userID": 42,
            "firstName": "Ethan",
            "lastName": "Zhang",
            "email": "ethan@mail.com",
            "role": "user",
            "qrCodeToken": "VALID_TOKEN"
        }
    }
    mock_socket.__enter__.return_value = mock_socket
    mock_socket.__exit__.return_value = None
    
    mocker.patch(
        "pi_roles.agent_pi.routes.endpoints.login.JsonSocketClient",
        return_value=mock_socket
    )
    
    response = client.post('/qrcode-login', json={
        "userID": "42",
        "token": "VALID_TOKEN"
    })
    
    assert response.status_code == 200
    assert response.json["message"] == "QR Code Login successful!"
    
    with client.session_transaction() as sess:
        assert sess["user_id"] == 42
        assert sess["user"]["user_id"] == 42
        assert sess["user"]["email"] == "ethan@mail.com"
        assert sess["user"]["first_name"] == "Ethan"
        assert sess["user"]["last_name"] == "Zhang"
        assert sess["user"]["role"] == "user"
        assert sess["user"]["qr_code_token"] == "VALID_TOKEN"


def test_qrcode_login_endpoint_invalid_credentials(client, mocker):
    """
    Additional Feature Test
    Test /qrcode-login endpoint with invalid credentials
    Should handle error with status code and message
    Should not update session
    """
    mock_socket = MagicMock()
    mock_socket.send_request.return_value = {
        "status": "error",
        "error": "invalid credentials"
    }
    mock_socket.__enter__.return_value = mock_socket
    mock_socket.__exit__.return_value = None
    
    mocker.patch(
        "pi_roles.agent_pi.routes.endpoints.login.JsonSocketClient",
        return_value=mock_socket
    )
    
    response = client.post('/qrcode-login', json={
        "userID": "42",
        "token": "WRONG_TOKEN"
    })
    
    assert response.status_code == 401
    assert "Invalid userID or token" in response.json["message"]

    with client.session_transaction() as sess:
        assert "user_id" not in sess
        assert "user" not in sess

def test_qrcode_login_endpoint_missing_fields(client):
    """
    Additional Feature Test
    Test /qrcode-login endpoint with missing fields
    Should handle error with status code and message
    Should not update session
    """
    # Missing token
    response = client.post('/qrcode-login', json={"userID": "42"})
    assert response.status_code == 400
    assert "Missing fields" in response.json["message"]
    
    # Missing userID
    response = client.post('/qrcode-login', json={"token": "TOKEN"})
    assert response.status_code == 400
    assert "Missing fields" in response.json["message"]

    with client.session_transaction() as sess:
        assert "user_id" not in sess
        assert "user" not in sess
