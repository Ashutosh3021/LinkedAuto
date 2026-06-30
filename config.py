import os
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() in ['true', '1', 't']
    TESTING = os.getenv('TESTING', 'False').lower() in ['true', '1', 't']
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')
    
    # Database configuration - support PostgreSQL for Render
    database_url = os.getenv('DATABASE_URL', 'sqlite:///linkedin_automation.db')
    # Render provides DATABASE_URL starting with postgres://, but SQLAlchemy requires postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    # Configure SSL and connection pooling for PostgreSQL
    if 'postgresql' in database_url:
        # Parse the URL to add SSL parameters and connection pool settings
        parsed_url = urlparse(database_url)
        query_params = parse_qs(parsed_url.query)
        
        # SSL settings
        query_params['sslmode'] = ['require']  # Enforce SSL connection
        query_params['connect_timeout'] = ['10']
        query_params['application_name'] = ['linkedin-automation']
        
        # Reconstruct URL
        new_query = urlencode(query_params, doseq=True)
        database_url = urlunparse(parsed_url._replace(query=new_query))
    
    SQLALCHEMY_DATABASE_URI = database_url
    
    # SQLAlchemy connection pooling configuration
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 30,
        'pool_recycle': 1800,  # Recycle connections after 30 minutes
        'pool_pre_ping': True,  # Check connection health before use
        'connect_args': {
            'connect_timeout': 10,
            'application_name': 'linkedin-automation',
        }
    } if 'postgresql' in database_url else {}
    
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
