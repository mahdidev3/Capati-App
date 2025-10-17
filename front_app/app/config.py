import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    BACKEND_URL = os.environ.get('BACKEND_URL') or 'http://127.0.0.1:8000/v1'
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 3000))