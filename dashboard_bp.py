from flask import Blueprint, jsonify
from datetime import datetime, timedelta
from models import (
    db, Post, PostStatus, Log, LogLevel,
    Config, LinkedInCredential, ConnectionJob,
    ConnectionConfiguration, LinkedInProfile, DailyConnectionStats
)
from scheduler import get_scheduler

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    # Count posts by status
    draft_count = Post.query.filter(Post.status == PostStatus.DRAFT).count()
    scheduled_count = Post.query.filter(Post.status == PostStatus.SCHEDULED).count()
    published_count = Post.query.filter(Post.status == PostStatus.PUBLISHED).count()
    failed_count = Post.query.filter(Post.status == PostStatus.FAILED).count()
    
    # Count total posts
    total_posts = Post.query.count()
    
    # Count logs by level
    info_logs = Log.query.filter(Log.level == LogLevel.INFO).count()
    warning_logs = Log.query.filter(Log.level == LogLevel.WARNING).count()
    error_logs = Log.query.filter(Log.level == LogLevel.ERROR).count()
    
    # Check LinkedIn connection
    linkedin_connected = LinkedInCredential.query.count() > 0
    
    # Connection stats
    total_profiles = LinkedInProfile.query.count()
    pending_jobs = ConnectionJob.query.filter(ConnectionJob.status == ConnectionJobStatus.PENDING).count()
    running_jobs = ConnectionJob.query.filter(ConnectionJob.status == ConnectionJobStatus.RUNNING).count()
    completed_jobs = ConnectionJob.query.filter(ConnectionJob.status == ConnectionJobStatus.COMPLETED).count()
    total_configs = ConnectionConfiguration.query.count()
    
    # Today's connection stats
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    today_stats = DailyConnectionStats.query.filter(DailyConnectionStats.date == today_str).first()
    today_sent = today_stats.requests_sent if today_stats else 0
    today_accepted = today_stats.requests_accepted if today_stats else 0
    today_failed = today_stats.requests_failed if today_stats else 0
    
    return jsonify({
        'success': True,
        'data': {
            'posts': {
                'total': total_posts,
                'draft': draft_count,
                'scheduled': scheduled_count,
                'published': published_count,
                'failed': failed_count
            },
            'logs': {
                'info': info_logs,
                'warning': warning_logs,
                'error': error_logs
            },
            'linkedin': {
                'connected': linkedin_connected
            },
            'connections': {
                'total_profiles': total_profiles,
                'pending_jobs': pending_jobs,
                'running_jobs': running_jobs,
                'completed_jobs': completed_jobs,
                'total_configs': total_configs,
                'today': {
                    'sent': today_sent,
                    'accepted': today_accepted,
                    'failed': today_failed
                }
            }
        }
    })


@dashboard_bp.route('/api/dashboard/posts/generated', methods=['GET'])
def get_generated_posts():
    posts = Post.query.order_by(Post.created_at.desc()).limit(50).all()
    return jsonify({
        'success': True,
        'data': [
            {
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'status': post.status.value,
                'scheduled_at': post.scheduled_at.isoformat() if post.scheduled_at else None,
                'published_at': post.published_at.isoformat() if post.published_at else None,
                'linkedin_post_id': post.linkedin_post_id,
                'created_at': post.created_at.isoformat(),
                'updated_at': post.updated_at.isoformat()
            }
            for post in posts
        ]
    })


@dashboard_bp.route('/api/dashboard/posts/scheduled', methods=['GET'])
def get_scheduled_posts():
    posts = Post.query.filter(
        Post.status == PostStatus.SCHEDULED
    ).order_by(Post.scheduled_at.asc()).all()
    return jsonify({
        'success': True,
        'data': [
            {
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'status': post.status.value,
                'scheduled_at': post.scheduled_at.isoformat() if post.scheduled_at else None,
                'published_at': post.published_at.isoformat() if post.published_at else None,
                'linkedin_post_id': post.linkedin_post_id,
                'created_at': post.created_at.isoformat()
            }
            for post in posts
        ]
    })


@dashboard_bp.route('/api/dashboard/logs', methods=['GET'])
def get_logs():
    logs = Log.query.order_by(Log.created_at.desc()).limit(100).all()
    return jsonify({
        'success': True,
        'data': [
            {
                'id': log.id,
                'level': log.level.value,
                'message': log.message,
                'context': log.context,
                'created_at': log.created_at.isoformat()
            }
            for log in logs
        ]
    })
