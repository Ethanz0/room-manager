from common.communication.interface import handle_socket_request_interface as interface
from common.db.repository.repository import SQLRepository

class handle_login_admin(interface):
    """ Handles admin login authentication """
    
    def handle(self, data, config=None):
        try:
            with SQLRepository(config.get('remote_db_host')) as repo:
                result = repo.fetch_one(
                    "SELECT * FROM user WHERE email = %s AND password = %s AND role = %s", 
                    (data.get('email'), data.get('password'), 'Admin')
                )
                
                if result is None:
                    return {"status": "error", "message": "Invalid credentials or not an admin"}
                
                user = {
                    "user_id": result[0],
                    "first_name": result[1],
                    "last_name": result[2],
                    "email": result[3],
                }
                
                return {
                    "status": "success",
                    "action": "admin_login",
                    "user": user
                }
        except Exception as e:
            return {"status": "error", "message": f"Error logging in admin: {e}"}