from common.communication.interface import handle_socket_request_interface as interface
from common.db.repository.repository import SQLRepository

class handle_get_user(interface):
    """ Handles getting a single user """
    
    def handle(self, data, config=None):
        try:
            with SQLRepository(config.get('remote_db_host')) as repo:

                result = repo.fetch_one("SELECT * FROM user WHERE user_id = %s", (data.get('user_id'),))
                
                if result is None:
                    return {"status": "error", "message": "User not found"}

                user = {
                    "user_id": result[0],
                    "first_name": result[1],
                    "last_name": result[2],
                    "email": result[3],
                    "role": result[4],
                    "sub_role": result[5],
                    "password": result[6]
                }
                
                return {
                    "status": "success",
                    "action": "get_all_users",
                    "user": user
                }
        except Exception as e:
            return {"status": "error", "message": f"Failed to fetch user: {e}"}