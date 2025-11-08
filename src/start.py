#!/bin/bash
import argparse
import socket
import os

from common.init.create_config import create_config, TEMPLATE_FILE, OUTPUT_FILE
from common.utils.config import load_config, create_app, print_config
from common.utils.flush import flush_stdout_periodically
from common.db.server.init import init_db_config
from common.db.server.db_server import SQLServer

def main():
    """Main entry point to start the appropriate Flask app based on role."""
    # Generate config.json from config.template.json and environment variables (expected to be injected by Docker)
    if (os.getenv("IS_DOCKER", "false").lower() == "true"):
        # TODO: Temporary solution to force flush stdout/stderr every second to avoid Docker log buffering
        flush_stdout_periodically(1.0)  # Flush every 1 second
        create_config(TEMPLATE_FILE, OUTPUT_FILE)

    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", required=True, help="Role: master | room1 | agent1")
    # Set to True for development, False for simulating production
    DEBUG_FLAG = not parser.add_argument("--sim", action="store_true", help="Turn off debug mode to simulate production") or not parser.parse_known_args()[0].sim
    args = parser.parse_args()

    # Load the configuration for the specified device
    if (os.getenv("IS_DOCKER", "false").lower() == "true"):
        config = load_config("../config.json", socket.gethostname())
    else:
        config = load_config("config.default.json", args.role)
    
    print_config(config)

    # Check if the role specified in config exists
    if config.get('role') not in load_config("config.template.json", "roles"):
        raise ValueError(f"Role {config.get('role')} not found in JSON configuration")

    if config.get('role') == "database":
        db_server = SQLServer(config.get("host"))
        db_server.run()
        return

    if config.get('db_init_config') is True:
        init_db_config(config) 

    app = create_app(config, debug=DEBUG_FLAG)


    app.run(host=config.get("host"), port=config.get("port"), debug=DEBUG_FLAG)

if __name__ == "__main__":
    main()

