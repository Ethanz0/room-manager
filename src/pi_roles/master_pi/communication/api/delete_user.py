from common.communication.interface import handle_socket_request_interface as interface
from common.db.repository.repository import SQLRepository

class handle_delete_user(interface):
    """ Handles deleting a user """
    def handle(self, data, config=None):
        user_id = data.get('user_id')
        
        if not user_id:
            return {"status": "error", "message": "Missing user_id"}
        
        try:
            with SQLRepository(config.get('remote_db_host')) as repo:
                repo.execute_query(
                    "DELETE FROM user WHERE user_id = %s", (user_id,))
                return {
                    "status": "success",
                    "message": "User deleted successfully"
                }
        except Exception as e:
            return {"status": "error", "message": f"Failed to delete user: {str(e)}"}