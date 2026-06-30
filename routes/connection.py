import threading
import asyncio
from flask import Blueprint, request, jsonify, current_app
from database import (
    db, ConnectionConfiguration, LinkedInProfile,
    ConnectionJob, ConnectionJobStatus, DailyConnectionStats
)
from services import get_connection_service

connection_bp = Blueprint('connection', __name__)


def run_async_task(job_id):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        service = get_connection_service(current_app._get_current_object())
        loop.run_until_complete(service.run_connection_job(job_id))
    finally:
        loop.close()


# Configuration Endpoints
@connection_bp.route('/api/connections/configs', methods=['GET'])
def get_configs():
    configs = ConnectionConfiguration.query.all()
    return jsonify({
        'success': True,
        'data': [
            {
                'id': c.id,
                'name': c.name,
                'is_active': c.is_active,
                'company': c.company,
                'role': c.role,
                'industry': c.industry,
                'location': c.location,
                'university': c.university,
                'keywords': c.keywords,
                'daily_limit': c.daily_limit,
                'request_cooldown': c.request_cooldown,
                'connection_message': c.connection_message,
                'created_at': c.created_at.isoformat()
            }
            for c in configs
        ]
    })


@connection_bp.route('/api/connections/configs', methods=['POST'])
def create_config():
    data = request.get_json()
    config = ConnectionConfiguration(
        name=data['name'],
        is_active=data.get('is_active', True),
        company=data.get('company'),
        role=data.get('role'),
        industry=data.get('industry'),
        location=data.get('location'),
        university=data.get('university'),
        keywords=data.get('keywords'),
        daily_limit=data.get('daily_limit', 20),
        request_cooldown=data.get('request_cooldown', 5),
        connection_message=data.get('connection_message')
    )
    db.session.add(config)
    db.session.commit()
    return jsonify({'success': True, 'data': {'id': config.id}}), 201


@connection_bp.route('/api/connections/configs/<int:config_id>', methods=['PUT'])
def update_config(config_id):
    config = ConnectionConfiguration.query.get(config_id)
    if not config:
        return jsonify({'success': False, 'error': 'Config not found'}), 404
    data = request.get_json()
    for key, value in data.items():
        if hasattr(config, key):
            setattr(config, key, value)
    db.session.commit()
    return jsonify({'success': True})


@connection_bp.route('/api/connections/configs/<int:config_id>', methods=['DELETE'])
def delete_config(config_id):
    config = ConnectionConfiguration.query.get(config_id)
    if not config:
        return jsonify({'success': False, 'error': 'Config not found'}), 404
    db.session.delete(config)
    db.session.commit()
    return jsonify({'success': True})


# Job Endpoints
@connection_bp.route('/api/connections/jobs', methods=['GET'])
def get_jobs():
    jobs = ConnectionJob.query.order_by(ConnectionJob.created_at.desc()).all()
    return jsonify({
        'success': True,
        'data': [
            {
                'id': j.id,
                'name': j.name,
                'status': j.status.value,
                'configuration_id': j.configuration_id,
                'target_count': j.target_count,
                'completed_count': j.completed_count,
                'failed_count': j.failed_count,
                'skipped_count': j.skipped_count,
                'started_at': j.started_at.isoformat() if j.started_at else None,
                'completed_at': j.completed_at.isoformat() if j.completed_at else None,
                'error_message': j.error_message,
                'created_at': j.created_at.isoformat()
            }
            for j in jobs
        ]
    })


@connection_bp.route('/api/connections/jobs', methods=['POST'])
def create_job():
    data = request.get_json()
    job = ConnectionJob(
        name=data['name'],
        configuration_id=data.get('configuration_id'),
        target_count=data.get('target_count')
    )
    db.session.add(job)
    db.session.commit()
    return jsonify({'success': True, 'data': {'id': job.id}}), 201


@connection_bp.route('/api/connections/jobs/<int:job_id>/start', methods=['POST'])
def start_job(job_id):
    job = ConnectionJob.query.get(job_id)
    if not job:
        return jsonify({'success': False, 'error': 'Job not found'}), 404
    
    # Start job in background thread
    thread = threading.Thread(target=run_async_task, args=(job_id,), daemon=True)
    thread.start()
    
    return jsonify({'success': True, 'message': 'Job started'})


# Profiles Endpoints
@connection_bp.route('/api/connections/profiles', methods=['GET'])
def get_profiles():
    job_id = request.args.get('job_id')
    query = LinkedInProfile.query
    if job_id:
        query = query.filter_by(job_id=int(job_id))
    profiles = query.order_by(LinkedInProfile.created_at.desc()).limit(100).all()
    return jsonify({
        'success': True,
        'data': [
            {
                'id': p.id,
                'profile_url': p.profile_url,
                'name': p.name,
                'title': p.title,
                'company': p.company,
                'location': p.location,
                'industry': p.industry,
                'university': p.university,
                'is_connected': p.is_connected,
                'connection_request_sent': p.connection_request_sent,
                'connection_request_sent_at': p.connection_request_sent_at.isoformat() if p.connection_request_sent_at else None,
                'job_id': p.job_id,
                'created_at': p.created_at.isoformat()
            }
            for p in profiles
        ]
    })


# Daily Stats
@connection_bp.route('/api/connections/stats/daily', methods=['GET'])
def get_daily_stats():
    stats = DailyConnectionStats.query.order_by(DailyConnectionStats.date.desc()).limit(30).all()
    return jsonify({
        'success': True,
        'data': [
            {
                'id': s.id,
                'date': s.date,
                'requests_sent': s.requests_sent,
                'requests_accepted': s.requests_accepted,
                'requests_failed': s.requests_failed
            }
            for s in stats
        ]
    })

