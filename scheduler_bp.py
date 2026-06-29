from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from scheduler import get_scheduler
from models import Post
from database import PostHelper


scheduler_bp = Blueprint('scheduler', __name__)


@scheduler_bp.route('/api/schedule', methods=['POST'])
def schedule_post():
    try:
        data = request.get_json()
        
        if not data or 'post_id' not in data or 'scheduled_at' not in data:
            return jsonify({'error': 'post_id and scheduled_at are required'}), 400
        
        post_id = data['post_id']
        scheduled_at_str = data['scheduled_at']
        
        try:
            scheduled_at = datetime.fromisoformat(scheduled_at_str)
        except ValueError:
            return jsonify({'error': 'Invalid scheduled_at format. Use ISO 8601 format.'}), 400
        
        scheduler = get_scheduler(current_app._get_current_object())
        job_id = scheduler.schedule_post(post_id, scheduled_at)
        
        if job_id:
            return jsonify({'success': True, 'job_id': job_id}), 200
        else:
            return jsonify({'error': 'Post not found'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Failed to schedule post: {str(e)}'}), 500


@scheduler_bp.route('/api/schedule/<int:post_id>', methods=['DELETE'])
def cancel_schedule(post_id):
    try:
        scheduler = get_scheduler(current_app._get_current_object())
        success = scheduler.cancel_schedule(post_id)
        
        if success:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'error': 'Post not found'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Failed to cancel schedule: {str(e)}'}), 500


@scheduler_bp.route('/api/schedule/<int:post_id>', methods=['PUT'])
def reschedule_post(post_id):
    try:
        data = request.get_json()
        
        if not data or 'scheduled_at' not in data:
            return jsonify({'error': 'scheduled_at is required'}), 400
        
        scheduled_at_str = data['scheduled_at']
        
        try:
            scheduled_at = datetime.fromisoformat(scheduled_at_str)
        except ValueError:
            return jsonify({'error': 'Invalid scheduled_at format. Use ISO 8601 format.'}), 400
        
        scheduler = get_scheduler(current_app._get_current_object())
        success = scheduler.reschedule_post(post_id, scheduled_at)
        
        if success:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'error': 'Post not found'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Failed to reschedule post: {str(e)}'}), 500


@scheduler_bp.route('/api/queue', methods=['GET'])
def view_queue():
    try:
        scheduler = get_scheduler(current_app._get_current_object())
        queue = scheduler.get_queue()
        return jsonify({'success': True, 'queue': queue}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get queue: {str(e)}'}), 500
