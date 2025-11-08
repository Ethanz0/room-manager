from common.communication.interface import handle_socket_request_interface as interface
from common.db.repository.repository import SQLRepository

class handle_get_all_users(interface):
    """ Handles getting all users """
    
    def handle(self, data, config=None):
        try:
            with SQLRepository(config.get('remote_db_host')) as repo:

                results = repo.fetch_all("SELECT * FROM user")
                
                if results is None:
                    return {"status": "error", "message": "Failed to fetch users"}
                
                users = []
                for row in results:
                    user = {
                        "user_id": row[0],
                        "first_name": row[1],
                        "last_name": row[2],
                        "email": row[3],
                        "role": row[4],
                        "sub_role": row[5],
                    }
                    users.append(user)
                
                return {
                    "status": "success",
                    "action": "get_all_users",
                    "users": users
                }
        except Exception as e:
            return {"status": "error", "message": f"Failed to retrieve all users{e}"} 