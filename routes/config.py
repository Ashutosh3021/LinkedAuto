from flask import Blueprint, request, jsonify
from database import db, Config, AIProvider, LinkedInAppCredentials, ConfigHelper
from utils import encrypt_api_key
import json

config_bp = Blueprint('config', __name__, url_prefix='/api/config')

def validate_config(data):
    errors = []
    required_fields = ['api_keys', 'domains', 'topics', 'projects', 'tone', 'audience', 'schedule', 'cooldown', 'posting_days', 'posting_times', 'character_limits']
    for field in required_fields:
        if field not in data:
            errors.append(f'Missing required field: {field}')
    return errors

@config_bp.route('/', methods=['POST'])
def save_config():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        errors = validate_config(data)
        if errors:
            return jsonify({'error': 'Validation failed', 'details': errors}), 400
        
        for key, value in data.items():
            ConfigHelper.set_value(f'posting_{key}', json.dumps(value) if isinstance(value, (dict, list)) else str(value))
        
        return jsonify({'success': True, 'message': 'Configuration saved successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@config_bp.route('/', methods=['GET'])
def load_config():
    try:
        config = {}
        config_keys = [
            'posting_api_keys', 'posting_domains', 'posting_topics', 'posting_projects',
            'posting_tone', 'posting_audience', 'posting_schedule', 'posting_cooldown',
            'posting_posting_days', 'posting_posting_times', 'posting_character_limits'
        ]
        
        for key in config_keys:
            config_entry = ConfigHelper.get_by_key(key)
            if config_entry:
                clean_key = key.replace('posting_', '')
                try:
                    config[clean_key] = json.loads(config_entry.value)
                except json.JSONDecodeError:
                    config[clean_key] = config_entry.value
        
        return jsonify({'success': True, 'data': config}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@config_bp.route('/', methods=['PUT'])
def update_config():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        for key, value in data.items():
            ConfigHelper.set_value(f'posting_{key}', json.dumps(value) if isinstance(value, (dict, list)) else str(value))
        
        return jsonify({'success': True, 'message': 'Configuration updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@config_bp.route('/', methods=['DELETE'])
def delete_config():
    try:
        config_keys = [
            'posting_api_keys', 'posting_domains', 'posting_topics', 'posting_projects',
            'posting_tone', 'posting_audience', 'posting_schedule', 'posting_cooldown',
            'posting_posting_days', 'posting_posting_times', 'posting_character_limits'
        ]
        
        for key in config_keys:
            config_entry = ConfigHelper.get_by_key(key)
            if config_entry:
                db.session.delete(config_entry)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Configuration deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# AI Provider endpoints
def validate_provider(data):
    errors = []
    if not data.get('name'):
        errors.append("Provider name is required")
    if not data.get('model_name'):
        errors.append("Model name is required")
    if not data.get('api_key'):
        errors.append("API key is required")
    if not data.get('base_url'):
        errors.append("Base URL is required")
    return errors

@config_bp.route('/providers', methods=['GET'])
def get_providers():
    try:
        providers = AIProvider.query.all()
        return jsonify({
            'success': True,
            'data': [
                {
                    'id': p.id,
                    'name': p.name,
                    'model_name': p.model_name,
                    'base_url': p.base_url,
                    'is_active': p.is_active,
                    'created_at': p.created_at.isoformat() if p.created_at else None,
                    'updated_at': p.updated_at.isoformat() if p.updated_at else None
                }
                for p in providers
            ]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@config_bp.route('/providers', methods=['POST'])
def create_provider():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        errors = validate_provider(data)
        if errors:
            return jsonify({'error': 'Validation failed', 'details': errors}), 400
        
        # Check if provider name already exists
        existing = AIProvider.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({'error': 'Provider with this name already exists'}), 400
        
        provider = AIProvider(
            name=data['name'],
            model_name=data['model_name'],
            api_key_encrypted=encrypt_api_key(data['api_key']),
            base_url=data['base_url'],
            is_active=data.get('is_active', False)
        )
        
        # If setting as active, deactivate others
        if provider.is_active:
            AIProvider.query.update({'is_active': False})
        
        db.session.add(provider)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Provider created successfully',
            'data': {
                'id': provider.id,
                'name': provider.name,
                'model_name': provider.model_name,
                'base_url': provider.base_url,
                'is_active': provider.is_active
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@config_bp.route('/providers/<int:provider_id>', methods=['PUT'])
def update_provider(provider_id):
    try:
        provider = AIProvider.query.get(provider_id)
        if not provider:
            return jsonify({'error': 'Provider not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        if 'name' in data:
            # Check if new name is unique
            existing = AIProvider.query.filter_by(name=data['name']).first()
            if existing and existing.id != provider_id:
                return jsonify({'error': 'Provider with this name already exists'}), 400
            provider.name = data['name']
        
        if 'model_name' in data:
            provider.model_name = data['model_name']
        
        if 'api_key' in data:
            provider.api_key_encrypted = encrypt_api_key(data['api_key'])
        
        if 'base_url' in data:
            provider.base_url = data['base_url']
        
        if 'is_active' in data:
            if data['is_active']:
                AIProvider.query.update({'is_active': False})
            provider.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Provider updated successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@config_bp.route('/providers/<int:provider_id>', methods=['DELETE'])
def delete_provider(provider_id):
    try:
        provider = AIProvider.query.get(provider_id)
        if not provider:
            return jsonify({'error': 'Provider not found'}), 404
        
        db.session.delete(provider)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Provider deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@config_bp.route('/providers/<int:provider_id>/activate', methods=['POST'])
def activate_provider(provider_id):
    try:
        provider = AIProvider.query.get(provider_id)
        if not provider:
            return jsonify({'error': 'Provider not found'}), 404
        
        # Deactivate all others
        AIProvider.query.update({'is_active': False})
        provider.is_active = True
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Provider activated successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# LinkedIn App Credentials endpoints
def validate_linkedin_app_creds(data):
    errors = []
    if not data.get('client_id'):
        errors.append("Client ID is required")
    if not data.get('client_secret'):
        errors.append("Client Secret is required")
    return errors

@config_bp.route('/linkedin-app', methods=['GET'])
def get_linkedin_app_creds():
    try:
        creds = LinkedInAppCredentials.query.all()
        return jsonify({
            'success': True,
            'data': [
                {
                    'id': c.id,
                    'client_id': c.client_id,
                    'redirect_uri': c.redirect_uri,
                    'is_active': c.is_active,
                    'created_at': c.created_at.isoformat() if c.created_at else None,
                    'updated_at': c.updated_at.isoformat() if c.updated_at else None
                }
                for c in creds
            ]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@config_bp.route('/linkedin-app', methods=['POST'])
def create_linkedin_app_creds():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        errors = validate_linkedin_app_creds(data)
        if errors:
            return jsonify({'error': 'Validation failed', 'details': errors}), 400
        
        creds = LinkedInAppCredentials(
            client_id=data['client_id'],
            client_secret_encrypted=encrypt_api_key(data['client_secret']),
            redirect_uri=data.get('redirect_uri', 'http://localhost:5000/linkedin/callback'),
            is_active=data.get('is_active', False)
        )
        
        # If setting as active, deactivate others
        if creds.is_active:
            LinkedInAppCredentials.query.update({'is_active': False})
        
        db.session.add(creds)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'LinkedIn app credentials created successfully',
            'data': {
                'id': creds.id,
                'client_id': creds.client_id,
                'redirect_uri': creds.redirect_uri,
                'is_active': creds.is_active
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@config_bp.route('/linkedin-app/<int:creds_id>', methods=['PUT'])
def update_linkedin_app_creds(creds_id):
    try:
        creds = LinkedInAppCredentials.query.get(creds_id)
        if not creds:
            return jsonify({'error': 'Credentials not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        if 'client_id' in data:
            creds.client_id = data['client_id']
        
        if 'client_secret' in data:
            creds.client_secret_encrypted = encrypt_api_key(data['client_secret'])
        
        if 'redirect_uri' in data:
            creds.redirect_uri = data['redirect_uri']
        
        if 'is_active' in data:
            if data['is_active']:
                LinkedInAppCredentials.query.update({'is_active': False})
            creds.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'LinkedIn app credentials updated successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@config_bp.route('/linkedin-app/<int:creds_id>', methods=['DELETE'])
def delete_linkedin_app_creds(creds_id):
    try:
        creds = LinkedInAppCredentials.query.get(creds_id)
        if not creds:
            return jsonify({'error': 'Credentials not found'}), 404
        
        db.session.delete(creds)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'LinkedIn app credentials deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@config_bp.route('/linkedin-app/<int:creds_id>/activate', methods=['POST'])
def activate_linkedin_app_creds(creds_id):
    try:
        creds = LinkedInAppCredentials.query.get(creds_id)
        if not creds:
            return jsonify({'error': 'Credentials not found'}), 404
        
        # Deactivate all others
        LinkedInAppCredentials.query.update({'is_active': False})
        creds.is_active = True
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'LinkedIn app credentials activated successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
