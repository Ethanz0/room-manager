def return_role_by_address(address, agent_addresses, room_addresses):
    """Return the role of the device based on its IP address"""
    if address in agent_addresses:
        return "AGENT"
    elif address in room_addresses:
        return "ROOM"
    else:
        return "UNKNOWN"