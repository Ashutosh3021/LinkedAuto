import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from sqlalchemy.exc import SQLAlchemyError
from config import Config
from database import db, Post, PostStatus, Log, LogLevel, PostHelper, LogHelper
from utils import retry_db_operation
from .linkedin import get_linkedin_publisher


logger = logging.getLogger(__name__)

# Global variables for app and scheduler service
_app = None
_scheduler_instance = None

# Constants
RETRY_INTERVALS = [15, 60, 360]
MAX_RETRIES = 3


@retry_db_operation(max_retries=3)
def _process_pending_posts():
    """Standalone function to process pending posts (picklable)"""
    if not _app:
        logger.warning("App not initialized, skipping post processing")
        return
    
    with _app.app_context():
        try:
            now = datetime.utcnow()
            
            scheduled_posts = Post.query.filter(
                Post.status == PostStatus.SCHEDULED,
                Post.scheduled_at <= now
            ).all()
            
            for post in scheduled_posts:
                _execute_post_job(post)
        except SQLAlchemyError as e:
            logger.error(f"Database error in _process_pending_posts: {str(e)}", exc_info=True)
            # Rollback on any SQLAlchemy error to keep session clean
            db.session.rollback()
            raise  # Re-raise to trigger retry


@retry_db_operation(max_retries=2)
def _execute_post_job(post: Post):
    try:
        logger.info(f"Executing post job for post {post.id}")
        
        publisher = get_linkedin_publisher()
        result = publisher.publish_post(post.content)
        
        post.status = PostStatus.PUBLISHED
        post.published_at = datetime.utcnow()
        post.linkedin_post_id = result.get('post_id') if result else None
        post.last_error = None
        post.retry_count = 0
        db.session.commit()
        
        LogHelper.create(
            Log,
            level=LogLevel.INFO,
            message=f"Post {post.id} published successfully",
            context=f"Post ID: {post.id}, LinkedIn Post ID: {post.linkedin_post_id}"
        )
        
    except SQLAlchemyError as e:
        logger.error(f"Database error publishing post {post.id}: {str(e)}", exc_info=True)
        db.session.rollback()
        raise  # Re-raise to trigger retry
    except Exception as e:
        logger.error(f"Error publishing post {post.id}: {e}")
        db.session.rollback()  # Always rollback on exception
        _handle_post_failure(post, str(e))


def _handle_post_failure(post: Post, error_message: str):
    try:
        post.retry_count += 1
        post.last_error = error_message
        
        LogHelper.create(
            Log,
            level=LogLevel.ERROR,
            message=f"Post {post.id} failed to publish: {error_message}",
            context=f"Post ID: {post.id}, Retry count: {post.retry_count}"
        )
        
        if post.retry_count >= MAX_RETRIES:
            post.status = PostStatus.FAILED
            db.session.commit()
            logger.warning(f"Post {post.id} failed after {MAX_RETRIES} retries")
        else:
            retry_minutes = RETRY_INTERVALS[post.retry_count - 1]
            next_attempt = datetime.utcnow() + timedelta(minutes=retry_minutes)
            post.scheduled_at = next_attempt
            db.session.commit()
            logger.info(f"Post {post.id} will retry in {retry_minutes} minutes at {next_attempt}")
    except SQLAlchemyError as e:
        logger.error(f"Database error handling post failure {post.id}: {str(e)}", exc_info=True)
        db.session.rollback()


class SchedulerService:
    def __init__(self, app):
        self.app = app
        self.scheduler = None
        
    def init_scheduler(self):
        # Use the same connection pool settings for APScheduler job store
        jobstores = {
            'default': SQLAlchemyJobStore(
                url=Config.SQLALCHEMY_DATABASE_URI,
                engine_options=Config.SQLALCHEMY_ENGINE_OPTIONS if hasattr(Config, 'SQLALCHEMY_ENGINE_OPTIONS') 
                    else ({'connect_args': {'check_same_thread': False}} if 'sqlite' in Config.SQLALCHEMY_DATABASE_URI else {})
            )
        }
        executors = {
            'default': ThreadPoolExecutor(10)
        }
        job_defaults = {
            'coalesce': True,  # Coalesce missed jobs
            'max_instances': 1,
            'misfire_grace_time': 300  # 5 minutes grace time for misfired jobs
        }
        
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='UTC'
        )
        
        self.scheduler.add_job(
            _process_pending_posts,
            'interval',
            minutes=1,
            id='process_pending_posts',
            name='Process pending posts every minute',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("Scheduler initialized")
    
    @retry_db_operation(max_retries=2)
    def schedule_post(self, post_id: int, scheduled_at: datetime) -> Optional[str]:
        with self.app.app_context():
            post = PostHelper.get(Post, post_id)
            if not post:
                return None
            
            job_id = f"post_{post_id}"
            post.scheduled_at = scheduled_at
            post.status = PostStatus.SCHEDULED
            post.job_id = job_id
            db.session.commit()
            
            LogHelper.create(
                Log,
                level=LogLevel.INFO,
                message=f"Post {post_id} scheduled for {scheduled_at}",
                context=f"Post ID: {post_id}, Scheduled at: {scheduled_at}"
            )
            
            return job_id
    
    @retry_db_operation(max_retries=2)
    def cancel_schedule(self, post_id: int) -> bool:
        with self.app.app_context():
            post = PostHelper.get(Post, post_id)
            if not post:
                return False
            
            post.status = PostStatus.DRAFT
            post.scheduled_at = None
            post.job_id = None
            post.retry_count = 0
            post.last_error = None
            db.session.commit()
            
            LogHelper.create(
                Log,
                level=LogLevel.INFO,
                message=f"Post {post_id} schedule canceled",
                context=f"Post ID: {post_id}"
            )
            
            return True
    
    @retry_db_operation(max_retries=2)
    def reschedule_post(self, post_id: int, new_scheduled_at: datetime) -> bool:
        with self.app.app_context():
            post = PostHelper.get(Post, post_id)
            if not post:
                return False
            
            post.scheduled_at = new_scheduled_at
            post.retry_count = 0
            post.last_error = None
            db.session.commit()
            
            LogHelper.create(
                Log,
                level=LogLevel.INFO,
                message=f"Post {post_id} rescheduled to {new_scheduled_at}",
                context=f"Post ID: {post_id}, New scheduled at: {new_scheduled_at}"
            )
            
            return True
    
    @retry_db_operation(max_retries=2)
    def get_queue(self) -> List[Dict]:
        with self.app.app_context():
            posts = Post.query.filter(
                Post.status.in_([PostStatus.SCHEDULED, PostStatus.FAILED])
            ).order_by(Post.scheduled_at).all()
            
            return [
                {
                    'id': post.id,
                    'title': post.title,
                    'content': post.content,
                    'status': post.status.value,
                    'scheduled_at': post.scheduled_at.isoformat() if post.scheduled_at else None,
                    'retry_count': post.retry_count,
                    'last_error': post.last_error,
                    'job_id': post.job_id
                }
                for post in posts
            ]
    
    def shutdown(self):
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            logger.info("Scheduler shut down")


def get_scheduler(app=None):
    global _scheduler_instance, _app
    if _scheduler_instance is None and app is not None:
        _app = app
        _scheduler_instance = SchedulerService(app)
        _scheduler_instance.init_scheduler()
    return _scheduler_instance
