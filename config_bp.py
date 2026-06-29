from flask import Blueprint, request, jsonify
from models import db, Config
from database import ConfigHelper
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
