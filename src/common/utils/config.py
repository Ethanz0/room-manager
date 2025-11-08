import json

from pi_roles.master_pi.main import MasterPi
from pi_roles.agent_pi.main import AgentPi
from pi_roles.room_pi.main import RoomPi

def load_config(file_path, name_id):
    """Load configuration from a JSON file based on the role."""
    with open(file_path, encoding="utf-8") as f:
        config = json.load(f)
    return config[name_id]

def create_app(config, debug=False):
    """Create Flask app based on the role."""
    app = None
    role = config.get("role")
    if "master" in role:
        master = MasterPi()
        app = master.create_app(config, debug=debug)
    elif "agent" in role:
        agent = AgentPi()
        app = agent.create_app(config, debug=debug)
    elif "room" in role:
        room = RoomPi()
        app = room.create_app(config, debug=debug)
    else:
        raise ValueError(f"Unknown role {role}")
    return app

def print_config(config):
    """Pretty print the configuration to the console."""
    print(f"Using JSON configuration: {json.dumps(config, indent=4)}")
