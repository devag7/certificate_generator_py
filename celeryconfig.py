"""
Celery Configuration for Certificate Generation System
====================================================

Author: devag7 (Deva Garwalla)
Description: Advanced Celery configuration with production-ready settings
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =============================================================================
# BROKER SETTINGS
# =============================================================================
broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Connection settings
broker_connection_retry_on_startup = True
broker_connection_retry = True
broker_connection_max_retries = 10

# =============================================================================
# TASK SETTINGS
# =============================================================================
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'UTC'
enable_utc = True

# Task execution settings
task_track_started = True
task_time_limit = 300  # 5 minutes
task_soft_time_limit = 240  # 4 minutes
task_acks_late = True
worker_prefetch_multiplier = 1

# Task result settings
result_expires = 3600  # 1 hour
result_persistent = True

# =============================================================================
# WORKER SETTINGS
# =============================================================================
worker_concurrency = 4
worker_max_tasks_per_child = 1000
worker_disable_rate_limits = False

# =============================================================================
# MONITORING SETTINGS
# =============================================================================
worker_send_task_events = True
task_send_sent_event = True

# =============================================================================
# LOGGING SETTINGS
# =============================================================================
worker_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
worker_task_log_format = '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'

# =============================================================================
# SECURITY SETTINGS
# =============================================================================
# Enable security features
worker_hijack_root_logger = False
worker_log_color = True

# =============================================================================
# ROUTES AND QUEUES
# =============================================================================
task_routes = {
    'tasks.generate_certificate': {'queue': 'certificates'},
    'tasks.cleanup_old_certificates': {'queue': 'maintenance'},
    'tasks.health_check': {'queue': 'monitoring'},
}

# =============================================================================
# BEAT SCHEDULE (for periodic tasks)
# =============================================================================
beat_schedule = {
    'cleanup-old-certificates': {
        'task': 'tasks.cleanup_old_certificates',
        'schedule': 24 * 60 * 60,  # Daily
        'args': (30,),  # 30 days old
    },
    'health-check': {
        'task': 'tasks.health_check',
        'schedule': 60 * 60,  # Hourly
    },
}

# =============================================================================
# DEVELOPMENT SETTINGS
# =============================================================================
if os.getenv('DEV_MODE', 'false').lower() == 'true':
    # More verbose logging for development
    worker_loglevel = 'DEBUG'
    task_eager_propagates = True
    task_always_eager = False
else:
    # Production settings
    worker_loglevel = 'INFO'
    task_eager_propagates = False
    task_always_eager = False