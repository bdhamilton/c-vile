#!/usr/bin/env python
import sys
import os
from dotenv import load_dotenv

sys.path.insert(0, '/var/www/cvile/html')

# Debug: Check if .env file exists
env_file = '/var/www/cvile/.env'
print(f"Looking for .env at: {env_file}")
print(f".env exists: {os.path.exists(env_file)}")
print(f"Current user: {os.getuid()}")

# Try to load and show result
result = load_dotenv(env_file)
print(f"load_dotenv result: {result}")

print(f"GRIPES_FILE env var: {os.getenv('GRIPES_FILE')}")

# Import app AFTER loading environment
from app import app as application

if __name__ == "__main__":
    application.run()