import sys
from unittest.mock import MagicMock
sys.modules['common.db.repository.repository'] = MagicMock()
from src.pi_roles.master_pi.communication.api.qr_code_login import handle_qr_code_login

def test_qr_login_successful(mocker):
    """
    Additional Feature Test
    Test successful QR code login
    """
    sql_repo_mock = MagicMock()
    sql_repo_mock.fetch_one.return_value = (
        42,
        "Ethan",
        "Zhang",
        "ethan@mail.com",
        "user",
        "VALID_TOKEN"
    )
    sql_repo_mock.__enter__.return_value = sql_repo_mock
    sql_repo_mock.__exit__.return_value = None
    
    mocker.patch(
        "src.pi_roles.master_pi.communication.api.qr_code_login.SQLRepository",
        return_value=sql_repo_mock
    )
    
    config = {"remote_db_host": "fakehost"}
    data = {"userID": "42", "token": "VALID_TOKEN"}
    
    handler = handle_qr_code_login()
    result = handler.handle(data, config)
    
    assert result["status"] == "success"
    assert result["data"]["userID"] == 42
    assert result["data"]["qrCodeToken"] == "VALID_TOKEN"

def test_qr_login_invalid_token(mocker):
    """
    Additional Feature Test
    Test QR code login with wrong token
    """
    sql_repo_mock = MagicMock()
    sql_repo_mock.fetch_one.return_value = (
        42,
        "Ethan",
        "Zhang",
        "ethan@mail.com",
        "user",
        "VALID_TOKEN"
    )
    sql_repo_mock.__enter__.return_value = sql_repo_mock
    sql_repo_mock.__exit__.return_value = None
    
    mocker.patch(
        "src.pi_roles.master_pi.communication.api.qr_code_login.SQLRepository",
        return_value=sql_repo_mock
    )
    
    config = {"remote_db_host": "fakehost"}
    data = {"userID": "42", "token": "INVALID_TOKEN"}
    
    handler = handle_qr_code_login()
    result = handler.handle(data, config)
    
    assert result["status"] == "error"
    assert result["error"] == "invalid credentials"

def test_qr_login_user_not_found(mocker):
    """
    Additional Feature Test
    Test QR code login with non existent user
    """
    sql_repo_mock = MagicMock()
    sql_repo_mock.fetch_one.return_value = None
    sql_repo_mock.__enter__.return_value = sql_repo_mock
    sql_repo_mock.__exit__.return_value = None
    
    mocker.patch(
        "src.pi_roles.master_pi.communication.api.qr_code_login.SQLRepository",
        return_value=sql_repo_mock
    )
    
    config = {"remote_db_host": "fakehost"}
    data = {"userID": "999", "token": "ANY_TOKEN"}
    
    handler = handle_qr_code_login()
    result = handler.handle(data, config)
    
    assert result["status"] == "error"
    assert result["error"] == "invalid credentials"
