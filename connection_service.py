import asyncio
import logging
from datetime import datetime, date
from typing import List, Dict, Optional
from models import (
    db, ConnectionConfiguration, LinkedInProfile,
    ConnectionJob, ConnectionJobStatus, DailyConnectionStats,
    Log, LogLevel
)
from database import LogHelper
from browser_service import get_browser_service

logger = logging.getLogger(__name__)


class ConnectionService:
    def __init__(self, app):
        self.app = app

    def get_daily_stats(self, d: date = None) -> DailyConnectionStats:
        target_date = d or date.today()
        date_str = target_date.strftime("%Y-%m-%d")
        stats = DailyConnectionStats.query.filter_by(date=date_str).first()
        if not stats:
            stats = DailyConnectionStats(date=date_str)
            db.session.add(stats)
            db.session.commit()
        return stats

    async def run_connection_job(self, job_id: int):
        with self.app.app_context():
            job = ConnectionJob.query.get(job_id)
            if not job:
                logger.error(f"Job {job_id} not found")
                return
            
            config = ConnectionConfiguration.query.get(job.configuration_id)
            if not config:
                logger.error(f"Configuration not found for job {job_id}")
                job.status = ConnectionJobStatus.FAILED
                job.error_message = "Configuration not found"
                db.session.commit()
                return
            
            browser = get_browser_service()
            
            try:
                job.status = ConnectionJobStatus.RUNNING
                job.started_at = datetime.utcnow()
                db.session.commit()
                
                # Start browser
                if not browser.browser:
                    await browser.start_browser()
                
                # Search profiles
                profiles = await browser.search_profiles(
                    keywords=config.keywords,
                    company=config.company,
                    role=config.role,
                    location=config.location,
                    industry=config.industry,
                    university=config.university,
                    max_results=job.target_count or 50
                )
                
                LogHelper.create(
                    Log,
                    level=LogLevel.INFO,
                    message=f"Job {job_id}: Found {len(profiles)} profiles",
                    context=f"Job ID: {job_id}"
                )
                
                # Process profiles
                daily_stats = self.get_daily_stats()
                sent_count = 0
                
                for profile_data in profiles:
                    if daily_stats.requests_sent >= config.daily_limit:
                        logger.info(f"Daily limit reached: {config.daily_limit}")
                        break
                    
                    if job.completed_count >= (job.target_count or float('inf')):
                        break
                    
                    try:
                        existing_profile = LinkedInProfile.query.filter_by(profile_url=profile_data['profile_url']).first()
                        if existing_profile:
                            job.skipped_count += 1
                            db.session.commit()
                            continue
                        
                        profile = LinkedInProfile(
                            profile_url=profile_data['profile_url'],
                            name=profile_data.get('name'),
                            title=profile_data.get('title'),
                            location=profile_data.get('location'),
                            job_id=job.id
                        )
                        db.session.add(profile)
                        db.session.commit()
                        
                        # Send connection request
                        success = await browser.send_connection_request(
                            profile_data['profile_url'],
                            config.connection_message
                        )
                        
                        if success:
                            profile.connection_request_sent = True
                            profile.connection_request_sent_at = datetime.utcnow()
                            job.completed_count += 1
                            daily_stats.requests_sent += 1
                            
                            LogHelper.create(
                                Log,
                                level=LogLevel.INFO,
                                message=f"Sent connection to {profile.name}",
                                context=f"Profile: {profile.profile_url}, Job: {job_id}"
                            )
                        else:
                            job.failed_count += 1
                            LogHelper.create(
                                Log,
                                level=LogLevel.WARNING,
                                message=f"Failed to send connection to {profile.name}",
                                context=f"Profile: {profile.profile_url}, Job: {job_id}"
                            )
                        
                        db.session.commit()
                        
                        # Cooldown
                        await asyncio.sleep(config.request_cooldown)
                    except Exception as e:
                        logger.error(f"Error processing profile: {e}")
                        job.failed_count += 1
                        LogHelper.create(
                            Log,
                            level=LogLevel.ERROR,
                            message=f"Error processing profile: {e}",
                            context=f"Job: {job_id}"
                        )
                        db.session.commit()
                
                # Mark job complete
                job.status = ConnectionJobStatus.COMPLETED
                job.completed_at = datetime.utcnow()
                job.last_run_at = datetime.utcnow()
                db.session.commit()
                
                LogHelper.create(
                    Log,
                    level=LogLevel.INFO,
                    message=f"Job {job_id} completed: {job.completed_count} sent, {job.failed_count} failed, {job.skipped_count} skipped",
                    context=f"Job ID: {job_id}"
                )
                
            except Exception as e:
                logger.error(f"Job {job_id} failed: {e}")
                job.status = ConnectionJobStatus.FAILED
                job.error_message = str(e)
                db.session.commit()
                LogHelper.create(
                    Log,
                    level=LogLevel.ERROR,
                    message=f"Job {job_id} failed: {e}",
                    context=f"Job ID: {job_id}"
                )
            finally:
                await browser.stop_browser()


_connection_service_instance: Optional[ConnectionService] = None


def get_connection_service(app) -> ConnectionService:
    global _connection_service_instance
    if not _connection_service_instance:
        _connection_service_instance = ConnectionService(app)
    return _connection_service_instance

