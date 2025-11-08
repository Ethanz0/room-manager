import sys
from unittest.mock import MagicMock

sys.modules['common.db.repository.repository'] = MagicMock()

from src.pi_roles.master_pi.communication.api.book_room import handle_book_room


def test_user_input_missing_fields(mocker):
    """
    User Input Validation
    Verifies that booking fails when required fields are missing
    """
    config = {"remote_db_host": "fakehost"}
    
    data_missing_room = {
        "userID": "456",
        "date": "2024-10-10",
        "startTime": "10:00",
        "endTime": "12:00"
    }
    
    handler = handle_book_room()
    result = handler.handle(data_missing_room, config)
    
    assert result["status"] == "error"
    assert "roomID" in result["error"] or "missing" in result["error"].lower()