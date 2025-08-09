#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    # Resolve config.json relative to this script (kaveri/scripts -> kaveri/config.json)
    config_path = Path(__file__).resolve().parents[1] / 'config.json'

    auth = os.getenv('KAVERI_AUTH')
    cookie = os.getenv('KAVERI_COOKIE')

    if not (auth and cookie):
        print('⚠️ No credentials found in secrets')
        return 0

    # Load existing config if present
    try:
        if config_path.exists():
            with config_path.open('r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {}
    except Exception as e:
        print(f'⚠️ Failed to read config.json: {e}')
        config = {}

    # Ensure credentials block exists
    config.setdefault('credentials', {})
    config['credentials']['authorization'] = auth
    config['credentials']['cookie'] = cookie
    config['credentials']['last_updated'] = datetime.now(timezone.utc).isoformat()

    # Write back to config
    try:
        with config_path.open('w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print('✓ Credentials updated from secrets')
    except Exception as e:
        print(f'❌ Failed to write config.json: {e}')
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
