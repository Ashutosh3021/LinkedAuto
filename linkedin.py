import logging
import secrets
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from requests_oauthlib import OAuth2Session
from config import Config
from models import db, LinkedInCredential, LogLevel, Post, LinkedInAppCredentials
from database import LogHelper, PostHelper
from utils import decrypt_api_key


logger = logging.getLogger(__name__)


class LinkedInAuth:
    def __init__(self):
        # Try to get active app credentials from DB first, fall back to Config
        app_creds = LinkedInAppCredentials.query.filter_by(is_active=True).first()
        if app_creds:
            self.client_id = app_creds.client_id
            self.client_secret = decrypt_api_key(app_creds.client_secret_encrypted)
            self.redirect_uri = app_creds.redirect_uri
        else:
            self.client_id = Config.LINKEDIN_CLIENT_ID
            self.client_secret = Config.LINKEDIN_CLIENT_SECRET
            self.redirect_uri = Config.LINKEDIN_REDIRECT_URI
        self.scope = Config.LINKEDIN_SCOPE
        self.auth_url = Config.LINKEDIN_AUTH_URL
        self.token_url = Config.LINKEDIN_TOKEN_URL
        self.api_base = Config.LINKEDIN_API_BASE_URL
        
    def get_authorization_url(self) -> tuple[str, str]:
        state = secrets.token_urlsafe(32)
        oauth = OAuth2Session(
            self.client_id,
            redirect_uri=self.redirect_uri,
            scope=self.scope
        )
        authorization_url, _ = oauth.authorization_url(self.auth_url, state=state)
        return authorization_url, state
    
    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        oauth = OAuth2Session(self.client_id, redirect_uri=self.redirect_uri)
        token = oauth.fetch_token(
            self.token_url,
            client_secret=self.client_secret,
            code=code,
            include_client_id=True
        )
        return token
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        oauth = OAuth2Session(self.client_id, token={'refresh_token': refresh_token})
        token = oauth.refresh_token(
            self.token_url,
            refresh_token=refresh_token,
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        return token


class LinkedInTokenManager:
    def __init__(self, auth_service: LinkedInAuth):
        self.auth = auth_service
        
    def get_valid_credential(self) -> Optional[LinkedInCredential]:
        credential = LinkedInCredential.query.order_by(LinkedInCredential.updated_at.desc()).first()
        if not credential:
            return None
        
        if datetime.utcnow() >= credential.token_expires_at:
            if credential.refresh_token and credential.refresh_token_expires_at and datetime.utcnow() < credential.refresh_token_expires_at:
                try:
                    new_token = self.auth.refresh_access_token(credential.refresh_token)
                    self._update_credential(credential, new_token)
                    db.session.commit()
                    logger.info("Successfully refreshed LinkedIn access token")
                except Exception as e:
                    logger.error(f"Failed to refresh access token: {e}")
                    return None
            else:
                logger.warning("Access token expired and no valid refresh token available")
                return None
        
        return credential
    
    def save_credential(self, token: Dict[str, Any]) -> LinkedInCredential:
        credential = LinkedInCredential.query.order_by(LinkedInCredential.updated_at.desc()).first()
        
        token_expires_at = datetime.utcnow() + timedelta(seconds=token.get('expires_in', 7200))
        refresh_token_expires_at = None
        if token.get('refresh_token_expires_in'):
            refresh_token_expires_at = datetime.utcnow() + timedelta(seconds=token['refresh_token_expires_in'])
        
        if not credential:
            credential = LinkedInCredential(
                access_token=token['access_token'],
                refresh_token=token.get('refresh_token'),
                token_expires_at=token_expires_at,
                refresh_token_expires_at=refresh_token_expires_at
            )
            db.session.add(credential)
        else:
            credential.access_token = token['access_token']
            credential.refresh_token = token.get('refresh_token')
            credential.token_expires_at = token_expires_at
            credential.refresh_token_expires_at = refresh_token_expires_at
        
        db.session.commit()
        
        LogHelper.create(
            Log,
            level=LogLevel.INFO,
            message="LinkedIn credentials saved successfully",
            context=None
        )
        
        return credential
    
    def _update_credential(self, credential: LinkedInCredential, token: Dict[str, Any]) -> None:
        credential.access_token = token['access_token']
        if 'refresh_token' in token:
            credential.refresh_token = token['refresh_token']
            if 'refresh_token_expires_in' in token:
                credential.refresh_token_expires_at = datetime.utcnow() + timedelta(seconds=token['refresh_token_expires_in'])
        credential.token_expires_at = datetime.utcnow() + timedelta(seconds=token.get('expires_in', 7200))


class LinkedInPublisher:
    def __init__(self, token_manager: LinkedInTokenManager):
        self.token_manager = token_manager
        self.api_base = 'https://api.linkedin.com/v2'
        self.userinfo_url = 'https://api.linkedin.com/v2/userinfo'
        
    def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        try:
            response = requests.get(self.userinfo_url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            return None
    
    def publish_post(self, post_content: str) -> Optional[Dict[str, Any]]:
        credential = self.token_manager.get_valid_credential()
        if not credential:
            raise Exception("No valid LinkedIn credentials available")
        
        user_info = self.get_user_info(credential.access_token)
        if not user_info or 'sub' not in user_info:
            raise Exception("Failed to get LinkedIn user information")
        
        linkedin_user_id = user_info['sub']
        
        headers = {
            'Authorization': f'Bearer {credential.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        payload = {
            'author': f'urn:li:person:{linkedin_user_id}',
            'lifecycleState': 'PUBLISHED',
            'specificContent': {
                'com.linkedin.ugc.ShareContent': {
                    'shareCommentary': {
                        'text': post_content
                    },
                    'shareMediaCategory': 'NONE'
                }
            },
            'visibility': {
                'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
            }
        }
        
        try:
            response = requests.post(
                f'{self.api_base}/ugcPosts',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            logger.debug(f"LinkedIn API response status: {response.status_code}")
            logger.debug(f"LinkedIn API response content: {response.text}")
            
            response.raise_for_status()
            
            response_data = {}
            if response.status_code == 201:
                location_header = response.headers.get('X-RestLi-Id')
                if location_header:
                    response_data['post_id'] = location_header
                else:
                    response_data['post_id'] = response.headers.get('Location', '')
            
            LogHelper.create(
                Log,
                level=LogLevel.INFO,
                message="Successfully published post to LinkedIn",
                context=f"Post ID: {response_data.get('post_id', '')}"
            )
            
            return response_data
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error publishing to LinkedIn: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Error publishing to LinkedIn: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)


# Initialize services
_linkedin_auth = None
_linkedin_token_manager = None
_linkedin_publisher = None


def get_linkedin_auth() -> LinkedInAuth:
    global _linkedin_auth
    if not _linkedin_auth:
        _linkedin_auth = LinkedInAuth()
    return _linkedin_auth


def get_linkedin_token_manager() -> LinkedInTokenManager:
    global _linkedin_token_manager, _linkedin_auth
    if not _linkedin_token_manager:
        if not _linkedin_auth:
            _linkedin_auth = LinkedInAuth()
        _linkedin_token_manager = LinkedInTokenManager(_linkedin_auth)
    return _linkedin_token_manager


def get_linkedin_publisher() -> LinkedInPublisher:
    global _linkedin_publisher, _linkedin_token_manager
    if not _linkedin_publisher:
        if not _linkedin_token_manager:
            _linkedin_token_manager = get_linkedin_token_manager()
        _linkedin_publisher = LinkedInPublisher(_linkedin_token_manager)
    return _linkedin_publisher
