import sys
from unittest.mock import MagicMock

# Prevent code inside the SQLRepository module from running during unit testing
sys.modules['common.db.repository.repository'] = MagicMock()

from src.pi_roles.master_pi.communication.api.book_room import handle_book_room

def test_start_time_after_end_time_error(mocker):
    """
    User Input Validation
    Verifies that booking returns an error when start time is after end time
    """
    config = {"remote_db_host": "fakehost"}
    data = {
        "roomID": "123",
        "userID": "456",
        "date": "2024-10-10",
        "startTime": "14:01",
        "endTime": "14:00"  # End time before start time
    }

    handler = handle_book_room()
    result = handler.handle(data, config)

    assert result["status"] == "error"
    assert result["error"] == "startTime must be before endTime"
