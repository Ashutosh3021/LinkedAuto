from flask import Blueprint, request, jsonify, session, redirect
from config import Config
from services import get_linkedin_auth, get_linkedin_token_manager, get_linkedin_publisher
from database import LinkedInCredential, db


linkedin_bp = Blueprint('linkedin', __name__)


@linkedin_bp.route('/linkedin/auth', methods=['GET'])
def linkedin_auth():
    auth = get_linkedin_auth()
    auth_url, state = auth.get_authorization_url()
    session['linkedin_state'] = state
    return jsonify({'success': True, 'auth_url': auth_url}), 200


@linkedin_bp.route('/linkedin/callback', methods=['GET'])
def linkedin_callback():
    code = request.args.get('code')
    state = request.args.get('state')
    
    if not code:
        return jsonify({'success': False, 'error': 'Missing authorization code'}), 400
    
    if state != session.get('linkedin_state'):
        return jsonify({'success': False, 'error': 'Invalid state parameter'}), 400
    
    try:
        auth = get_linkedin_auth()
        token = auth.exchange_code_for_token(code)
        
        token_manager = get_linkedin_token_manager()
        credential = token_manager.save_credential(token)
        
        publisher = get_linkedin_publisher()
        user_info = publisher.get_user_info(credential.access_token)
        if user_info and 'sub' in user_info:
            credential.linkedin_user_id = user_info['sub']
            db.session.commit()
        
        return redirect('/settings')
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@linkedin_bp.route('/api/linkedin/status', methods=['GET'])
def linkedin_status():
    try:
        token_manager = get_linkedin_token_manager()
        credential = token_manager.get_valid_credential()
        
        if not credential:
            return jsonify({'success': True, 'is_connected': False, 'message': 'Not connected to LinkedIn'}), 200
        
        return jsonify({
            'success': True,
            'is_connected': True,
            'linkedin_user_id': credential.linkedin_user_id,
            'token_expires_at': credential.token_expires_at.isoformat(),
            'refresh_token_expires_at': credential.refresh_token_expires_at.isoformat() if credential.refresh_token_expires_at else None
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@linkedin_bp.route('/api/linkedin/disconnect', methods=['POST'])
def linkedin_disconnect():
    try:
        credentials = LinkedInCredential.query.all()
        for cred in credentials:
            db.session.delete(cred)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Successfully disconnected from LinkedIn'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
