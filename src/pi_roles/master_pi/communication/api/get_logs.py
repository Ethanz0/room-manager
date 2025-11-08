from common.communication.interface import handle_socket_request_interface as interface
from common.db.repository.repository import SQLRepository
from datetime import datetime
import re

class handle_get_logs(interface):
    """Handle fetching system logs"""
    
    def handle(self, data, config=None):
        log_type = data.get("log_type", "")
        try:
            with SQLRepository(config.get('remote_db_host')) as repo:
                if log_type:
                    query = "SELECT * FROM usage_logs WHERE type = %s ORDER BY timestamp DESC, log_id DESC"
                    results = repo.fetch_all(query, (log_type,))
                else:
                    query = "SELECT * FROM usage_logs ORDER BY timestamp DESC, log_id DESC"
                    results = repo.fetch_all(query)
                
                if results is None:
                    results = []
                
                logs = []
                for row in results:
                    logs.append({
                        "log_id": row[0],
                        "timestamp": row[1].strftime('%Y-%m-%d %H:%M:%S'),
                        "type": row[2],
                        "description": row[3]
                    })
                
                return {"status": "success", "logs": logs}
        except Exception as e:
            return {"status": "error", "message": f"Failed to retrieve logs: {e}"}