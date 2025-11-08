from common.communication.interface import handle_socket_request_interface as interface
from common.db.repository.repository import SQLRepository

class handle_qr_code_login(interface):
    """ Handle user QR code login requests """
    def handle(self, data, config=None):
        userID = data.get('userID')
        token = data.get('token')
        
        if userID == None:
            return {"status": "error", "error": "Missing userID"}
        if token == None:
            return {"status": "error", "error": "Missing token"}
        
        try:
            with SQLRepository(config.get('remote_db_host')) as repo:
                user = repo.fetch_one(
                    "SELECT user_id, first_name, last_name, email, role, qr_code_token FROM user WHERE user_id = %s",
                    (userID,)
                )
                
                if user == None:
                    return {"status": "error", "error": "invalid credentials"}

                if token == None:
                    return {"status": "error", "error": "invalid credentials"}

                qr_code_token = user[5]
                if qr_code_token != token:
                    return {"status": "error", "error": "invalid credentials"}

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
            print(f"Error during QR code login: {e}")
            return {"status": "error", "error": f"Database error: {str(e)}"}