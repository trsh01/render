import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # API Configuration
    API_KEY = os.getenv('API_KEY')
    API_SECRET = os.getenv('API_SECRET')

    # Trading Configuration
    TEST_MODE = os.getenv('TEST_MODE', 'True').lower() == 'true'

    # Validate configuration
    @classmethod
    def validate(cls):
        if not cls.API_KEY or not cls.API_SECRET:
            raise ValueError("API_KEY and API_SECRET must be set in .env file")
        if cls.TEST_MODE:
            print("Running in TEST MODE - No real trades will be executed")
        else:
            print("Running in LIVE MODE - Real trades will be executed!")