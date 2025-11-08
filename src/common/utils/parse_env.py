import os
import json
import re
import socket
import subprocess


def load_and_expand_env_vars(template_path: str) -> dict:
    """Load a JSON template file and replace {VAR_NAME} with environment variable values."""
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace {VAR_NAME} with env values
    content = re.sub(r'"\{(\w+)\}"', get_env_var_on_match, content)
    return json.loads(content)


# Replace {VAR_NAME} with environment variable value
def get_env_var_on_match(match) -> str:
    """Return a matched {VAR_NAME} with its environment variable value."""
    var_name = match.group(1)
    if var_name == "NAME_ID":
        hostname = socket.gethostname() .strip()
        return f'"{os.getenv(var_name, hostname)}"'  # return with double quotes
    
    if var_name == "IP_ADDRESS":
        try:
            container_name = subprocess.check_output(
                ["docker", "ps", "--filter", f"id={socket.gethostname()}", "--format", "{{.Names}}"],
                text=True
            ).strip()
        except Exception:
            container_name = "<MISSING:IP_ADDRESS>"
        return f'"{container_name}"'
    var_value = os.getenv(var_name, f"<MISSING:{var_name}>")
    if var_value.isdigit():
        return var_value  # Return as number (no quotes)
    if var_value.lower() in ["true", "false"]:
        return var_value.lower()  # Return as boolean (no quotes)
    return f'"{var_value}"'


def substitute_addresses(config: dict, max_device_num: int = 10) -> dict:
    """Substitute [AGENT_ADDRESSES] and [ROOM_ADDRESSES] placeholders with env values."""
    # --- Build lists from env variables ---
    agent_addresses = []
    room_addresses = []

    # Collect AGENT_IP_ADDR1, AGENT_IP_ADDR2, ...
    for i in range(1, max_device_num):  # support up to 10, adjust as needed
        val = os.getenv(f"AGENT_IP_ADDR{i}")
        if val:
            agent_addresses.append(val)

    # Collect ROOM_IP_ADDR1, ROOM_IP_ADDR2, ...
    for i in range(1, max_device_num):
        val = os.getenv(f"ROOM_IP_ADDR{i}")
        if val:
            room_addresses.append(val)

    # --- Replace placeholders in config ---
    if config[socket.gethostname()]["agents"] == ["[AGENT_ADDRESSES]"]:
        config[socket.gethostname()]["agents"] = agent_addresses

    if config[socket.gethostname()]["rooms"] == ["[ROOM_ADDRESSES]"]:
        config[socket.gethostname()]["rooms"] = room_addresses

    return config
