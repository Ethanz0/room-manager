"""API module that exports all request handlers."""
from .delete_user import handle_delete_user
from .register import handle_register
from .login_user import handle_login_user
from .test_print import handle_test_print
from .get_available_rooms import handle_get_available_rooms
from .get_all_users import handle_get_all_users
from .get_user import handle_get_user
from .update_user import handle_update_user
from .create_user import handle_create_user
from .book_room import handle_book_room
from .get_booked_rooms import handle_get_booked_rooms
from .cancel_booking import handle_cancel_bookings
from .check_in_room import handle_check_in_room
from .login_admin import handle_login_admin
from .get_rooms import handle_get_rooms
from .check_availability import handle_check_availability
from .publish_status_update import handle_publish_status_update
from .get_logs import handle_get_logs
from .get_all_bookings import handle_get_all_bookings
from .get_all_booking_stats import handle_get_booking_stats
from .get_bookings_between import handle_get_bookings_between
from .qr_code_login import handle_qr_code_login

# Map action strings to api endpoints
socket_endpoints = {
    "register": handle_register(),
    "register_user": handle_register(),
    "login_user": handle_login_user(),
    "delete_user": handle_delete_user(),
    "test": handle_test_print(),
    "get_available_rooms": handle_get_available_rooms(),
    "get_all_users": handle_get_all_users(),
    "get_user": handle_get_user(),
    "update_user": handle_update_user(),
    "create_user": handle_create_user(),
    # add more actions here
    "get_rooms": handle_get_rooms(),
    "get_bookings_between": handle_get_bookings_between(),
    "check_availability": handle_check_availability(),
    "publish_status_update": handle_publish_status_update(),
    "book_room": handle_book_room(),
    "get_booked_rooms": handle_get_booked_rooms(),
    "cancel_booking": handle_cancel_bookings(),
    "check_in_room": handle_check_in_room(),
    "login_admin": handle_login_admin(),
    "get_logs": handle_get_logs(),
    "get_bookings": handle_get_all_bookings(),
    'get_booking_stats': handle_get_booking_stats(),
    "qr_code_login": handle_qr_code_login()
    }