from common.communication.interface import handle_socket_request_interface as interface
from common.db.repository.repository import SQLRepository

class handle_register(interface):
    """ Handle user registration requests """
    def handle(self, data, config=None):
        first_name = data.get('firstName')
        last_name = data.get('lastName')
        email = data.get('email')
        password = data.get('password')
        sub_role = data.get('role')
        
        if not all([first_name, last_name, email, password, sub_role]):
            return {"status": "error", "error": "Missing required fields"}
        
        try:
            with SQLRepository(config.get('remote_db_host')) as repo:
                user_exists = repo.fetch_one(
                    "SELECT * FROM user WHERE email = %s", 
                    (email,)
                )
                
                if user_exists:
                    return {"status": "error", "error": "email already registered"}
                
                repo.execute_query(
                    "INSERT INTO user (first_name, last_name, email, password, role, sub_role) VALUES (%s, %s, %s, %s, %s, %s)",
                    (first_name, last_name, email, password, "User", sub_role)
                )
                
                user_id_row = repo.fetch_one(
                    "SELECT user_id FROM user WHERE email = %s", 
                    (email,)
                )
                user_id = user_id_row[0] if user_id_row else None
                
                if not user_id:
                    return {"status": "error", "error": "Failed to retrieve user ID"}
                
                return {
                    "status": "success",
                    "data": {
                        "userID": user_id
                    }
                }
        except Exception as e:
            print(f"Error during registration: {e}")
            return {"status": "error", "error": f"Database error: {str(e)}"}