from common.communication.interface import handle_socket_request_interface as interface
from common.db.repository.repository import SQLRepository

class handle_create_user(interface):
    """ Handles creating a new user """
    def handle(self, data, config=None):
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')
        sub_role = data.get('sub_role', '')
        
        # Validate required fields
        if not all([first_name, last_name, email, password, role]):
            return {"status": "error", "message": "Missing required fields"}
        
        try:
            with SQLRepository(config.get('remote_db_host')) as repo:
                repo.execute_query(
                    "INSERT INTO user (first_name, last_name, email, password, role, sub_role) VALUES (%s, %s, %s, %s, %s, %s)",
                    (first_name, last_name, email, password, role, sub_role)
                )
                
                return {
                    "status": "success",
                    "message": "User created successfully"
                }
        except Exception as e:
            return {"status": "error", "message": f"Failed to create user: {str(e)}"}