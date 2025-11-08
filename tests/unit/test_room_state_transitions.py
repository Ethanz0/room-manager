import unittest
from unittest.mock import MagicMock
from flask_socketio import SocketIO
from common.utils.room_pi.room_status import RoomStatus, Status

class TestRoomStatus(unittest.TestCase):
    """Unit tests for the RoomStatus class."""

    def setUp(self):
        """Reset the singleton before each test to avoid cross-test contamination."""
        RoomStatus._singleton_instance = None
        RoomStatus._config = None

        self.mock_socketio = MagicMock(spec=SocketIO)
        self.mock_callback = MagicMock()
        self.initial_status = {
            "room1": Status.AVAILABLE,
            "room2": Status.RESERVED
        }

        self.room_status = RoomStatus(
            initial_status=self.initial_status.copy(),
            app=self.mock_socketio,
            on_change=lambda: self.mock_callback,
            config={"some": "config"}
        )

    def test_singleton_behavior(self):
        """Test that only one instance is created."""
        another_instance = RoomStatus.instance()
        self.assertIs(self.room_status, another_instance)

        with self.assertRaises(RuntimeError):
            # Accessing instance before initialization should raise
            RoomStatus._singleton_instance = None
            RoomStatus.instance()

    def test_update_status_calls_callback(self):
        """Test that updating a status key calls the callback."""
        self.room_status.update("room1", Status.IN_USE)
        self.mock_callback.assert_called_once_with(
            self.mock_socketio,
            {"some": "config"},
            "room1",
            Status.AVAILABLE,
            Status.IN_USE
        )

    def test_update_status_key_error(self):
        """Test updating a non-existent key is handled gracefully."""
        # Should not raise, just log error
        self.room_status.update("non_existent_key", Status.IN_USE)
        # No callback called
        self.mock_callback.assert_not_called()

    def test_get_and_as_dict(self):
        """Test retrieving values and the full status dict."""
        self.assertEqual(self.room_status.get("room1"), Status.AVAILABLE)
        self.assertEqual(self.room_status.as_dict(), self.initial_status)

    def test_str_and_repr(self):
        """Test string and repr outputs."""
        self.assertIn("room1", str(self.room_status))
        self.assertIn("room1", repr(self.room_status))

if __name__ == "__main__":
    unittest.main()
