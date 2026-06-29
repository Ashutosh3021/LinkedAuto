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
    pending_jobs = ConnectionJob.query.filter(ConnectionJob.status == PostStatus.PENDING).count()
    running_jobs = ConnectionJob.query.filter(ConnectionJob.status == PostStatus.RUNNING).count()
    completed_jobs = ConnectionJob.query.filter(ConnectionJob.status == PostStatus.COMPLETED).count()
    total_configs = ConnectionConfiguration.query.count()
    
    # Today's connection stats
    today = datetime.utcnow().strftime("%Y-%m-%d")
    today_stats = DailyConnectionStats.query.filter_by(date=today).first()
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
                'created_at': post.created_at.isoformat()
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
                'scheduled_at': post.scheduled_at.isoformat() if post.scheduled_at else None,
                'retry_count': post.retry_count,
                'last_error': post.last_error,
                'created_at': post.created_at.isoformat()
            }
            for post in posts
        ]
    })


@dashboard_bp.route('/api/dashboard/logs', methods=['GET'])
def get_publishing_logs():
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


@dashboard_bp.route('/api/dashboard/activity', methods=['GET'])
def get_recent_activity():
    # Combine posts and logs for recent activity
    recent_posts = Post.query.order_by(Post.updated_at.desc()).limit(20).all()
    recent_logs = Log.query.order_by(Log.created_at.desc()).limit(20).all()
    
    activities = []
    
    for post in recent_posts:
        activities.append({
            'type': 'post',
            'id': post.id,
            'title': post.title,
            'status': post.status.value,
            'timestamp': (post.updated_at or post.created_at).isoformat(),
            'message': f'Post "{post.title}" is {post.status.value}'
        })
    
    for log in recent_logs:
        activities.append({
            'type': 'log',
            'id': log.id,
            'level': log.level.value,
            'message': log.message,
            'timestamp': log.created_at.isoformat()
        })
    
    # Sort activities by timestamp descending
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    return jsonify({
        'success': True,
        'data': activities[:50]
    })


@dashboard_bp.route('/api/dashboard/health', methods=['GET'])
def get_app_health():
    try:
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        
        # Check for critical errors in last hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_errors = Log.query.filter(
            Log.level == LogLevel.ERROR,
            Log.created_at >= one_hour_ago
        ).count()
        
        health_status = 'healthy' if recent_errors == 0 else 'degraded'
        
        return jsonify({
            'success': True,
            'data': {
                'status': health_status,
                'database': 'connected',
                'recent_errors': recent_errors,
                'timestamp': datetime.utcnow().isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            'success': True,
            'data': {
                'status': 'unhealthy',
                'database': 'disconnected',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
        })


@dashboard_bp.route('/api/dashboard/scheduler', methods=['GET'])
def get_scheduler_status():
    try:
        scheduler = get_scheduler()
        if not scheduler or not scheduler.scheduler:
            return jsonify({
                'success': True,
                'data': {
                    'status': 'not_initialized',
                    'jobs': []
                }
            })
        
        jobs = scheduler.scheduler.get_jobs()
        
        return jsonify({
            'success': True,
            'data': {
                'status': 'running' if scheduler.scheduler.running else 'stopped',
                'jobs': [
                    {
                        'id': job.id,
                        'name': job.name,
                        'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None
                    }
                    for job in jobs
                ]
            }
        })
    except Exception as e:
        return jsonify({
            'success': True,
            'data': {
                'status': 'error',
                'error': str(e),
                'jobs': []
            }
        })


@dashboard_bp.route('/api/dashboard/config', methods=['GET'])
def get_config_summary():
    configs = Config.query.all()
    linkedin_cred = LinkedInCredential.query.order_by(LinkedInCredential.updated_at.desc()).first()
    
    config_dict = {c.key: c.value for c in configs}
    
    return jsonify({
        'success': True,
        'data': {
            'configurations': config_dict,
            'linkedin': {
                'connected': linkedin_cred is not None,
                'user_id': linkedin_cred.linkedin_user_id if linkedin_cred else None,
                'token_expires_at': linkedin_cred.token_expires_at.isoformat() if (linkedin_cred and linkedin_cred.token_expires_at) else None
            }
        }
    })

