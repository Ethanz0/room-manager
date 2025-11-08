from common.communication.interface import handle_socket_request_interface as interface
from common.db.repository.repository import SQLRepository

class handle_test_print(interface):
    """ Handle test print requests """
    def handle(self, data, config=None):
        message = data.get("message")
        if not message:
            return {"error": "Missing 'message' field"}
        print(f"Received message at '/test' endpoint: {message}")
        
        with SQLRepository(config.get('remote_db_host')) as repo:
            repo.execute_query("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY AUTO_INCREMENT, name TEXT)")
            repo.execute_query("INSERT INTO test (name) VALUES (%s)", ("Sample Name",))
            results = repo.fetch_all("SELECT * FROM test")
            print("Database initialized and sample data inserted:", results)
        return {"status": "success", "action": "test", "message": message}