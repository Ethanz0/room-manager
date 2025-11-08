"""API module that exports all request handlers."""
from .check_in import handle_check_in
from .update_status import handle_update_status
from .get_status import handle_get_status

# Map action strings to api endpoints
socket_endpoints = {
    "check_in": handle_check_in(),
    "update_status": handle_update_status(),
    "get_status": handle_get_status(),
    # add more actions here
}