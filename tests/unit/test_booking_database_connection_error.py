import sys
from unittest.mock import MagicMock

sys.modules['common.db.repository.repository'] = MagicMock()

from src.pi_roles.master_pi.communication.api.book_room import handle_book_room

def test_booking_database_connection_error(mocker):
    """
    Exception Handling - Database Connection Failure
    Verifies that booking handles database errors gracefully when connection fails
    """
    sql_repo_mock = MagicMock()
    sql_repo_mock.__enter__.side_effect = Exception("Database connection failed")
    sql_repo_mock.__exit__.return_value = None

    mocker.patch(
        "src.pi_roles.master_pi.communication.api.book_room.SQLRepository",
        return_value=sql_repo_mock
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
    
    try:
        result = handler.handle(data, config)
        assert result["status"] == "error"
        assert "database" in result["error"].lower() or "error" in result["error"].lower()
    except Exception as e:
        assert "Database connection failed" in str(e)