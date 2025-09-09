#!/usr/bin/env python
import sys
import os
from dotenv import load_dotenv

sys.path.insert(0, '/var/www/cvile/html')
result = load_dotenv('/var/www/cvile/.env')

# Import app AFTER loading environment
from app import app as application

if __name__ == "__main__":
    application.run()