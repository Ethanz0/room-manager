import string
import secrets

class SecureTokenService:
    def generate_secure_token() -> str:
        """ Generate a random secure token """
        characters = string.ascii_letters + string.digits
        token = ''.join(secrets.choice(characters) for _ in range(25))
        return token