import sys
from unittest.mock import MagicMock

# Prevent code inside the SQLRepository module from running during unit testing
sys.modules['common.db.repository.repository'] = MagicMock()

from src.pi_roles.master_pi.communication.api.book_room import handle_book_room

def test_room_already_taken(mocker):
    """
    Authentication and booking logic
    Verifies that booking returns an error when the room is already booked for the requested time slot
    """
    sql_repo_mock = MagicMock()
    sql_repo_mock.fetch_all.return_value = [5]
    sql_repo_mock.__enter__.return_value = sql_repo_mock
    sql_repo_mock.__exit__.return_value = None

    mocker.patch("src.pi_roles.master_pi.communication.api.book_room.SQLRepository", return_value=sql_repo_mock)

    config = {"remote_db_host": "fakehost"}
    data = {
        "roomID": "123",
        "userID": "456",
        "date": "2024-10-10",
        "startTime": "10:00",
        "endTime": "12:00"
    }

    handler = handle_book_room()
    result = handler.handle(data, config)

    sql_repo_mock.fetch_all.assert_called_once()
    assert result["status"] == "error"
    assert result["error"] == "room unavailable at given time"

