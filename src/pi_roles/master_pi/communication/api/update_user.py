from common.communication.interface import handle_socket_request_interface as interface
from common.db.repository.repository import SQLRepository

class handle_update_user(interface):
    """ Handles updating a user """
    def handle(self, data, config=None):
        user_id = data.get('user_id')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        password = data.get('password')
        
        # Validate required fields
        if not all([user_id, first_name, last_name, email, password]):
            return {"status": "error", "message": "Missing required fields"}
        
        try:
            with SQLRepository(config.get('remote_db_host')) as repo:
                repo.execute_query(
                    "UPDATE user SET first_name = %s, last_name = %s, email = %s, password = %s WHERE user_id = %s",
                    (first_name, last_name, email, password, user_id)
                )
                
                return {
                    "status": "success",
                    "message": "User updated successfully"
                }
        except Exception as e:
            return {"status": "error", "message": f"Failed to update user: {str(e)}"}