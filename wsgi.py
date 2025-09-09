#!/usr/bin/env python
import sys
from dotenv import load_dotenv
from app import app as application

sys.path.insert(0, '/var/www/cvile/html')
load_dotenv('/var/www/cvile/.env')

if __name__ == "__main__":
    application.run()