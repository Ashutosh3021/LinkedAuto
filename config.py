import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() in ['true', '1', 't']
    TESTING = os.getenv('TESTING', 'False').lower() in ['true', '1', 't']
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')
    
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///linkedin_automation.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'openai/gpt-4o-mini')
    OPENROUTER_BASE_URL = 'https://openrouter.ai/api/v1'
    
    LINKEDIN_CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID')
    LINKEDIN_CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')
    LINKEDIN_REDIRECT_URI = os.getenv('LINKEDIN_REDIRECT_URI', 'http://localhost:5000/linkedin/callback')
    LINKEDIN_SCOPE = 'w_member_social openid profile email'
    LINKEDIN_AUTH_URL = 'https://www.linkedin.com/oauth/v2/authorization'
    LINKEDIN_TOKEN_URL = 'https://www.linkedin.com/oauth/v2/accessToken'
    LINKEDIN_API_BASE_URL = 'https://api.linkedin.com/v2'
