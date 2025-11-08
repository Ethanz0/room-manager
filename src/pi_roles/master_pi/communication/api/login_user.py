from common.communication.interface import handle_socket_request_interface as interface
from common.db.repository.repository import SQLRepository
from pi_roles.master_pi.services.secure_token_service import SecureTokenService

class handle_login_user(interface):
    """ Handle user login requests """
    def handle(self, data, config=None):
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return {"status": "error", "error": "Missing email or password"}
            
        
        try:
            with SQLRepository(config.get('remote_db_host')) as repo:
                user = repo.fetch_one(
                    "SELECT user_id, first_name, last_name, email, role, qr_code_token FROM user WHERE email = %s AND password = %s",
                    (email, password)
                )
                
                if not user:
                    return {"status": "error", "error": "invalid credentials"}
                
                qr_code_token = user[5]

                if qr_code_token == None:
                    qr_code_token = SecureTokenService.generate_secure_token()

                    repo.execute_query(
                        "UPDATE user SET qr_code_token = %s WHERE user_id = %s",
                        (qr_code_token, user[0])
                    )

                return {
                    "status": "success",
                    "data": {
                        "userID": user[0],
                        "firstName": user[1],
                        "lastName": user[2],
                        "email": user[3],
                        "role": user[4],
                        "qrCodeToken": qr_code_token
                    }
                }
        except Exception as e:
            print(f"Error during login: {e}")
            return {"status": "error", "error": f"Database error: {str(e)}"}