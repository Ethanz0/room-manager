import sys
from unittest.mock import MagicMock
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Prevent code inside the SQLRepository module from running during unit testing
sys.modules['common.db.repository.repository'] = MagicMock()

from src.pi_roles.master_pi.communication.api.check_in_room import handle_check_in_room

def test_successful_check_in(mocker):
    """
    Authentication and booking logic
    Verifies that check-in returns success status when check-in is successful
    """
    sql_repo_mock = MagicMock()
    sql_repo_mock.fetch_one.return_value = [
        "ABCDEF", 
        False, 
        datetime.now(tz=ZoneInfo("Australia/Melbourne")) + timedelta(minutes=14) # Less than 15 minutes before check-in
    ]
    sql_repo_mock.execute_query.return_value = [None]
    sql_repo_mock.__enter__.return_value = sql_repo_mock
    sql_repo_mock.__exit__.return_value = None

    mocker.patch("src.pi_roles.master_pi.communication.api.check_in_room.SQLRepository", return_value=sql_repo_mock)

    config = {"remote_db_host": "fakehost"}
    data = {
        "bookingID": "123",
        "accessToken": "ABCDEF",
    }

    handler = handle_check_in_room()
    result = handler.handle(data, config)

    sql_repo_mock.fetch_one.assert_called_once()
    sql_repo_mock.execute_query.assert_called_once()
    assert result["status"] == "success"
    assert result["message"] == "check in successful"
