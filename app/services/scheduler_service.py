"""Scheduler service for automated tasks."""

import asyncio
import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import Optional, Callable, Dict, Any
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.ip_range_service import IPRangeService
from app.utils.logging import log_error


class SchedulerService:
    """Service for scheduling automated tasks."""
    
    def __init__(self):
        self.db_session: Optional[Session] = None
        self.scheduler_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.tasks: Dict[str, Dict[str, Any]] = {}
    
    def start_scheduler(self):
        """Start the scheduler service."""
        if self.is_running:
            print("⚠️  Scheduler is already running")
            return
        
        self.is_running = True
        
        # Schedule GitHub IP range updates daily at 05:00
        schedule.every().day.at("05:00").do(self._run_ip_update_task)
        
        # Schedule daily ChatGPT IP update from crawlers-info.de at 06:00 daily
        schedule.every().day.at("06:00").do(self._run_chatgpt_ip_update_task)
        
        # Schedule cleanup tasks daily
        schedule.every().day.at("02:00").do(self._run_cleanup_task)
        
        # Start scheduler in background thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        print("🕐 Scheduler started")
    
    def stop_scheduler(self):
        """Stop the scheduler service."""
        self.is_running = False
        schedule.clear()
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        print("🛑 Scheduler stopped")
    
    def schedule_ip_update_now(self):
        """Manually trigger IP update task."""
        self._run_ip_update_task()
    
    def schedule_cleanup_now(self):
        """Manually trigger cleanup task."""
        self._run_cleanup_task()
    
    def schedule_chatgpt_ip_update_now(self):
        """Manually trigger ChatGPT IP update task."""
        self._run_chatgpt_ip_update_task()
    
    def register_task(self, name: str, func: Callable, interval_hours: int = 24, immediate: bool = False):
        """Register a custom task with the scheduler."""
        schedule_func = func
        if immediate:
            schedule_func()
        
        schedule.every(interval_hours).hours.do(schedule_func)
        
        self.tasks[name] = {
            'func': func,
            'interval_hours': interval_hours,
            'last_run': datetime.now() if immediate else None,
            'status': 'active'
        }
        
        print(f"📋 Task '{name}' registered with {interval_hours}h interval")
    
    def _run_scheduler(self):
        """Main scheduler loop."""
        print("🕒 Scheduler thread started")
        
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                error_msg = f"Scheduler error: {str(e)}"
                print(f"❌ {error_msg}")
                log_error(
                    error_message=error_msg,
                    error_details=str(e),
                    site_id=None
                )
        
        print("🕒 Scheduler thread stopped")
    
    def _run_ip_update_task(self):
        """Run IP update task."""
        print("🔄 Starting scheduled IP update...")
        
        async def main():
            db = SessionLocal()
            try:
                ip_service = IPRangeService(db)
                result = await ip_service.update_all_ai_bot_ips()
                
                success_count = result['successful_updates']
                total_count = result['total_sources']
                
                print(f"✅ Scheduled IP update completed: {success_count}/{total_count} sources updated")
                
                # Log successful updates
                for source_name, source_result in result['sources'].items():
                    if source_result.get('success'):
                        ip_count = source_result.get('total_ips', 0)
                        new_count = source_result.get('new_ips_count', 0)
                        print(f"  📡 {source_name}: {ip_count} IPs ({new_count} new)")
                
                # Update task tracking
                self._update_task_status('ip_update', success=success_count > 0)
                
            except Exception as e:
                error_msg = f"Scheduled IP update failed: {str(e)}"
                print(f"❌ {error_msg}")
                log_error(
                    error_message=error_msg,
                    error_details=str(e),
                    site_id=None
                )
                self._update_task_status('ip_update', success=False, error=error_msg)
            finally:
                db.close()
        
        # Run async function
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(main())
            loop.close()
        except Exception as e:
            print(f"❌ Error running IP update task: {str(e)}")
    
    def _run_chatgpt_ip_update_task(self):
        """Run ChatGPT IP update task from crawlers-info.de."""
        print("🤖 Starting scheduled ChatGPT IP update from crawlers-info.de...")
        
        try:
            db = SessionLocal()
            ip_service = IPRangeService(db)
            
            result = ip_service.update_chatgpt_ips_from_crawlers_info()
            
            if result['status'] == 'success':
                ip_count = result['total_ips']
                changes = result['ips_added']
                print(f"✅ ChatGPT IP update completed: {ip_count} total IPs ({changes} new)")
                
                # Update task tracking
                self._update_task_status('chatgpt_ip_update', success=True)
            else:
                error_msg = f"ChatGPT IP update failed: {result.get('error', 'Unknown error')}"
                print(f"❌ {error_msg}")
                log_error(
                    error_message=error_msg,
                    error_details=result.get('error', 'Unknown error'),
                    site_id=None
                )
                self._update_task_status('chatgpt_ip_update', success=False, error=error_msg)
            
            db.close()
            
        except Exception as e:
            error_msg = f"Scheduled ChatGPT IP update failed: {str(e)}"
            print(f"❌ {error_msg}")
            log_error(
                error_message=error_msg,
                error_details=str(e),
                site_id=None
            )
            self._update_task_status('chatgpt_ip_update', success=False, error=error_msg)
    
    def _run_cleanup_task(self):
        """Run cleanup tasks."""
        print("🧹 Starting scheduled cleanup...")
        
        try:
            db = SessionLocal()
            ip_service = IPRangeService(db)
            
            # Clean up old logs (30 days)
            deleted_logs = ip_service.cleanup_old_logs(days=30)
            
            print(f"🧹 Cleanup completed: {deleted_logs} old logs deleted")
            
            self._update_task_status('cleanup', success=True)
            
            db.close()
            
        except Exception as e:
            error_msg = f"Scheduled cleanup failed: {str(e)}"
            print(f"❌ {error_msg}")
            log_error(
                error_message=error_msg,
                error_details=str(e),
                site_id=None
            )
            self._update_task_status('cleanup', success=False, error=error_msg)
    
    def _update_task_status(self, task_name: str, success: bool, error: str = None):
        """Update task execution status."""
        if task_name in self.tasks:
            self.tasks[task_name]['last_run'] = datetime.now()
            self.tasks[task_name]['status'] = 'success' if success else 'error'
            if error:
                self.tasks[task_name]['last_error'] = error
        else:
            # Create entry for system tasks
            self.tasks[task_name] = {
                'last_run': datetime.now(),
                'status': 'success' if success else 'error',
                'last_error': error if error else None
            }
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get current scheduler status."""
        next_run_times = []
        for job in schedule.jobs:
            next_run_times.append({
                'job': job.job_func.__name__ if hasattr(job.job_func, '__name__') else str(job.job_func),
                'next_run': job.next_run.isoformat() if job.next_run else None
            })
        
        return {
            'is_running': self.is_running,
            'registered_tasks': len(self.tasks),
            'scheduled_jobs': len(schedule.jobs),
            'tasks_status': self.tasks,
            'next_run_times': next_run_times
        }


# Global scheduler instance
scheduler_service = SchedulerService()
