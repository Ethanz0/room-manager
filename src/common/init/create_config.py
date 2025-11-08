import json

from common.utils.parse_env import load_and_expand_env_vars, substitute_addresses

TEMPLATE_FILE = "config.template.json"
OUTPUT_FILE = "../config.json"


def create_config(template_path: str = TEMPLATE_FILE, output_path: str = OUTPUT_FILE):
    # --- Build agent and room address arrays ---
    """Create config.json from config.template.json by expanding environment variables."""
    config = load_and_expand_env_vars(template_path)

    config = substitute_addresses(config)
    
    # Write the expanded JSON to output file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
