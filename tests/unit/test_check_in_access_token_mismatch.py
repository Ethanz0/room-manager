import sys
from unittest.mock import MagicMock
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

sys.modules['common.db.repository.repository'] = MagicMock()

from src.pi_roles.master_pi.communication.api.check_in_room import handle_check_in_room

def test_check_in_access_token_mismatch(mocker):
    """
    Exception Handling - Invalid Access Token
    Verifies that check-in fails when the access token doesn't match
    """
    sql_repo_mock = MagicMock()
    
    sql_repo_mock.fetch_one.return_value = [
        "CORRECT_TOKEN",
        False,
        datetime.now(tz=ZoneInfo("Australia/Melbourne")) + timedelta(minutes=10)
    ]
    
    sql_repo_mock.__enter__.return_value = sql_repo_mock
    sql_repo_mock.__exit__.return_value = None

    mocker.patch("src.pi_roles.master_pi.communication.api.check_in_room.SQLRepository", return_value=sql_repo_mock)

    config = {"remote_db_host": "fakehost"}
    data = {
        "bookingID": "123",
        "accessToken": "WRONG_TOKEN",
    }

    handler = handle_check_in_room()
    result = handler.handle(data, config)

    sql_repo_mock.fetch_one.assert_called_once()
    
    sql_repo_mock.execute_query.assert_not_called()
    
    assert result["status"] == "error"
    assert "access token" in result["error"].lower() or "invalid" in result["error"].lower()