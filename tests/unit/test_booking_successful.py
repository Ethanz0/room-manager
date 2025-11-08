import sys
from unittest.mock import MagicMock

sys.modules['common.db.repository.repository'] = MagicMock()

from src.pi_roles.master_pi.communication.api.book_room import handle_book_room

def test_booking_successful(mocker):
    """
    Authentication and Booking Logic
    Verifies that booking succeeds when a room is available and returns booking details
    """
    sql_repo_mock_1 = MagicMock()
    sql_repo_mock_1.fetch_all.return_value = []
    sql_repo_mock_1.__enter__.return_value = sql_repo_mock_1
    sql_repo_mock_1.__exit__.return_value = None
    
    sql_repo_mock_2 = MagicMock()
    sql_repo_mock_2.execute_query.return_value = 101
    sql_repo_mock_2.__enter__.return_value = sql_repo_mock_2
    sql_repo_mock_2.__exit__.return_value = None

    mocker.patch(
        "src.pi_roles.master_pi.communication.api.book_room.SQLRepository",
        side_effect=[sql_repo_mock_1, sql_repo_mock_2]
    )

    mocker.patch(
        "src.pi_roles.master_pi.communication.api.book_room.SecureTokenService.generate_secure_token",
        return_value="ABCDEF123456",
    )
    
    config = {"remote_db_host": "fakehost"}
    data = {
        "roomID": "5",
        "userID": "42",
        "date": "2024-10-15",
        "startTime": "10:00",
        "endTime": "12:00"
    }

    handler = handle_book_room()
    result = handler.handle(data, config)

    sql_repo_mock_1.fetch_all.assert_called_once()
    
    sql_repo_mock_2.execute_query.assert_called_once()
    
    assert result["status"] == "success"
    assert "bookingID" in result["data"]
    assert "accessToken" in result["data"]
    assert result["data"]["bookingID"] == 101
    assert result["data"]["accessToken"] == "ABCDEF123456"